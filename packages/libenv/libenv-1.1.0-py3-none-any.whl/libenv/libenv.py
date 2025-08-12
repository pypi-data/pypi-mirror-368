from typing import Optional, Any, Set
import asyncio
from pathlib import Path
from typing_extensions import Annotated
import sys
import logging
_logger = logging.getLogger(__name__)

import typer
from aurl import arun
from aurl.subst import subst

from .config import load_config, Config
from .envtype import EnvError, MissingEnvError, load_envfile
from .types.var import Var
from .artifacts import get_artifacts
from .lmod import Lmod, LmodError, quote
from .console import console, run_command, load_module

def setup_logging(v, vv):
    if vv:
        logging.basicConfig(level=logging.DEBUG)
    elif v:
        logging.basicConfig(level=logging.INFO)

#app = typer.Typer(pretty_exceptions_enable=False)
app = typer.Typer()

DoStep = Annotated[bool, typer.Option("-s", help="Do a single install step")]
NSteps = Annotated[Optional[int], typer.Option(..., help="Number of steps to load")]
V1 = Annotated[bool, typer.Option("-v", help="show info-level logs")]
V2 = Annotated[bool, typer.Option("-vv", help="show debug-level logs")]
CfgArg = Annotated[Optional[Path], typer.Option("--config",
                   envvar="LIBENV_CONFIG",
                   help="Config file path [default ~/.config/libenv.json].")]
SpecFile = Annotated[Path, typer.Argument(..., help="Environment spec file.")]

def prelude(config: Config, prefix: Path) -> Lmod:
    scr = Var(vars = {"prefix": str(prefix),
                      "MAKEFLAGS": f"-j{config.concurrency}"
                     },
              prepend = {"PATH": f"{prefix}/bin",
                         "LD_LIBRARY_PATH": f"{prefix}/lib",
                         "DYLD_LIBRARY_PATH": f"{prefix}/lib",
                         "MANPATH": f"{prefix}/share/man",
                         "CMAKE_PREFIX_PATH": str(prefix),
                         "PKG_CONFIG_PATH": f"{prefix}/lib/pkgconfig",
                        }
             ).loadScript(config)
    return scr

def load_script(config: Config,
                fname: Path,
                nsteps: Optional[int] = None) -> Lmod:
    env = load_envfile(config, fname)

    if nsteps is not None:
        assert nsteps <= len(env.specs), "nsteps exceeds actual steps"
        env.specs = env.specs[:nsteps]
    else:
        nsteps = len(env.specs)

    try:
        ndone = env.check_installed()
        if ndone != nsteps:
            return LmodError(f"Incomplete install: only {ndone} of {nsteps} steps complete.")
    except EnvError as e:
        return LmodError(f"Invalid install: {e}")
    scr = prelude(config, env.prefix)
    for spec in env.specs:
        scr.extend( spec.loadScript(config) )
    return scr

async def run_install(config: Config, fname: Path, step: bool = False,
                      args: str = "") -> int:
    env = load_envfile(config, fname)

    try:
        ndone = env.check_installed()
    except MissingEnvError:
        ndone = 0
        env.mark_complete(0)

    if ndone == len(env.specs):
        console.print("Install already complete!")
        return 0

    if step:
        spec = env.specs[ndone]
        moddir = config.data_dir/"modulefiles"
        moddir.mkdir(parents=True, exist_ok=True)
        modfile = moddir / f"{fname.stem}.lua"
        #load_script(config, fname, ndone).write(modfile)

        steptype = spec.__class__.__name__
        stepname = f"{ndone+1:02d}-{steptype.lower()}"
        console.rule(f"[bold green]Step {ndone+1} ({steptype})")

        # TODO: load/save os.environ (not strictly needed, since we're in a sub-process)
        with config.workdir(fname.name):
            await get_artifacts(config.cache_dir/"mirror", spec.artifacts, True)
            if ndone > 0:
                await load_module(modfile) # modifies env!
            ret = await spec.install(config)
            if ret != 0:
                print(f"Error running {stepname} in {Path().resolve()}")
                return ret
        env.mark_complete(ndone+1)
        # write out the updated module file
        load_script(config, fname, ndone+1).write(modfile)
    else:
        assert args != "", "args are required when step == False"
        # download all artifacts at once
        with config.workdir(fname.name):
            art: Set[str] = set()
            for spec in env.specs:
                art |= set(spec.artifacts)
            await get_artifacts(config.cache_dir/"mirror", art)

        for i in range(ndone, len(env.specs)):
            cmd = [sys.executable, "-c", f"from libenv import libenv; from pathlib import Path,PosixPath,WindowsPath; exit(libenv.install({args}));"]
            ret = await run_command(cmd)
            if ret != 0:
                console.rule(f"[red]Error Installing Step {i+1}")
                print(f"from: libenv install -s {fname}")
                return ret

    return 0

@app.command()
def load(specfile: SpecFile,
         nsteps: NSteps = None,
         v: V1 = False,
         vv: V2 = False,
         cfg: CfgArg = None):
    """
    Load a specfile (assuming components are installed).
    """
    setup_logging(v, vv)
    config = load_config(cfg)
    scr = load_script(config, specfile, nsteps)
    print(scr)

@app.command()
def install(specfile: SpecFile,
            step: DoStep = False,
            v: V1 = False,
            vv: V2 = False,
            cfg: CfgArg = None):
    """
    Install a specfile.
    """
    setup_logging(v, vv)
    config = load_config(cfg)

    # args needed to call this function recursively when doing a single step.
    args = f'specfile={specfile!r}, step=True, v={v}, vv={vv}, cfg={cfg!r}'
    #arun( run_install(config, specfile, step, args=args) )
    err = asyncio.run( run_install(config, specfile, step, args=args) )
    #raise typer.Exit(code=err)
    exit(err)

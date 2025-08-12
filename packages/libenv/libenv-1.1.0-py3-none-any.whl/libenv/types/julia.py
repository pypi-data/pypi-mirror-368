from typing import Dict, List
import os
from pathlib import Path

from ..artifacts import get_artifacts
from ..envtype import EnvType
from ..lmod import Lmod, SetEnv, Prepend, quote
from ..config import Config
from ..console import run_command, set_env, expand

class Julia(EnvType):
    specs: List[str] = []
    registries: List[str] = []
    env: Dict[str,str] = {}

    def _depotdir(self):
        return expand("$prefix/julia/depot")
    def _projdir(self):
        return expand("$prefix/julia/project")

    async def install(self, config: Config) -> int:
        with set_env(**{k: expand(v) for k,v in self.env.items()}):
            # Don't need an env var here, since we use --project
            #loadpath = os.environ.get("JULIA_LOAD_PATH","")
            #if len(loadpath) == 0:
            #    loadpath = self._projdir()
            #else:
            #    loadpath = f"{self._projdir()}:{loadpath}"
            #os.environ["JULIA_LOAD_PATH"] = loadpath
            os.environ["JULIAUP_DEPOT_PATH"] = self._depotdir()
            os.environ["JULIA_DEPOT_PATH"] = self._depotdir()
            os.environ["JULIA_PROJECT"] = self._projdir()

            julia = Path(os.environ["prefix"])/"julia"
            if julia.exists():
                assert julia.is_dir(), "$prefix/julia is not a dir."
            else:
                ans = await get_artifacts(config.cache_dir/"mirror",
                        ["https://install.julialang.org"],
                        False)
                assert len(ans) == 1, "Unable to fetch file."
                for k, v in ans.items():
                    pass
                cmd = ["/bin/sh", str(v), '--add-to-path=no', '--yes',
                        f'--path={julia}',
                        '--background-selfupdate', '0',
                        '--startup-selfupdate', '0'
                       ]
                ret = await run_command(cmd)
                if ret != 0:
                    return ret

            script = ["using Pkg"]
            for registry in self.registries:
                if registry.startswith("RegistrySpec"):
                    script.append(f"Pkg.Registry.add({registry})")
                else:
                    script.append(f"Pkg.Registry.add({quote(registry)})")

            for spec in self.specs:
                script.append(f"Pkg.add({quote(spec)})")

            cmd = [str(julia/"bin"/"julia"),
                   f"--project={self._projdir()}",
                   "-e", "; ".join(script)]
            if len(script) > 1:
                ret = await run_command(cmd)
                if ret != 0:
                    return ret

        return 0

    def loadScript(self, config: Config) -> Lmod:
        return Lmod([
                SetEnv("JULIAUP_DEPOT_PATH", self._depotdir()),
                SetEnv("JULIA_DEPOT_PATH", self._depotdir()),
                Prepend("JULIA_LOAD_PATH", self._projdir()),
                Prepend("PATH", expand("$prefix/julia/bin")),
            ])

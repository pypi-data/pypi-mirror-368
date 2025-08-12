from typing import List
from pathlib import Path
from string import Template
import os
import asyncio
from contextlib import contextmanager

from rich.console import Console
from rich.text import Text

console = Console(soft_wrap=True)

async def run_command(command: List[str], shell=False) -> int:
    if shell:
        console.print(Text("\n".join(command),
                           overflow="ellipsis",
                           no_wrap=True))
    else:
        console.print("running: " + " ".join(map(repr,command)))

    try:
        if shell:
            process = await asyncio.create_subprocess_shell("\n".join(command))
        else:
            process = await asyncio.create_subprocess_exec(*command)
        #stdout, stderr = await process.communicate()
        ret = await process.wait()
    except FileNotFoundError:
        print(f"File not found: {command[0]} in {Path().resolve()}")
        return 7
    return ret

async def read_command(command: List[str]) -> str:
    """ Run a command and return its stdout.
    """
    process = await asyncio.create_subprocess_exec(
        *command,
        stdout=asyncio.subprocess.PIPE,
        #stderr=asyncio.subprocess.PIPE
    )
    
    stdout, stderr = await process.communicate()
    ret = await process.wait()
    if ret != 0:
        raise RuntimeError(f"Process {command!r} returned {ret}")
    return stdout.decode('utf-8')

async def load_module(modpath: Path) -> None:
    moddir = str(modpath.parent)
    assert modpath.suffix == ".lua"

    lmod = os.environ.get("LMOD_CMD", "")
    if lmod == "":
        raise KeyError("LMOD_CMD must be defined!")

    # Temporarily prepend MODULEPATH
    mpath = os.environ.get("MODULEPATH", "")
    if mpath == "":
        os.environ["MODULEPATH"] = moddir
    else:
        os.environ["MODULEPATH"] = moddir + ":" + mpath
    try:
        cmds = await read_command([lmod, "python", "load", modpath.stem])
        #print(cmds)
        # Sadly, exec is the price we pay for asking lmod to set env vars within python.
        exec(cmds, {"os": os}, {})
    finally: # env vars might have been concurrently modified...
        mpath = os.environ.get("MODULEPATH", "")
        if mpath == moddir:
            del os.environ["MODULEPATH"]
        else:
            os.environ["MODULEPATH"] = mpath.replace(moddir+":", "", 1)
    return None

@contextmanager
def set_env(**environ):
    old_environ = dict(os.environ)
    os.environ.update(environ)
    try:
        yield
    finally:
        os.environ.clear()
        os.environ.update(old_environ)

@contextmanager
def set_dir(working_dir: Path):
    original = os.getcwd()
    try:
        os.chdir(working_dir)
        yield
    finally:
        os.chdir(original)

def expand(expr):
    try:
        ans = Template(expr).substitute(os.environ)
    except KeyError as e:
        raise KeyError(f"Undefined variable {e} in {expr!r}")
    return ans

from typing import List, Set, Optional, Union, Dict
import asyncio
from pathlib import Path

from aurl import Mirror, URL
from .console import run_command, console

def unpack_artifact_cmd(fname: str) -> List[str]:
    if fname.endswith(".tgz") or fname.endswith(".tar.gz"):
        return ["tar", "xzf", fname]
    if fname.endswith(".tbz") or fname.endswith(".tar.bz2"):
        return ["tar", "xjf", fname]
    if fname.endswith(".txz") or fname.endswith(".tar.xz") \
            or fname.endswith(".tar"):
        return ["tar", "xf", fname]
    if fname.endswith(".zip"):
        return ["unzip", "-u", fname]
    return ["cp", "-r", fname, "."]

async def unpack_artifact(fname: str) -> None:
    cmd = unpack_artifact_cmd(fname)
    await run_command(cmd)

async def get_artifacts(cache: Path,
                        artifacts: Union[List[str],Set[str]],
                        unpack=False) -> Dict[URL, Path]:
    """ Download all artifacts into a cache directory,
    and then extract / copy them into the current working directory.
    """
    if len(artifacts) == 0:
        return {}

    cache.mkdir(exist_ok=True)
    M = Mirror(cache)
    with console.status("Downloading artifacts"):
        outputs = await M.fetch_all(map(URL, artifacts))

    if unpack:
        with console.status("Unpacking artifacts"):
            for fname in outputs.values():
                await unpack_artifact(str(fname))
    return outputs

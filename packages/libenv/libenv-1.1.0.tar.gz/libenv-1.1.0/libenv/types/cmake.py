from typing import Dict, Optional, Tuple
from pathlib import Path
import os

from ..envtype import EnvType
from ..config import Config
from ..lmod import Lmod
from ..console import set_env, set_dir, run_command, expand

class Cmake(EnvType):
    source: str # name of directory containing source
    cmake: Dict[str, str] = {} # "C_COMPILER: gcc" ~> "-D C_COMPILER=gcc"
    env: Dict[str, str] = {}
    pre_configure: Optional[str] = None
    post_configure: Optional[str] = None
    post_install: Optional[str] = None

    async def install(self, config: Config) -> int:
        cmake_opts = [f"-D{k}={expand(v)}" for k,v in self.cmake.items()]
        with set_env(**{k: expand(v) for k,v in self.env.items()}):
            build = "_build"
            await run_command(["rm", "-fr", build])
            if self.pre_configure:
                with set_dir(Path(self.source)):
                    ret = await run_command([self.pre_configure], shell=True)
                if ret != 0:
                    return ret

            ret = await run_command(["cmake", "-B", build, "-S", self.source,
                                     "-DCMAKE_INSTALL_PREFIX="+os.environ["prefix"],
                                    ] + cmake_opts)
            if ret != 0:
                return ret
            if self.post_configure:
                with set_dir(Path(build)):
                    ret = await run_command([self.post_configure], shell=True)
                if ret != 0:
                    return ret
            ret = await run_command(["make", f"-j{config.concurrency}", "-C", build, "install"])
            if ret != 0:
                return ret

            if self.post_install:
                with set_dir(Path(build)):
                    ret = await run_command([self.post_install], shell=True)
                if ret != 0:
                    return ret
            await run_command(["rm", "-fr", self.source, build])
        return 0

    def loadScript(self, config: Config) -> Lmod:
        return Lmod()

from typing import Dict, Optional, List
from pathlib import Path
import shlex
import os

from ..envtype import EnvType
from ..config import Config
from ..lmod import Lmod
from ..console import set_env, set_dir, run_command, expand

class Autotools(EnvType):
    source: str # name of directory containing source
    env: Dict[str, str] = {}
    configure: List[str] = []
    pre_configure: Optional[str] = None
    post_configure: Optional[str] = None
    post_install: Optional[str] = None

    async def install(self, config: Config) -> int:
        with set_env(**{k: expand(v) for k,v in self.env.items()}):
            with set_dir(Path(self.source)):
                if self.pre_configure:
                    ret = await run_command([self.pre_configure], shell=True)
                    if ret != 0:
                        return ret

                ret = await run_command(["./configure", f"--prefix={os.environ['prefix']}"]
                                                + list(map(expand, self.configure)))
                if ret != 0:
                    return ret
                if self.post_configure:
                    ret = await run_command([self.post_configure], shell=True)
                    if ret != 0:
                        return ret
                ret = await run_command(["make", f"-j{config.concurrency}", "install"])
                if ret != 0:
                    return ret

                if self.post_install:
                    ret = await run_command([self.post_install], shell=True)
                    if ret != 0:
                        return ret
            await run_command(["rm", "-fr", self.source])
        return 0

    def loadScript(self, config: Config) -> Lmod:
        return Lmod()

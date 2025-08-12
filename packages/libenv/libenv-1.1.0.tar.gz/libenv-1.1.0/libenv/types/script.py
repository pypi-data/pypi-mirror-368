from typing import List

from ..envtype import EnvType
from ..lmod import Lmod
from ..console import run_command, expand
from ..config import Config

class Script(EnvType):
    script: str
    load: List[str] = []

    async def install(self, config: Config) -> int:
        return await run_command([self.script], shell=True)
    def loadScript(self, config: Config) -> Lmod:
        #return Lmod.parse(list(map(expand, self.load)))
        return Lmod.parse(self.load)

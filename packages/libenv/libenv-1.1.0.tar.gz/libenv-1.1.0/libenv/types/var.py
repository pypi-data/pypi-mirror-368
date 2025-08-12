from typing import Dict

from ..envtype import EnvType
from ..lmod import Lmod, SetEnv, Append, Prepend
from ..config import Config

class Var(EnvType):
    vars:    Dict[str, str] = {}
    append:  Dict[str, str] = {}
    prepend: Dict[str, str] = {}

    async def install(self, config: Config) -> int:
        return 0
        # TODO: run lmod with this script to check for errors?

    def loadScript(self, config: Config) -> Lmod:
        return Lmod(  [SetEnv(k,v) for k,v in self.vars.items()]
                    + [Append(k,v) for k,v in self.append.items()]
                    + [Prepend(k,v) for k,v in self.prepend.items()]
                   )

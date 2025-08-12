from ..envtype import EnvType
from ..lmod import Lmod, Load, Unload
from ..config import Config

class Module(EnvType):
    specs: list[str]
    unload: list[str] = []

    async def install(self, config: Config) -> int:
        return 0
    def loadScript(self, config: Config) -> Lmod:
        return Lmod( [Unload(s) for s in self.unload] \
                    +[Load(s) for s in self.specs]
                   )

from typing import Dict
import os

from ..envtype import EnvType
from ..lmod import Lmod, SetEnv
from ..config import Config
from ..console import run_command, set_env, expand

class Venv(EnvType):
    python: str = "python3"
    system_site_packages: bool = False
    opts: list[str] = []
    specs: list[str] = []
    env: Dict[str,str] = {}

    async def install(self, config: Config) -> int:
        with set_env(**{k: expand(v) for k,v in self.env.items()}):
            vopts = []
            if self.system_site_packages:
                vopts.append("--system-site-packages")

            cmd = [ self.python, "-m", "venv" ] #"--upgrade-deps"
            cmd.extend(vopts)
            cmd.append(os.environ['prefix'])
            ret = await run_command(cmd)
            if ret != 0:
                return ret

            os.environ["VIRTUAL_ENV"] = os.environ['prefix']
            cmd = ["pip", "--cache-dir", str(config.cache_dir/"pip"),
                           "--no-input",
                           "--require-virtualenv",
                           "install"]
            cmd.extend(self.opts)

            for spec in self.specs:
                ret = await run_command(cmd + [spec])
                if ret != 0:
                    return ret
        return 0

    def loadScript(self, config: Config) -> Lmod:
        return Lmod([SetEnv("VIRTUAL_ENV", "$prefix")])

from typing import List, Dict, Any, Optional
from pathlib import Path
import json
import os

from ..envtype import EnvType
from ..lmod import Lmod
from ..config import Config
from ..console import run_command, set_env

#spack bootstrap now
#spack compiler find

#  specs: []
#  view: true
#  concretizer:
#    unify: true

class Spack(EnvType):
    #artifacts: [ "https://github.com/my_patch" ]
    #pre_configure: "git checkout deadbeef; patch -p1 <my_patch"
    pre_configure: Optional[str] = None
    spack: Dict[str,Any]
    spack_url: str = "https://github.com/spack/spack.git"

    async def install(self, config: Config) -> int:
        spack_root = Path(os.environ["prefix"])/"share"/"spack"
        #stutter = lambda x: f"{spack_root}/{x}/spack"
        spack = str(spack_root/"bin"/"spack")

        with set_env(SPACK_ROOT = str(spack_root),
                     SPACK_USER_CACHE_PATH  = str(spack_root/".cache"),
                     SPACK_USER_CONFIG_PATH = str(spack_root/".spack")):
            if not spack_root.is_dir():
                ret = await run_command(["git", "clone", "--depth", "1", self.spack_url, str(spack_root)])
                if ret != 0:
                    return ret
            if self.pre_configure is not None:
                ret = await run_command([self.pre_configure], shell=True)
                if ret != 0:
                    return ret
            ret = await run_command([spack, "bootstrap", "now"])
            if ret != 0: return ret

            # make an editable copy of spack config
            cfg = dict(self.spack)
            cfg['config'] = dict(cfg.get('config', {}))
            cfg['config']['install_tree'] = {'root': os.path.join(os.environ["prefix"],"opt")}
            #cfg['config']['view'] = os.environ['prefix'] # had no effect when enabled!
            specfile = json.dumps({"spack":cfg}, indent=2)
            
            (spack_root/"spackenv.yaml").write_text(specfile)
            ret = await run_command([spack, "env", "rm", "-f", "spackenv"])
            if ret != 0: return ret
            ret = await run_command([spack, "env", "create", "spackenv",
                                                    str(spack_root/"spackenv.yaml")])
            if ret != 0: return ret
            # f"{spack} env activate spackenv"
            ret = await run_command([spack, "-e", "spackenv", "install"])
            if ret != 0: return ret

            # spack refuses to install a view into $prefix
            # so we put it into prefix/local
            # TODO: make this prefix/spack1, spack2, ...
            ret = await run_command([spack, "-e", "spackenv", "env", "view", "enable",
                                     os.path.join(os.environ["prefix"],"local")])
            if ret != 0: return ret
            # (create / enable view of this env.)
            # spack view -d true copy -i $prefix single-pkg@1.2
            # (single package)
            await run_command([spack, "clean", "-dms"])
        return 0

    def loadScript(self, config: Config) -> Lmod:
        return Lmod()

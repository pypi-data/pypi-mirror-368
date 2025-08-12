""" Recursively download and interpret (as inlined)
    environment specs from URL-s.

    We assume that all dependencies can be installed
    in parallel.  Each install gets run in a shell with
    the "load" step from all previous steps.

    After installing, the "load" steps from this block
    done in serial.

    TODO: use as_completed to run in parallel.

    This involves clever naming that will reveal common
    package dependencies (e.g. one subdir per dependency).
"""
from typing import Any, List
from pathlib import Path
from tempfile import NamedTemporaryFile

import yaml

#from aurl import URL
from aurl import arun
from aurl.fetch import download_url

from ..config import Config
from ..envtype import EnvType, load_envfile
from ..lmod import Lmod

# TODO: force URL to refer to a git repo in the form,
# git+https://gitlab.com/frobnitzem/libenv.git
#
# then construct the download from
# git+https://gitlab.com/frobnitzem/libenv.git@<tag>:env.yaml
#
# i.e. repo = https://gitlab.com/frobnitzem/libenv.git
#      rev-parse = <tag>:env.yaml
async def fetch_env(config: Config, url: str) -> Any:
    with NamedTemporaryFile(mode="r", encoding="utf-8") as f:
        await download_url(f.name, url)
        return load_envfile(config, Path(f.name))

class Depends(EnvType):
    urls: List[str]

    async def install(self, config: Config) -> int:
        raise NotImplementedError("needs a parallel loop through specs...")
        #for url in self.urls:
        #    spec = await fetch_env(config, url)
        #    ret = await spec.install(config)
        #    if ret != 0:
        #        return ret
        return 0
    def loadScript(self, config: Config) -> Lmod:
        script = Lmod()
        for url in self.urls:
            specs = arun(fetch_env(config, url))
            for spec in specs:
                script.extend( spec.loadScript(config) )
        return script

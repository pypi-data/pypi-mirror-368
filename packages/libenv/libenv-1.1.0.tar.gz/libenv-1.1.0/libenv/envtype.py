from typing import List, Optional, Any, Dict
from pathlib import Path
from abc import ABC, abstractmethod
import json

from pydantic import BaseModel

from .config import Config
from .spec import Spec, load_specs, read_data
from .lmod import Lmod

class EnvError(Exception):
    pass

class MissingEnvError(EnvError):
    pass

class EnvType(BaseModel, ABC, extra='forbid'):
    artifacts: List[str] = []

    @abstractmethod
    def loadScript(self, config: Config) -> Lmod:
        return Lmod()

    @abstractmethod
    async def install(self, config: Config) -> int:
        return 0

    def model_dump(self, **kws) -> Dict[str,Any]:
        proper_caps = lambda x: x[0].upper() + x[1:].lower()
        ans = {"type": proper_caps(self.__class__.__name__)}
        ans.update(super().model_dump(exclude_defaults=True, **kws))
        return ans

class EnvFile(BaseModel):
    prefix: Path
    specs: List[EnvType]

    def check_installed(self) -> int:
        """ Check that the prefix/env.json file documents a partial
        install of this EnvFile object.

        Raises MissingEnvError if prefix/env.json is missing.
        
        Raises an EnvError if the env.json is missing or lists
        different install steps.

        Otherwise, returns the number of steps that prefix/env.json
        documents (i.e. completed steps).
        """
        if not self.prefix.is_dir():
            raise MissingEnvError(f"prefix {self.prefix} not initialized")
        try:
            info = load_envfile(None, self.prefix/"env.json")
        except FileNotFoundError:
            raise MissingEnvError(f"No env.json in {self.prefix}")
        if info.prefix != self.prefix:
            raise EnvError("Invalid prefix.")
        
        if len(info.specs) > len(self.specs):
            raise EnvError(f"{len(info.specs)} specs installed, but expected {len(self.specs)}")
        for i, (expected, actual) in enumerate(zip(self.specs, info.specs)):
            if expected != actual:
                raise EnvError(f"Specs differ at step {i+1}: expected {expected.model_dump_json()} but found {actual.model_dump_json()}")

        return len(info.specs)

    def mark_complete(self, n: int) -> None:
        """ Mark "n" install steps as completed.
        """
        if n == 0:
            self.prefix.mkdir(parents=True, exist_ok=True)
        assert n <= len(self.specs)

        #sub_env = EnvFile(prefix=self.prefix, specs=self.specs[:n])
        (self.prefix/"env.json").write_text(
            json.dumps({"prefix":str(self.prefix),
                        "environment":[s.model_dump() for s in self.specs[:n]]
                       }, indent=2)
        )

def load_envfile(config: Optional[Config], fname: Path) -> EnvFile:
    data = read_data(fname)
    specs = load_specs(data["environment"])
    
    if config is None or "prefix" in data:
        prefix = Path(data["prefix"])
    else:
        prefix = config.data_dir / fname.name.rsplit(".", 1)[0]

    return EnvFile(prefix=prefix, specs=specs)

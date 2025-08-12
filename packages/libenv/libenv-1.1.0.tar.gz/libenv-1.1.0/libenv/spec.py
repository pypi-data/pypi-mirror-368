from typing import Union, Any, List, Dict
import os
import importlib
from pathlib import Path
import json

import yaml
from pydantic import BaseModel, ConfigDict

class Spec(BaseModel):
    type: str

    model_config = ConfigDict(
        extra="allow",
    )

def read_data(path : Union[str, os.PathLike]) -> Any:
    path1 = Path(path)
    if path1.suffix == ".yaml" or path1.suffix == ".yml":
        with open(path1, encoding="utf-8") as f:
            attr = yaml.safe_load(f)
    else:
        with open(path1, encoding="utf-8") as f:
            attr = json.load(f)
    return attr

def load_spec(attr: Any) -> Any:
    """ Dynamically load a spec by creating an instance
        of the class named by "type".
    """
    stype = attr.pop("type")
    specname = stype.lower()
    stype = stype[:1].upper() + specname[1:] # first-letter-caps convention
    mod = importlib.import_module(f".types.{specname}", package="libenv")

    cls = getattr(mod, stype)
    return cls.model_validate( attr )

def load_specs(attr: List[Any]) -> List[Any]:
    return [load_spec(x) for x in attr]

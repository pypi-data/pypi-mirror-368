from typing import Union
import os
from pathlib import Path
from contextlib import contextmanager
import logging
_logger = logging.getLogger(__name__)

from pydantic import BaseModel

from .console import set_dir

class Config(BaseModel):
    data_dir    : Path
    concurrency : int
    build_dir   : Path = Path("/tmp/build")
    cache_dir   : Path = Path("/tmp/libenv.cache")

    @contextmanager
    def workdir(self, name: str):
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        working_dir = self.build_dir/name
        working_dir.mkdir(parents=True, exist_ok=True)
        _logger.info("Set up working directories for %s", working_dir)

        with set_dir(working_dir):
            yield
        _logger.info("Leaving working directory %s", working_dir)

def load_config(path: Union[str, os.PathLike, None]) -> Config:
    cfg_name = "libenv.json"
    if path is None:
        path1 = Path(os.environ["HOME"]) / '.config' / cfg_name
    else:
        path1 = Path(path)
    assert path1.exists(), f"{cfg_name} is required to exist (tried {path1})"
    config = Config.model_validate_json(
                        path1.read_text(encoding='utf-8'))
    # additional validation steps...
    return config


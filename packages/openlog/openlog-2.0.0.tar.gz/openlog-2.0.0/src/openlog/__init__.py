from importlib import resources

from .logger import Logger as Logger

try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib

_cfg = tomllib.loads(resources.read_text("openlog", "config.toml"))

__version__ = "2.0.0"

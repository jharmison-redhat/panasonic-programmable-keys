import os
from pathlib import Path

from dynaconf import Dynaconf

from .helpers import Truthy

skip_load = bool(Truthy(os.getenv("PANASONIC_KEYS_SKIP_LOAD_FILES", "false")))

default_config = Path(__file__).parent.joinpath("defaults.toml")
system_configs = [
    Path("/usr/share/panasonic/config.toml"),
    Path("/etc/panasonic/config.toml"),
]
user_config = Path(os.getenv("XDG_CONFIG_HOME", "~/.config")).expanduser().joinpath("panasonic", "config.toml")
running_config = Path.cwd().joinpath("config.toml")

if skip_load:
    settings = Dynaconf(
        envvar_prefix="PANASONIC_KEYS",
        core_loaders=["TOML"],
        settings_files=[default_config],
        load_dotenv=False,
    )
else:
    settings = Dynaconf(
        envvar_prefix="PANASONIC_KEYS",
        core_loaders=["TOML"],
        settings_files=[default_config],
        load_dotenv=True,
        includes=system_configs + [user_config, running_config],
    )

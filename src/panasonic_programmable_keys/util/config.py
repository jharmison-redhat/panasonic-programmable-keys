import os
from pathlib import Path

from dynaconf import Dynaconf

settings = Dynaconf(
    envvar_prefix="PANASONIC_KEYS",
    core_loaders=["TOML"],
    settings_files=[Path(__file__).parent.joinpath("defaults.toml")],
    load_dotenv=True,
    includes=[
        "/etc/panasonic/config.toml",
        # TODO: find a good way to prefer looking in /usr
        os.path.join(os.getenv("XDG_CONFIG_HOME", os.path.expanduser("~/.config")), "panasonic", "config.toml"),
        os.path.join(os.getcwd(), "config.toml"),
    ],
)

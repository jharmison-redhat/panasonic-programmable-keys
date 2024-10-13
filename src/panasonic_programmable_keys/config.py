import os
from dynaconf import Dynaconf

settings = Dynaconf(
    envvar_prefix="PANASONIC_KEYS",
    core_loaders=["TOML"],
    settings_files=['defaults.toml'],
    load_dotenv=True,
    includes=[
        "/etc/panasonic/config.toml",
        os.path.join(os.getenv("XDG_CONFIG_HOME", os.path.expanduser("~/.config")), "panasonic", "config.toml"),
        os.path.join(os.getcwd(), "config.toml"),
    ]
)


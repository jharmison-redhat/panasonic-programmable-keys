import os
from pathlib import Path

from dynaconf import Dynaconf
from watchdog.events import FileSystemEvent
from watchdog.events import FileSystemEventHandler
from watchdog.observers.inotify import InotifyObserver

from .helpers import Truthy
from .logging import logger

skip_load = bool(Truthy(os.getenv("PANASONIC_KEYS_SKIP_LOAD_FILES", "false")))

default_config = Path(__file__).parent.joinpath("defaults.toml")
system_configs = [
    Path("/usr/share/panasonic/config.toml"),
    Path("/etc/panasonic/config.toml"),
]
user_config = Path(os.getenv("XDG_CONFIG_HOME", "~/.config")).expanduser().joinpath("panasonic", "config.toml")
running_config = Path.cwd().joinpath("config.toml")
include_configs = system_configs + [user_config, running_config]

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
        includes=include_configs,
    )


class SettingsHotReloader:
    class SettingsEventHandler(FileSystemEventHandler):
        def on_any_event(self, event: FileSystemEvent) -> None:
            logger.debug(f"Reloading config due to {event}")
            settings.reload()

    def __init__(self) -> None:
        self.event_handler = self.SettingsEventHandler()
        self.observer = InotifyObserver()
        for config in include_configs:
            self.observer.schedule(self.event_handler, str(config))

    def __enter__(self) -> None:
        self.observer.start()

    def __exit__(self, *_) -> None:
        self.observer.stop()
        self.observer.join()

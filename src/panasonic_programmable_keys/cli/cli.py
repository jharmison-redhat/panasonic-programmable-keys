from pathlib import Path

import typer
from rich import print
from typing_extensions import Annotated

from ..input import InputDevices
from ..util import make_logger
from ..util import settings
from .base import Cli
from .base import VerboseOption
from .base import VersionOption
from .base import path_autocomplete
from .base import version_callback


class Config(Cli):
    help = "Operations on the configuration"

    def cmd_view(self, verbose: VerboseOption, _: VersionOption) -> None:
        """View the current configuration, as loaded"""
        make_logger(verbose)
        print(settings.as_dict())


class Input(Cli):
    help = "Operations on lower-level input devices"

    def cmd_validate(
        self,
        _: VersionOption,
        verbose: VerboseOption,
        proc_input_file: Annotated[
            Path,
            typer.Argument(
                autocompletion=path_autocomplete(file_okay=True, dir_okay=False),
                help="The path to a file with syntax similar to /proc/bus/input/devices",
            ),
        ] = Path("/proc/bus/input/devices"),
    ) -> None:
        """Load the input device list"""
        make_logger(verbose)
        print(InputDevices.load(proc_input_file).model_dump())


class Main(Cli):
    help = "Panasonic Programmable Keys Configuration Utility"
    subcommands = [Config(), Input()]

    def cmd_version(self) -> None:
        """Print the version and exit"""
        version_callback(True)


cli = Main()

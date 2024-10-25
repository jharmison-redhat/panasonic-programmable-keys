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
    help = "Configure and view configuration information."

    def cmd_view(self, verbose: VerboseOption, _: VersionOption) -> None:
        """View the current configuration, as loaded by default."""
        make_logger(verbose)
        print(settings.as_dict())


class Input(Cli):
    help = "Operations on lower-level input devices."

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
        check_paths: Annotated[
            bool | None,
            typer.Option(help="Whether to check paths that should exist (like those under /sys or /dev/input)"),
        ] = settings.input.get("check_paths", True),
    ) -> None:
        """Load and validate the input device list."""
        if check_paths is not None:
            settings.input["check_paths"] = check_paths
        make_logger(verbose)
        try:
            print(InputDevices.load(proc_input_file).model_dump())
        except AssertionError as e:
            if str(e).startswith("Path") and str(e).endswith("doesn't exist"):
                raise AssertionError(f"{e}: Did you mean to pass --no-check-paths on the CLI or change the settings?")
            raise e

    def cmd_read(
        self,
        _: VersionOption,
        verbose: VerboseOption,
    ) -> None:
        """Read the bytes coming off of the device as a raw struct (mostly for debugging)."""
        make_logger(verbose)
        from ..input import yield_from

        for line in yield_from():
            print(line)


class Main(Cli):
    help = "Panasonic Programmable Keys Configuration Utility"
    subcommands = [Config(), Input()]

    def cmd_version(self) -> None:
        """Print the version and exit."""
        version_callback(True)

    def cmd_gui(
        self,
        verbose: VerboseOption,
        proc_input_file: Annotated[
            Path,
            typer.Argument(
                autocompletion=path_autocomplete(file_okay=True, dir_okay=False),
                help="The path to a file with syntax similar to /proc/bus/input/devices",
            ),
        ] = Path("/proc/bus/input/devices"),
        check_paths: Annotated[
            bool | None,
            typer.Option(help="Whether to check paths that should exist (like those under /sys or /dev/input)"),
        ] = settings.input.get("check_paths", True),
    ) -> None:
        """Run the GUI application for configuring the functions of your programmable buttons."""
        make_logger(verbose)

        if check_paths is not None:
            settings.input["check_paths"] = check_paths

        from ..gui import gui

        gui(proc_input_file)


cli = Main()

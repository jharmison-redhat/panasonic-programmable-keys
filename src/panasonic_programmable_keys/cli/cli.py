import os
from pathlib import Path

import typer
from rich import print
from typing_extensions import Annotated

from ..input import InputDevices
from ..util import make_logger
from ..util import settings
from .base import CheckPathsOption
from .base import Cli
from .base import DevicesFileArgument
from .base import VerboseOption
from .base import VersionOption
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
        devices_file: DevicesFileArgument,
        check_paths: CheckPathsOption,
    ) -> None:
        """Load and validate the input device list."""
        if check_paths is not None:
            settings.input["check_paths"] = check_paths
        make_logger(verbose)
        try:
            print(InputDevices.load(devices_file).model_dump())
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


class Debug(Cli):
    help = "Debugging tools, not intended for external consumption"
    extra_app_settings = {"hidden": True}
    subcommands = [Input()]

    def cmd_server(self) -> None:
        """Debug the server interface."""
        make_logger(5)
        settings.rpc["socket"] = Path(os.environ.get("XDG_RUNTIME_DIR", "/run/user/1000")).joinpath("panasonic.sock")
        from ..rpc.server import get_server

        get_server().requestLoop()

    def cmd_client(self) -> None:
        """Debug the client interface."""
        make_logger(5)
        settings.rpc["socket"] = Path(os.environ.get("XDG_RUNTIME_DIR", "/run/user/1000")).joinpath("panasonic.sock")
        from ..rpc.client import KeyClient

        client = KeyClient()
        print(client.ping())

    def cmd_args(self) -> None:
        """Print sysv args for help with finding the path."""
        make_logger(5)
        import sys

        print(sys.argv)


class Main(Cli):
    help = "Panasonic Programmable Keys Configuration Utility"
    subcommands = [Config(), Debug()]

    def cmd_version(self) -> None:
        """Print the version and exit."""
        version_callback(True)

    def cmd_gui(
        self,
        verbose: VerboseOption,
        devices_file: DevicesFileArgument,
        check_paths: CheckPathsOption,
    ) -> None:
        """Run the GUI application for configuring the functions of your programmable buttons."""
        make_logger(verbose)

        if check_paths is not None:
            settings.input["check_paths"] = check_paths

        from ..gui import gui

        gui(devices_file)

    def cmd_server(
        self,
        _: VersionOption,
        verbose: VerboseOption,
        devices_file: DevicesFileArgument,
        check_paths: CheckPathsOption,
    ) -> None:
        """Run the rootful server, reading bytes off of the input device and forwarding them to a unix socket."""
        make_logger(2)  # Default to INFO logging for running the server
        verbose = verbose + 2
        make_logger(verbose)
        if check_paths is not None:
            settings.input["check_paths"] = check_paths

        from ..rpc.server import get_server

        get_server(device_path=devices_file).requestLoop()

    def cmd_client(
        self,
        _: VersionOption,
        verbose: VerboseOption,
    ) -> None:
        """Run the user-mode client, reading events from the rootful server's unix socket."""
        make_logger(2)  # Default to INFO logging for running the client
        verbose = verbose + 2
        make_logger(verbose)

        from ..input.handle import handle_keys

        handle_keys()

    def cmd_hidden_install(
        self,
        _: VersionOption,
        verbose: VerboseOption,
        install_to: Annotated[
            Path, typer.Argument(help="The root directory into which to install files", metavar="PATH")
        ] = Path("/"),
    ) -> None:
        """Install the SystemD system an user units and GUI application shortcut."""
        make_logger(verbose)
        from ..install import install

        print(install(root=install_to))


cli = Main()

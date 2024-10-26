import inspect
import os
import re
from pathlib import Path
from typing import Callable
from typing import List
from typing import Optional

import typer
from typer.main import get_command_name
from typing_extensions import Annotated

from ..util.config import settings


def path_autocomplete(
    file_okay: bool = True,
    dir_okay: bool = True,
    writable: bool = False,
    readable: bool = True,
    allow_dash: bool = False,
    match_wildcard: Optional[str] = None,
) -> Callable[[str], list[str]]:
    def wildcard_match(string: str, pattern: str) -> bool:
        regex = re.escape(pattern).replace(r"\?", ".").replace(r"\*", ".*")
        return re.fullmatch(regex, string) is not None

    def completer(incomplete: str) -> list[str]:
        items = os.listdir()
        completions = []
        for item in items:
            if not file_okay and os.path.isfile(item):
                continue
            elif not dir_okay and os.path.isdir(item):
                continue

            if readable and not os.access(item, os.R_OK):
                continue
            if writable and not os.access(item, os.W_OK):
                continue

            completions.append(item)

        if allow_dash:
            completions.append("-")

        if match_wildcard is not None:
            completions = list(filter(lambda i: wildcard_match(i, match_wildcard), completions))  # type: ignore

        return [i for i in completions if i.startswith(incomplete)]

    return completer


def version_callback(value: bool):
    if value:
        from ..__version__ import version

        print(version)
        raise typer.Exit()


class Cli:
    help: str
    subcommands: List["Cli"]

    def __init__(self, name: str = "") -> None:
        if name:
            self.name = name
        else:
            self.name = self.__class__.__name__.lower()

        app_settings = {
            "context_settings": {"help_option_names": ["-h", "--help"]},
            "no_args_is_help": True,
            "pretty_exceptions_show_locals": False,
        }
        if getattr(self, "help", None) is not None:
            app_settings["help"] = self.help

        self.run = typer.Typer(**app_settings)

        for method, func in inspect.getmembers(self, predicate=inspect.ismethod):
            # Put commands into the typer app
            if method.startswith("cmd_"):
                command_name = get_command_name(method.removeprefix("cmd_"))
                self.run.command(name=command_name)(func)

        if getattr(self, "subcommands", None) is not None:
            for subcommand in self.subcommands:
                self.add_subcommand(subcommand)

    def add_subcommand(self, other: "Cli") -> None:
        self.run.add_typer(other.run, name=other.name)


VerboseOption = Annotated[
    int,
    typer.Option(
        "--verbose",
        "-v",
        count=True,
        help="Increase logging verbosity (repeat for more)",
        default_factory=lambda: 0,
        show_default=False,
    ),
]
VersionOption = Annotated[
    Optional[bool],
    typer.Option(
        "--version",
        "-V",
        callback=version_callback,
        help="Print the version and exit",
        default_factory=lambda: None,
        is_eager=True,
        show_default=False,
    ),
]
PortOption = Annotated[
    int,
    typer.Option(
        "--port",
        "-p",
        help="The port to listen on or connect to",
        min=1,
        max=65535,
        metavar="PORT",
        rich_help_panel="Command Options",
        default_factory=lambda: settings.rpc.get("port", 10018),
        show_default=str(settings.rpc.get("port", 10018)),
    ),
]
DevicesFileArgument = Annotated[
    Path,
    typer.Argument(
        autocompletion=path_autocomplete(file_okay=True, dir_okay=False),
        help="The path to a file with syntax similar to /proc/bus/input/devices",
        default_factory=lambda: Path("/proc/bus/input/devices"),
        show_default="/proc/bus/input/devices",
    ),
]
CheckPathsOption = Annotated[
    bool | None,
    typer.Option(
        help="Whether to check paths that should exist (like those under /sys or /dev/input)",
        rich_help_panel="Command Options",
        default_factory=lambda: settings.input.get("check_paths", True),
        show_default="--check-paths",
    ),
]

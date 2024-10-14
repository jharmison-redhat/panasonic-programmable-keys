from rich import print

from .base import Cli, VerboseOption, VersionOption, version_callback
from ..util import make_logger
from ..util import settings


class Config(Cli):
    help = "Operations on the configuration"

    def cmd_view(self, verbose: VerboseOption, _: VersionOption) -> None:
        """View the current configuration, as loaded"""
        logger = make_logger(verbose)
        print(settings.as_dict())
        logger.debug(__file__)


class Main(Cli):
    help = "Panasonic Programmable Keys Configuration Utility"
    subcommands = [Config()]

    def cmd_version(self) -> None:
        """Print the version and exit"""
        version_callback(True)


cli = Main()

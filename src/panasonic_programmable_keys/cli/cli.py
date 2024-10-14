from rich import print

from ..util import make_logger
from ..util import settings
from .base import Cli
from .base import VerboseOption
from .base import VersionOption
from .base import version_callback


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

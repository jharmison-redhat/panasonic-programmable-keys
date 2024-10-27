import sys
from pathlib import Path

from jinja2 import Environment
from jinja2 import PackageLoader
from jinja2 import select_autoescape

from ..util import logger


def install(root: Path | None = None) -> tuple[Path, ...]:
    if root is None:
        root = Path("/")

    env = Environment(loader=PackageLoader("panasonic_programmable_keys.install"), autoescape=select_autoescape())
    app_name = sys.argv[0]

    logger.debug(f"Templating installation files for {app_name}")

    server = "panasonic-programmable-keys-server.service"
    client = "panasonic-programmable-keys-client.service"
    application = "panasonic-programmable-keys.application"

    server_service = env.get_template(f"{server}.j2").render(ppk_full_path=app_name)
    logger.debug(f"{server}:\n{server_service}")
    client_service = env.get_template(f"{client}.j2").render(ppk_full_path=app_name)
    logger.debug(f"{client}:\n{client_service}")
    application_file = env.get_template(f"{application}.j2").render(ppk_full_path=app_name)
    logger.debug(f"{application}:\n{application_file}")

    server_service_dest = root.joinpath(Path(f"etc/systemd/system/{server}"))
    client_service_dest = root.joinpath(Path(f"etc/systemd/user/{client}"))
    application_file_dest = root.joinpath(Path(f"usr/local/share/applications/{application}"))

    logger.debug("Ensuring directories exist...")
    server_service_dest.parent.mkdir(parents=True, exist_ok=True)
    client_service_dest.parent.mkdir(parents=True, exist_ok=True)
    application_file_dest.parent.mkdir(parents=True, exist_ok=True)

    with open(server_service_dest, "w") as f:
        logger.debug(f"Writing {server_service_dest}")
        f.write(server_service)
    with open(client_service_dest, "w") as f:
        logger.debug(f"Writing {client_service_dest}")
        f.write(client_service)
    with open(application_file_dest, "w") as f:
        logger.debug(f"Writing {application_file_dest}")
        f.write(application_file)

    server_service_symlink = root.joinpath(Path(f"etc/systemd/system/multi-user.target.wants/{server}"))
    server_service_symlink.parent.mkdir(parents=True, exist_ok=True)
    logger.debug(f"Symlinking {server_service_symlink} to {server_service_dest}")
    server_service_symlink.symlink_to(server_service_dest)
    client_service_symlink = root.joinpath(Path(f"etc/systemd/user/basic.target.wants/{client}"))
    client_service_symlink.parent.mkdir(parents=True, exist_ok=True)
    logger.debug(f"Symlinking {client_service_symlink} to {client_service_dest}")
    client_service_symlink.symlink_to(client_service_dest)

    return (
        server_service_dest,
        client_service_dest,
        application_file_dest,
        server_service_symlink,
        client_service_symlink,
    )

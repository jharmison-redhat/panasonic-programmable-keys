from concurrent.futures import ThreadPoolExecutor

from ..rpc.client import KeyClient
from ..util import logger
from ..util import settings
from ..util.shell import shell
from .models import KeyPressEvent


def handle_keys():
    handled_keys = settings.keyboard.get("enabled_keys", [])
    client = KeyClient()
    # Only handle if the client is operational
    if client.ping():
        futures = []
        # Submit shell execution to the thread pool
        with ThreadPoolExecutor() as thread_pool:
            # Iterate through keys delivered by the client proxy
            key_event: KeyPressEvent
            for key_event in client.yield_keys():
                logger.debug(f"Processing {key_event}")
                # Only react to press events, not release events
                if key_event.type.name == "press":
                    # Only react if it's a key we've marked for handling
                    key_name = key_event.descriptor.name
                    if key_name in handled_keys:
                        desired_command = settings.keyboard.get(key_name, "")
                        logger.info(f"Executing: {desired_command}")
                        output = shell(desired_command, fail=False)
                        futures.append(thread_pool.submit(logger.info, output))
                    else:
                        logger.warning(f"Unhandled key received ({key_name}) - did you mean to configure it?")
                else:
                    # This was a release
                    pass
        # Block until all remaining children processes have stopped
        for future in futures:
            future.result()
    else:
        raise RuntimeError(f"Unable to reach the server on {client.socket}")

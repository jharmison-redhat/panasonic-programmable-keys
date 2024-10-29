import os
import shlex
import subprocess
from typing import Dict
from typing import Iterable

from .helpers import merge
from .logging import logger


class ShellRuntimeException(RuntimeError):
    """Shell command returned non-zero return code.
    Attributes:
        code -- the return code from the shell command
    """

    def __init__(self, code: int | None, line: str | None):
        """Save the code with the exception."""
        self.code = code
        self.line = line


def _utf8ify(line_bytes: bytes | None = None) -> str:
    """Decode line_bytes as utf-8 and strips excess whitespace."""
    if line_bytes is not None:
        return line_bytes.decode("utf-8").rstrip()
    else:
        return ""


def shell(
    cmd: str = "",
    fail: bool = True,
    stderr: int | None = subprocess.STDOUT,
    env: Dict[str, str] = merge(os.environ.copy(), vars),
) -> Iterable[str]:
    """Run a command in a subprocess, yielding lines of output from it.
    By default will throw an Exception depending on  the return code of the
    command. To change this behavior, pass fail=False.
    """
    logger.debug("Running: {}".format(cmd))
    proc = subprocess.Popen(
        shlex.split(cmd),  # nosec
        stdout=subprocess.PIPE,
        stderr=stderr,
        env=env,
    )

    last_line = None
    assert proc.stdout is not None
    for line in map(_utf8ify, iter(proc.stdout.readline, b"")):
        last_line = line
        yield line

    ret = proc.wait()
    if fail and ret != 0:
        logger.error("Command errored: {}".format(cmd))
        raise ShellRuntimeException(ret, last_line)
    elif ret != 0:
        logger.warning("Command returned {}: {}".format(ret, cmd))


def shellw(
    cmd: str = "",
    fail: bool = True,
    stderr: int | None = subprocess.STDOUT,
    env: Dict[str, str] = merge(os.environ.copy(), vars),
) -> str:
    """Run a command in a subprocess, wait for it to finish, return all
    lines from it as a single string."""
    return "\n".join([line for line in shell(cmd=cmd, fail=fail, stderr=stderr, env=env)])

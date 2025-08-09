"""Thin wrapper around the ``launchctl`` command."""

from __future__ import annotations

import logging
import os
import platform
import shutil
import subprocess  # noqa: S404
import sys
from pathlib import Path
from subprocess import CompletedProcess, run  # noqa: S404
from typing import TYPE_CHECKING

from onginred.config import DEFAULT_LAUNCHCTL_PATH

if TYPE_CHECKING:
    from onginred.protocols import CommandRunner

__all__ = ["LaunchctlClient", "LaunchctlError"]


class LaunchctlError(Exception):
    """Error raised when ``launchctl`` cannot be resolved or invoked."""


logger = logging.getLogger(__name__)


class LaunchctlClient:
    """Client responsible for executing ``launchctl`` commands."""

    def __init__(self, path: Path | None = None, runner: CommandRunner = run):
        self.path = path or self._resolve_launchctl()
        self._runner = runner

    @staticmethod
    def _resolve_launchctl() -> Path:
        """Locate the ``launchctl`` binary or raise ``LaunchctlError``."""
        if DEFAULT_LAUNCHCTL_PATH.exists():
            return DEFAULT_LAUNCHCTL_PATH

        found = shutil.which("launchctl")
        if found:
            try:
                return Path(found).resolve(strict=True)
            except OSError as e:
                msg = "`launchctl` binary cannot be found at /bin/launchctl or via PATH."
                raise LaunchctlError(msg) from e
        msg = "`launchctl` binary cannot be found."
        raise LaunchctlError(msg)

    def _run(self, *args: str, check: bool) -> subprocess.CompletedProcess[str]:
        cmd = [str(self.path), *args]
        logger.info("executing launchctl command", extra={"cmd": cmd})
        res = self._runner(cmd, check=check)
        logger.debug(
            "launchctl command finished",
            extra={"cmd": cmd, "returncode": res.returncode},
        )
        return res

    def load(self, plist_path: Path, *, _user_domain: bool = True) -> CompletedProcess[str]:
        if sys.platform == "darwin" and platform.mac_ver()[0] >= "11":
            domain = f"gui/{os.getuid()}"
            return self._run("bootstrap", domain, str(plist_path), check=False)
        return self._run("load", str(plist_path), check=False)

    def unload(self, plist_path: Path) -> subprocess.CompletedProcess[str]:
        if sys.platform == "darwin" and platform.mac_ver()[0] >= "11":
            domain = f"gui/{os.getuid()}"
            return self._run("bootout", domain, str(plist_path), check=True)
        return self._run("unload", str(plist_path), check=True)

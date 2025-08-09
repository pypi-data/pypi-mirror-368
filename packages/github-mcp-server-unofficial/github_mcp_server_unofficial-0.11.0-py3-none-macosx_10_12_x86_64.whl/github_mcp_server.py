import os
import sys
import sysconfig
from pathlib import Path


def find_github_mcp_server_bin() -> Path:
    """Return the path to github-mcp-server."""

    # adapted from uv's python launcher

    exe = "github-mcp-server" + sysconfig.get_config_var("EXE")

    path = Path(sysconfig.get_path("scripts")) / exe
    if path.is_file():
        return path

    if sys.version_info >= (3, 10):
        user_scheme = sysconfig.get_preferred_scheme("user")
    elif os.name == "nt":
        user_scheme = "nt_user"
    elif sys.platform == "darwin" and sys._framework:
        user_scheme = "osx_framework_user"
    else:
        user_scheme = "posix_user"

    path = Path(sysconfig.get_path("scripts", scheme=user_scheme)) / exe
    if path.is_file():
        return path

    # Search in `bin` adjacent to package root (as created by `pip install --target`).
    pkg_root = Path(__file__).parent
    target_path = pkg_root / "bin" / exe
    if path.is_file():
        return target_path

    raise FileNotFoundError(path)

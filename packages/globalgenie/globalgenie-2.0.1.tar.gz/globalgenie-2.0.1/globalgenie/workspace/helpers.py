from pathlib import Path
from typing import Optional

from globalgenie.utils.log import logger


def get_workspace_dir_from_env() -> Optional[Path]:
    from os import getenv

    from globalgenie.constants import WORKSPACE_DIR_ENV_VAR

    logger.debug(f"Reading {WORKSPACE_DIR_ENV_VAR} from environment variables")
    workspace_dir = getenv(WORKSPACE_DIR_ENV_VAR, None)
    if workspace_dir is not None:
        return Path(workspace_dir)
    return None


def get_workspace_dir_path(ws_root_path: Path) -> Path:
    """
    Get the workspace directory path from the given workspace root path.
    GlobalGenie workspace dir can be found at:
        1. subdirectory: workspace
        2. In a folder defined by the pyproject.toml file
    """
    from globalgenie.utils.pyproject import read_pyproject_globalgenie

    logger.debug(f"Searching for a workspace directory in {ws_root_path}")

    # Case 1: Look for a subdirectory with name: workspace
    ws_workspace_dir = ws_root_path.joinpath("workspace")
    logger.debug(f"Searching {ws_workspace_dir}")
    if ws_workspace_dir.exists() and ws_workspace_dir.is_dir():
        return ws_workspace_dir

    # Case 2: Look for a folder defined by the pyproject.toml file
    ws_pyproject_toml = ws_root_path.joinpath("pyproject.toml")
    if ws_pyproject_toml.exists() and ws_pyproject_toml.is_file():
        globalgenie_conf = read_pyproject_globalgenie(ws_pyproject_toml)
        if globalgenie_conf is not None:
            globalgenie_conf_workspace_dir_str = globalgenie_conf.get("workspace", None)
            if globalgenie_conf_workspace_dir_str is not None:
                globalgenie_conf_workspace_dir_path = ws_root_path.joinpath(globalgenie_conf_workspace_dir_str)
            else:
                logger.error("Workspace directory not specified in pyproject.toml")
                exit(0)
            logger.debug(f"Searching {globalgenie_conf_workspace_dir_path}")
            if globalgenie_conf_workspace_dir_path.exists() and globalgenie_conf_workspace_dir_path.is_dir():
                return globalgenie_conf_workspace_dir_path

    logger.error(f"Could not find a workspace at: {ws_root_path}")
    exit(0)

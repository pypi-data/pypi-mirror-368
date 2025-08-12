from pathlib import Path
from typing import Dict, Optional

from globalgenie.utils.log import log_debug, logger


def read_pyproject_globalgenie(pyproject_file: Path) -> Optional[Dict]:
    log_debug(f"Reading {pyproject_file}")
    try:
        import tomli

        pyproject_dict = tomli.loads(pyproject_file.read_text())
        globalgenie_conf = pyproject_dict.get("tool", {}).get("globalgenie", None)
        if globalgenie_conf is not None and isinstance(globalgenie_conf, dict):
            return globalgenie_conf
    except Exception as e:
        logger.error(f"Could not read {pyproject_file}: {e}")
    return None

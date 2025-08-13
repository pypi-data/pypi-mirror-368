import os
from pathlib import Path


def get_atoti_home() -> Path:
    return Path(os.environ.get("ATOTI_HOME", Path.home() / ".atoti"))

from __future__ import annotations

from enum import Enum, auto
from typing import final

from .license_key_env_var_name import LICENSE_KEY_ENV_VAR_NAME


@final
class LicenseKeyLocation(Enum):
    EMBEDDED = auto()
    """Use the embedded community edition license key."""

    ENVIRONMENT = auto()
    f"""Read the license key from the :guilabel:`{LICENSE_KEY_ENV_VAR_NAME}` environment variable."""

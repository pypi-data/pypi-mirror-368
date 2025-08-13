from __future__ import annotations

from abc import ABC
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from atoti import (  # noqa: ICN003 # pylint: disable=nested-import,undeclared-dependency
        Session,
        SessionConfig,
    )


class Plugin(ABC):  # noqa: B024
    """Class extended by Atoti plugins."""

    def session_config_hook(
        self,
        session_config: SessionConfig,
        /,
    ) -> SessionConfig:
        """Hook called with a config before it is used to start a session."""
        return session_config

    def session_hook(
        self,
        session: Session,  # noqa: ARG002
        /,
    ) -> None:
        """Hook called after a session is started."""
        return

    @property
    def _key(self) -> str | None:
        """The key of the corresponding Java plugin.

        When not ``None``, the `install()` method of the plugin will be called when starting the application.
        """
        return None

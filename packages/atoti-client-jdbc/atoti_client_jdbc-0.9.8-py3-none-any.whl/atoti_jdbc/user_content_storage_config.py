from __future__ import annotations

from dataclasses import KW_ONLY
from typing import final

from atoti._collections import FrozenMapping, frozendict
from atoti._pydantic import PYDANTIC_CONFIG as _PYDANTIC_CONFIG
from pydantic.dataclasses import dataclass

from ._connection_config import ConnectionConfig


@final
@dataclass(config=_PYDANTIC_CONFIG, frozen=True)
class UserContentStorageConfig(ConnectionConfig):
    """The config for storing user content in a separate database.

    Example:
        >>> from atoti_jdbc import UserContentStorageConfig
        >>> config = UserContentStorageConfig(
        ...     "h2:/home/user/database/file/path;USER=username;PASSWORD=passwd"
        ... )

    """

    _: KW_ONLY

    hibernate_options: FrozenMapping[str, str] = frozendict()
    """Extra options to pass to Hibernate.

    See `AvailableSettings <https://javadoc.io/static/org.hibernate/hibernate-core/5.6.15.Final/org/hibernate/cfg/AvailableSettings.html>`__.
    """

    prefix: str | None = None
    """
    The prefix to add to all paths when reading and writing files and directories.

    This allows sharing the same database in multiple Atoti applications without conflicts.
    """

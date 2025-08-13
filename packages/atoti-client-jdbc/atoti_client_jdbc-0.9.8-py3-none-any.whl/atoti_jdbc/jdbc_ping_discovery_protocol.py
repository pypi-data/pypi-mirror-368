from __future__ import annotations

from dataclasses import KW_ONLY
from typing import final

from atoti._pydantic import PYDANTIC_CONFIG as _PYDANTIC_CONFIG
from atoti.distribution_protocols import DiscoveryProtocol
from pydantic.dataclasses import dataclass
from typing_extensions import override

from ._connection_config import ConnectionConfig


@final
@dataclass(config=_PYDANTIC_CONFIG, frozen=True)
class JdbcPingDiscoveryProtocol(ConnectionConfig, DiscoveryProtocol):
    """Discovery protocol relying on a JDBC connection.

    The set of nodes is stored in a database table, allowing each node to join the cluster without having to know any other node.
    """

    _: KW_ONLY

    username: str

    password: str

    delete_single_sql: str | None = None

    initialize_sql: str | None = None

    insert_single_sql: str | None = None

    remove_all_data_on_view_change: bool = True
    """"Defined by the FILE_PING protocol.

    See http://jgroups.org/manual4/index.html#_removal_of_zombie_files.
    """

    remove_old_coords_on_view_change: bool = True
    """"Defined by the FILE_PING protocol.

    See http://jgroups.org/manual4/index.html#_removal_of_zombie_files.
    """

    select_all_pingdata_sql: str | None = None

    write_data_on_find: bool = True
    """"Defined by the FILE_PING protocol.

    See http://jgroups.org/manual4/index.html#_removal_of_zombie_files.
    """

    @property
    @override
    def _name(self) -> str:
        return "JDBC_PING"

    @property
    @override
    def _properties(self) -> dict[str, object]:
        properties = super()._properties
        for property_name in ["driver", "password", "url", "username"]:
            properties[f"connection_{property_name}"] = properties.pop(property_name)
        return properties

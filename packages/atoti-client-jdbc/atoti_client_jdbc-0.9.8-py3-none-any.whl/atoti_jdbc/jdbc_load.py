from __future__ import annotations

from dataclasses import KW_ONLY
from typing import final

from atoti._collections import FrozenSequence
from atoti._constant import Constant
from atoti._pydantic import PYDANTIC_CONFIG as _PYDANTIC_CONFIG
from atoti.data_load import DataLoad
from pydantic.dataclasses import dataclass
from typing_extensions import override

from ._connection_config import ConnectionConfig


# This base class is only used so that `query` comes before `url` in `JdbcLoad`.
@dataclass(config=_PYDANTIC_CONFIG, frozen=True)
class _JdbcLoadBase(DataLoad):  # pylint: disable=final-class
    query: str
    """The query (usually SQL) to execute."""

    _: KW_ONLY


@final
@dataclass(config=_PYDANTIC_CONFIG, frozen=True)
# Unlike the other plugin symbols, this one repeats the plugin key in its name (i.e. it is not just `Load`).
# The reasons are:
# - Class names should be nouns but `Load` can read as a verb (`JdbcLoad` reads a noun, as opposed to `LoadJdbc`).
# - It avoids stuttering: `table.load(Load())`.
# - Consistency with the built-in `CsvLoad` and `ParquetLoad` classes.
class JdbcLoad(ConnectionConfig, _JdbcLoadBase):
    """The definition of a JDBC query.

    Example:
        .. doctest::
            :hide:

            >>> from pathlib import Path
            >>> from shutil import copy
            >>> tmp_path = getfixture("tmp_path")
            >>> database_path = Path(
            ...     copy(TEST_RESOURCES_PATH / "jdbc" / "h2-database.mv.db", tmp_path)
            ... )
            >>> # Remove `.mv.db` extension.
            >>> database_path = database_path.parent / Path(database_path.stem).stem
            >>> session = getfixture("session_with_jdbc_plugin")

        >>> from atoti_jdbc import JdbcLoad
        >>> url = f"h2:{database_path};USER=root;PASSWORD=pass"
        >>> jdbc_load = JdbcLoad("SELECT * FROM MYTABLE", url=url)

        Inferring data types:

        >>> data_types = session.tables.infer_data_types(jdbc_load)
        >>> data_types
        {'ID': 'int', 'CITY': 'String', 'MY_VALUE': 'long'}

        Creating table from inferred data types:

        >>> table = session.create_table(
        ...     "Cities",
        ...     data_types=data_types,
        ...     keys={"ID"},
        ... )

        Loading query results into the table:

        >>> table.load(jdbc_load)
        >>> table.head().sort_index()
                CITY  MY_VALUE
        ID
        1      Paris       100
        2     London        80
        3   New York        90
        4     Berlin        70
        5    Jakarta        75
        >>> table.drop()

        Using a parametrized query:

        >>> table.load(
        ...     JdbcLoad(
        ...         "SELECT * FROM MYTABLE WHERE City IN (?, ?)",
        ...         parameters=["Paris", "New York"],
        ...         url=url,
        ...     )
        ... )
        >>> table.head().sort_index()
                CITY  MY_VALUE
        ID
        1      Paris       100
        3   New York        90

    See Also:
        The other :class:`~atoti.data_load.DataLoad` implementations.

    """

    _: KW_ONLY

    parameters: FrozenSequence[Constant] = ()
    """The query parameters, sometimes also called *bind variables*."""

    @property
    @override
    def _options(
        self,
    ) -> dict[str, object]:
        assert self.driver is not None
        return {
            "driverClass": self.driver,
            "parameters": self.parameters,
            "query": self.query,
            "url": self.url,
        }

    @property
    @override
    def _plugin_key(
        self,
    ) -> str:
        return "JDBC"

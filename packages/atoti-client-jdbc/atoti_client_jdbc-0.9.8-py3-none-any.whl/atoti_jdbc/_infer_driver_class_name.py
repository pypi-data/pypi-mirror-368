import re
from collections.abc import Mapping

from .driver import (
    H2_DRIVER,
    IBM_DB2_DRIVER,
    MARIADB_DRIVER,
    MSSQL_DRIVER,
    ORACLE_DRIVER,
    POSTGRESQL_DRIVER,
)

_DRIVER_CLASS_NAME_FROM_SCHEME: Mapping[str, str] = {
    "db2": IBM_DB2_DRIVER,
    "h2": H2_DRIVER,
    "mariadb": MARIADB_DRIVER,
    "oracle": ORACLE_DRIVER,
    "postgresql": POSTGRESQL_DRIVER,
    "sqlserver": MSSQL_DRIVER,
}


def infer_driver_class_name(url: str, /) -> str:
    match = re.match(r"jdbc:?(?P<scheme>[^:]+):", url)
    scheme = match.group("scheme") if match else None
    driver_class_name = _DRIVER_CLASS_NAME_FROM_SCHEME.get(scheme) if scheme else None

    if not driver_class_name:
        raise ValueError(
            f"Cannot infer driver class name from URL: `{url}`, specify it manually.",
        )

    return driver_class_name

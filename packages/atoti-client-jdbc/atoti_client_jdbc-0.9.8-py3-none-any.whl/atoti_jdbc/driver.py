"""Constants for the Java class names of the embedded JDBC drivers.

To use another JDBC driver, add it to :attr:`~atoti.SessionConfig.extra_jars`.

Example:
    Storing user content in Google BigQuery:

    >>> from pathlib import Path
    >>> from atoti_jdbc import UserContentStorageConfig
    >>> user_content_storage_config = UserContentStorageConfig(
    ...     "jdbc:bigquery://https://www.googleapis.com/bigquery/v2:443;ProjectId=PROJECT_ID;OAuthType=0;OAuthServiceAcctEmail=EMAIL_OF_SERVICEACCOUNT;OAuthPvtKeyPath=path/to/json/keys;",
    ...     driver="com.simba.googlebigquery.jdbc42.Driver",
    ... )
    >>> session_config = tt.SessionConfig(
    ...     extra_jars=Path("odbc_jdbc_drivers").glob("*.jar"),
    ...     user_content_storage=user_content_storage_config,
    ... )

"""

from atoti._jdbc import H2_DRIVER as _H2_DRIVER

H2_DRIVER = _H2_DRIVER
"""H2 driver class name."""

IBM_DB2_DRIVER = "com.ibm.db2.jcc.DB2Driver"
"""IBM Db2 driver class name."""

MARIADB_DRIVER = "org.mariadb.jdbc.Driver"
"""MariaDB driver class name."""

MSSQL_DRIVER = "com.microsoft.sqlserver.jdbc.SQLServerDriver"
"""Microsoft SQL Server driver class name."""

ORACLE_DRIVER = "oracle.jdbc.OracleDriver"
"""Oracle driver class name."""

POSTGRESQL_DRIVER = "org.postgresql.Driver"
"""PostgreSQL driver class name."""

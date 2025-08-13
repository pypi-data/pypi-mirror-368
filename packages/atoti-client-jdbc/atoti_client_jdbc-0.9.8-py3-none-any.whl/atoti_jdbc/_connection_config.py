from __future__ import annotations

from dataclasses import KW_ONLY
from typing import Annotated

from atoti._jdbc import normalize_jdbc_url
from atoti._pydantic import PYDANTIC_CONFIG as _PYDANTIC_CONFIG
from pydantic import AfterValidator, ValidationInfo
from pydantic.dataclasses import dataclass

from ._infer_driver_class_name import infer_driver_class_name


def _validate_driver(driver: str | None, validation_info: ValidationInfo, /) -> str:
    if driver:
        return driver

    url = validation_info.data.get("url")
    assert isinstance(url, str)
    return driver or infer_driver_class_name(url)


@dataclass(config=_PYDANTIC_CONFIG, frozen=True)
class ConnectionConfig:  # pylint: disable=final-class
    url: Annotated[str, AfterValidator(normalize_jdbc_url)]
    """The JDBC connection string of the database.

    The ``"jdbc"`` scheme is optional but the database specific scheme (such as ``"h2"``) is mandatory.
    For instance:

    * ``"h2:/home/user/database/file/path;USER=username;PASSWORD=passwd"``
    * ``"postgresql://postgresql.db.server:5430/example?user=username&password=passwd"``

    More examples can be found `here <https://www.baeldung.com/java-jdbc-url-format>`__.

    This defines Hibernate's `URL <https://javadoc.io/static/org.hibernate/hibernate-core/5.6.15.Final/org/hibernate/cfg/AvailableSettings.html#URL>`__ option.
    """

    _: KW_ONLY

    driver: Annotated[str | None, AfterValidator(_validate_driver)] = None
    """The Java class name of the :mod:`~atoti_jdbc.driver` to use.

    This defines Hibernate's `DRIVER <https://javadoc.io/static/org.hibernate/hibernate-core/5.6.15.Final/org/hibernate/cfg/AvailableSettings.html#DRIVER>`__ option.

    Inferred from :attr:`url` if ``None``.
    """

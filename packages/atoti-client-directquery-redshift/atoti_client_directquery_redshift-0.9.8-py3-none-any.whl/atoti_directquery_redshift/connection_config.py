from typing import Annotated, final

from atoti._pydantic import PYDANTIC_CONFIG as _PYDANTIC_CONFIG
from atoti.directquery._external_database_connection_config import (
    AutoMultiColumnArrayConversionConfig,
    CacheConfig,
    EmulatedTimeTravelConfig,
    ExternalDatabaseConnectionConfig,
    PasswordConfig,
)
from pydantic import Field
from pydantic.dataclasses import dataclass
from typing_extensions import override


@final
@dataclass(config=_PYDANTIC_CONFIG, frozen=True, kw_only=True)
class ConnectionConfig(
    ExternalDatabaseConnectionConfig,
    AutoMultiColumnArrayConversionConfig,
    CacheConfig,
    PasswordConfig,
):
    """Config to connect to a Redshift database.

    Example:
        .. doctest::
            :hide:

            >>> session = getfixture("session_with_directquery_redshift_plugin")

        >>> import os
        >>> from atoti_directquery_redshift import ConnectionConfig
        >>> connection_config = ConnectionConfig(
        ...     url="jdbc:redshift://"
        ...     + os.environ["REDSHIFT_ACCOUNT_IDENTIFIER"]
        ...     + ".redshift.amazonaws.com:5439/dev?user="
        ...     + os.environ["REDSHIFT_USERNAME"]
        ...     + "&schema=test_resources",
        ...     password=os.environ["REDSHIFT_PASSWORD"],
        ... )
        >>> external_database = session.connect_to_external_database(connection_config)

    """

    url: str
    """The JDBC connection string."""

    connection_pool_size: Annotated[
        int,
        Field(gt=0),
    ] = 450  # Keep in sync with Java default
    """The maximum size that the pool is allowed to reach, including both idle and in-use connections.

    When the pool reaches this size, and no idle connections are available, the creation of new connections will block.
    """

    time_travel: EmulatedTimeTravelConfig | None = None
    """Optional configuration for emulated time-travel.

    :meta private:
    """

    @property
    @override
    def _database_key(self) -> str:
        return "REDSHIFT"

    @property
    @override
    def _options(self) -> dict[str, str]:
        return {
            **super()._options,
            **self._auto_multi_array_conversion_options,
            **self._cache_options,
            "CONNECTION_POOL_SIZE": str(self.connection_pool_size),
            **(
                self.time_travel._emulated_time_travel_options
                if self.time_travel
                else {}
            ),
        }

    @property
    @override
    def _password(self) -> str | None:
        return self.password

    @property
    @override
    def _url(self) -> str | None:
        return self.url

from typing import final

from atoti._pydantic import PYDANTIC_CONFIG as _PYDANTIC_CONFIG
from atoti.directquery._external_database_connection_config import (
    AutoMultiColumnArrayConversionConfig,
    EmulatedTimeTravelConfig,
    ExternalDatabaseConnectionConfig,
    PasswordConfig,
)
from pydantic.dataclasses import dataclass
from typing_extensions import override


@final
@dataclass(config=_PYDANTIC_CONFIG, frozen=True, kw_only=True)
class ConnectionConfig(
    ExternalDatabaseConnectionConfig,
    AutoMultiColumnArrayConversionConfig,
    PasswordConfig,
):
    """Config to connect to a Synapse database.

    Example:
        .. doctest::
            :hide:

            >>> account_identifier = "tck-directquery-ondemand"
            >>> session = getfixture("session_with_directquery_synapse_plugin")

        >>> import os
        >>> from atoti_directquery_synapse import ConnectionConfig
        >>> connection_config = ConnectionConfig(
        ...     url="jdbc:sqlserver://"
        ...     + account_identifier
        ...     + ".sql.azuresynapse.net;authentication="
        ...     + os.environ["SYNAPSE_AUTHENTICATION_METHOD"]
        ...     + ";user="
        ...     + os.environ["SYNAPSE_USERNAME"],
        ...     password=os.environ["SYNAPSE_PASSWORD"],
        ... )
        >>> external_database = session.connect_to_external_database(connection_config)

    """

    url: str
    """The JDBC connection string.

    See https://docs.microsoft.com/en-us/azure/synapse-analytics/sql/connection-strings#sample-jdbc-connection-string for more information.
    """

    time_travel: EmulatedTimeTravelConfig | None = None
    """Optional configuration for emulated time-travel.

    :meta private:
    """

    @property
    @override
    def _database_key(self) -> str:
        return "SYNAPSE"

    @property
    @override
    def _options(self) -> dict[str, str]:
        return {
            **super()._options,
            **self._auto_multi_array_conversion_options,
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

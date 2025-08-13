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
    """Config to connect to a Microsoft SQL Server database.

    See Also:
        :class:`atoti_directquery_snowflake.ConnectionConfig` for an example.

    """

    url: str
    """The JDBC connection string.

    See https://learn.microsoft.com/en-us/sql/connect/jdbc/building-the-connection-url?view=sql-server-ver16 for more information.
    """

    time_travel: EmulatedTimeTravelConfig | None = None
    """Optional configuration for emulated time-travel.

    :meta private:
    """

    @property
    @override
    def _database_key(self) -> str:
        return "MS_SQL"

    @property
    @override
    def _options(self) -> dict[str, str]:
        return {
            **super()._options,
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

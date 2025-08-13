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
    """Config to connect to an external database through JDBC.

    See Also:
        :class:`atoti_directquery_snowflake.ConnectionConfig` for an example.

    """

    url: str
    """The JDBC connection string."""

    sql_dialect_key: str
    """The key of the SQL dialect to use.

    The dialect will typically be provided with an :attr:`extra JAR <atoti.SessionConfig.extra_jars>`.
    """

    password_parameter_name: str | None = None
    """The name of the query string parameter in which :attr:`password` should be added to :attr:`url`.

    Unused when :attr:`password` is ``None``, required when it is not.
    """

    time_travel: EmulatedTimeTravelConfig | None = None
    """Optional configuration for emulated time-travel.

    :meta private:
    """

    @property
    @override
    def _database_key(self) -> str:
        return "GENERIC_JDBC"

    @property
    @override
    def _options(self) -> dict[str, str]:
        return {
            **super()._options,
            "CONNECTOR_KEY": self.sql_dialect_key,
            **(
                {"PASSWORD_PROPERTY_NAME": self.password_parameter_name}
                if self.password_parameter_name
                else {}
            ),
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

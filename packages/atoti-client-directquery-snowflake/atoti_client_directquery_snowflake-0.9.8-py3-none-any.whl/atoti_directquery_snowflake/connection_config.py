from typing import final

from atoti._pydantic import PYDANTIC_CONFIG as _PYDANTIC_CONFIG
from atoti.directquery._external_database_connection_config import (
    AutoMultiColumnArrayConversionConfig,
    CacheConfig,
    ExternalDatabaseConnectionConfig,
    PasswordConfig,
    TimeTravelConfig,
)
from pydantic.dataclasses import dataclass
from typing_extensions import override


@final
@dataclass(config=_PYDANTIC_CONFIG, frozen=True, kw_only=True)
class ConnectionConfig(
    ExternalDatabaseConnectionConfig,
    AutoMultiColumnArrayConversionConfig,
    CacheConfig,
    PasswordConfig,
    TimeTravelConfig,
):
    """Config to connect to a Snowflake database.

    Example:
        .. doctest::
            :hide:

            >>> session = getfixture("session_with_directquery_snowflake_plugin")

        >>> import os
        >>> from atoti_directquery_snowflake import ConnectionConfig
        >>> connection_config = ConnectionConfig(
        ...     url="jdbc:snowflake://"
        ...     + os.environ["SNOWFLAKE_ACCOUNT_IDENTIFIER"]
        ...     + ".snowflakecomputing.com/?user="
        ...     + os.environ["SNOWFLAKE_USERNAME"],
        ...     password=os.environ["SNOWFLAKE_PASSWORD"],
        ... )
        >>> external_database = session.connect_to_external_database(connection_config)
    """

    url: str
    """The JDBC connection string.

    See https://docs.snowflake.com/en/user-guide/jdbc-configure.html#jdbc-driver-connection-string for more information.
    """

    array_agg_wrapper_function_name: str | None = None
    """The name of the User Defined Function to use to wrap the aggregations on arrays to improve performance.

    This function must be defined in Snowflake and accessible to the role running the queries.
    """

    feeding_warehouse_name: str | None = None
    """The name of the warehouse to use for the initial feeding.

    If ``None``, the main warehouse will be used.
    """

    @property
    @override
    def _database_key(self) -> str:
        return "SNOWFLAKE"

    @property
    @override
    def _options(self) -> dict[str, str]:
        return {
            **super()._options,
            **self._auto_multi_array_conversion_options,
            **self._cache_options,
            **self._time_travel_options,
            **(
                {
                    "ARRAY_AGG_WRAPPER_FUNCTION_NAME": self.array_agg_wrapper_function_name,
                }
                if self.array_agg_wrapper_function_name
                else {}
            ),
            **(
                {
                    "FEEDING_WAREHOUSE_NAME": self.feeding_warehouse_name,
                }
                if self.feeding_warehouse_name
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

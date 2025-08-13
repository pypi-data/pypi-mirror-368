from typing import Literal, final

from atoti._pydantic import PYDANTIC_CONFIG as _PYDANTIC_CONFIG
from atoti.directquery._external_database_connection_config import (
    AutoMultiColumnArrayConversionConfig,
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
    """Config to connect to a Databricks database.

    :atoti_server_docs:`To aggregate native Databrick arrays, UDAFs (User Defined Aggregation Functions) provided by ActiveViam must be registered on the cluster <directquery/databases/databricks/#vectors-support>`.

    Native array aggregation is not supported on SQL warehouses.

    Example:
        .. doctest::
            :hide:

            >>> session = getfixture("session_with_directquery_databricks_plugin")

        >>> import os
        >>> from atoti_directquery_databricks import ConnectionConfig
        >>> connection_config = ConnectionConfig(
        ...     url="jdbc:databricks://"
        ...     + os.environ["DATABRICKS_SERVER_HOSTNAME"]
        ...     + "/default;"
        ...     + "transportMode=http;"
        ...     + "ssl=1;"
        ...     + "httpPath="
        ...     + os.environ["DATABRICKS_HTTP_PATH_CLUSTER_RUNTIME_15"]
        ...     + ";"
        ...     + "AuthMech=3;"
        ...     + "UID=token;"
        ...     + "EnableArrow=0;",
        ...     password=os.environ["DATABRICKS_AUTH_TOKEN"],
        ... )
        >>> external_database = session.connect_to_external_database(connection_config)

    """

    url: str
    """The JDBC connection string."""

    feeding_url: str | None = None
    """When not ``None``, this JDBC connection string will be used instead of :attr:`url` for the feeding phases."""

    time_travel: Literal[False, "lax", "strict"] = "strict"
    """How to use Databricks' time travel feature.

    Databricks does not support time travel with views, so the options are:

    * ``False``: tables and views are queried on the latest state of the database.
    * ``"lax"``: tables are queried with time travel but views are queried without it.
    * ``"strict"``: tables are queried with time travel and querying a view raises an error.
    """

    array_sum_agg_function_name: str | None = None
    """The name (if different from the default) of the UDAF performing :func:`atoti.agg.sum` on native arrays.

    Note:
        This function must be defined in Databricks and accessible to the role running the queries.
    """

    array_long_agg_function_name: str | None = None
    """The name (if different from the default) of the UDAF performing :func:`atoti.agg.long` on native arrays.

    Note:
        This function must be defined in Databricks and accessible to the role running the queries.
    """

    array_short_agg_function_name: str | None = None
    """The name (if different from the default) of the UDAF performing :func:`atoti.agg.short` on native arrays.

    Note:
        This function must be defined in Databricks and accessible to the role running the queries.
    """

    array_sum_product_agg_function_name: str | None = None
    """The name (if different from the default) of the UDAF performing :func:`atoti.agg.sum_product` on native arrays.

    Note:
        This function must be defined in Databricks and accessible to the role running the queries.
    """

    @property
    @override
    def _database_key(self) -> str:
        return "DATABRICKS"

    @property
    @override
    def _options(self) -> dict[str, str]:
        return {
            **super()._options,
            **self._auto_multi_array_conversion_options,
            **(
                {"FEEDING_CONNECTION_STRING": self.feeding_url}
                if self.feeding_url
                else {}
            ),
            **(
                {
                    "SUM_VECTOR_FUNCTION_NAME": self.array_sum_agg_function_name,
                }
                if self.array_sum_agg_function_name
                else {}
            ),
            **(
                {
                    "LONG_VECTOR_FUNCTION_NAME": self.array_long_agg_function_name,
                }
                if self.array_long_agg_function_name
                else {}
            ),
            **(
                {
                    "SHORT_VECTOR_FUNCTION_NAME": self.array_short_agg_function_name,
                }
                if self.array_short_agg_function_name
                else {}
            ),
            **(
                {
                    "SUM_PRODUCT_VECTOR_FUNCTION_NAME": self.array_sum_product_agg_function_name,
                }
                if self.array_sum_product_agg_function_name
                else {}
            ),
            "TIME_TRAVEL": self.time_travel.upper() if self.time_travel else "DISABLED",
        }

    @property
    @override
    def _password(self) -> str | None:
        return self.password

    @property
    @override
    def _url(self) -> str | None:
        return self.url

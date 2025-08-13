from pathlib import Path
from typing import final

from atoti._pydantic import PYDANTIC_CONFIG as _PYDANTIC_CONFIG
from atoti.directquery._external_database_connection_config import (
    AutoMultiColumnArrayConversionConfig,
    CacheConfig,
    ExternalDatabaseConnectionConfig,
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
    TimeTravelConfig,
):
    """Config to connect to a BigQuery database.

    Example:
        .. doctest::
            :hide:

            >>> session = getfixture("session_with_directquery_bigquery_plugin")

        >>> from atoti_directquery_bigquery import ConnectionConfig
        >>> connection_config = ConnectionConfig()
        >>> external_database = session.connect_to_external_database(connection_config)

    """

    credentials: Path | None = None
    """The path to the `BigQuery credentials file <https://cloud.google.com/docs/authentication/getting-started#setting_the_environment_variable>`__.

    If ``None``, the `application default credentials <https://cloud.google.com/java/docs/reference/google-auth-library/latest/com.google.auth.oauth2.GoogleCredentials#com_google_auth_oauth2_GoogleCredentials_getApplicationDefault__>`__ will be used.
    """

    @property
    @override
    def _database_key(self) -> str:
        return "BIGQUERY"

    @property
    @override
    def _options(self) -> dict[str, str]:
        return {
            **super()._options,
            **self._auto_multi_array_conversion_options,
            **self._cache_options,
            **self._time_travel_options,
        }

    @property
    @override
    def _password(self) -> str | None:
        return None if self.credentials is None else str(self.credentials)

    @property
    @override
    def _url(self) -> str | None:
        return None if self.credentials is None else str(self.credentials)

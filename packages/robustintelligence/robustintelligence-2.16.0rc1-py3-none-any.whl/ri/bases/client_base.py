"""The base client to interact with the Robust Intelligence API."""

from typing import Any, Optional, Union

from ri.apiclient import ApiClient, Configuration
from ri.fwclient import ApiClient as FWApiClient
from ri.fwclient import Configuration as FWConfiguration

DEFAULT_CHANNEL_TIMEOUT = 300.0
FIREWALL_AUTH_TOKEN_NAME = "X-Firewall-Auth-Token"
RIME_API_KEY_NAME = "rime-api-key"


class BaseClient:
    """Base client class for creating API clients with comprehensive configuration options.

    Initializes an API client with settings for authentication, server configuration, SSL details,
    and operation-specific configurations.

    :param domain: str
        The base URL of the API server.
    :param api_key: str
        The API key used for authentication. Each entry in the dict specifies an API key.
        The dict key is the name of the security scheme in the OAS specification.
        The dict value is the API key secret.
    :param api_key_header_name: str
        The header name for the API key.
    :param channel_timeout: float
        The timeout for network connections in seconds. Default is 300 seconds.
    :param username: Optional[str]
        Username for HTTP basic authentication.
    :param password: Optional[str]
        Password for HTTP basic authentication.
    :param access_token: Optional[str]
        Access token for bearer authentication.
    :param ssl_ca_cert: Optional[str]
        Path to a file of concatenated CA certificates in PEM format.
    :param proxy: Optional[str]
        URL of the proxy server to use for requests.
    :param verify_ssl: bool
        Whether to verify SSL certificates. Default is True.
    :param cert_file: Optional[str]
        Path to a client certificate file (PEM).
    :param key_file: Optional[str]
        Path to a client key file (PEM).
    :param api_key_prefix: Optional[Dict[str, str]]
        Dict to store API prefix (e.g., Bearer). The dict key is the name of the security scheme in the OAS specification.
        The dict value is an API key prefix when generating the auth data.
    :param server_index: Optional[int]
        Index to servers configuration for selecting the base URL.
    :param server_variables: Optional[Dict[str, str]]
        Variables to replace in the templated server URL.
    :param server_operation_index: Optional[Dict[str, int]]
        Mapping from operation ID to an index to server configuration.
    :param server_operation_variables: Optional[Dict[str, Dict[str, str]]]
        Mapping from operation ID to variables for templated server URLs.

    """

    def __init__(  # noqa: PLR0913
        self,
        domain: str,
        api_key: str,
        api_key_header_name: str,
        channel_timeout: float = DEFAULT_CHANNEL_TIMEOUT,
        api_key_prefix: Optional[dict[Any, Any]] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        access_token: Optional[str] = None,
        ssl_ca_cert: Optional[str] = None,
        verify_ssl: bool = True,
        cert_file: Optional[str] = None,
        key_file: Optional[str] = None,
        proxy: Optional[str] = None,
        server_index: Optional[int] = None,
        server_variables: Optional[dict[str, str]] = None,
        server_operation_index: Optional[dict[str, int]] = None,
        server_operation_variables: Optional[dict[str, dict[str, str]]] = None,
    ):
        """Initialize the base client."""
        host = self._cleanup_domain(domain)
        self._api_client: Union[FWApiClient, ApiClient, None] = None
        config: Union[FWConfiguration, Configuration]
        if api_key_header_name == FIREWALL_AUTH_TOKEN_NAME:
            config = FWConfiguration(
                host=host,
                api_key={api_key_header_name: api_key},
                api_key_prefix=api_key_prefix,
                username=username,
                password=password,
                access_token=access_token,
                server_index=server_index,
                server_variables=server_variables,
                server_operation_index=server_operation_index,
                server_operation_variables=server_operation_variables,
                ssl_ca_cert=ssl_ca_cert,
            )
            config.verify_ssl = verify_ssl
            config.cert_file = cert_file
            config.key_file = key_file
            config.proxy = proxy
            self._api_client = FWApiClient(configuration=config)
        else:
            config = Configuration(
                host=host,
                api_key={api_key_header_name: api_key},
                api_key_prefix=api_key_prefix,
                username=username,
                password=password,
                access_token=access_token,
                server_index=server_index,
                server_variables=server_variables,
                server_operation_index=server_operation_index,
                server_operation_variables=server_operation_variables,
                ssl_ca_cert=ssl_ca_cert,
            )
            config.verify_ssl = verify_ssl
            config.cert_file = cert_file
            config.key_file = key_file
            config.proxy = proxy
            self._api_client = ApiClient(configuration=config)

        self._api_client.rest_client.pool_manager.connection_pool_kw[
            "timeout"
        ] = channel_timeout

    @staticmethod
    def _cleanup_domain(domain: str) -> str:
        if domain.endswith("/"):
            domain = domain[:-1]
        if not domain.startswith("https://") and not domain.startswith("http://"):
            domain = "https://" + domain
        return domain

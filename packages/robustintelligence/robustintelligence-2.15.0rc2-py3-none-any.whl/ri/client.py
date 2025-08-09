"""Client interfaces for the Robust Intelligence API."""

from functools import cached_property
from typing import TYPE_CHECKING, Any, Optional

from typing_extensions import deprecated

from ri.bases.client_base import (
    DEFAULT_CHANNEL_TIMEOUT,
    FIREWALL_AUTH_TOKEN_NAME,
    RIME_API_KEY_NAME,
    BaseClient,
)

if TYPE_CHECKING:
    from ri.apiclient.api import (
        AgentManagerApi,
        CustomerManagedKeyServiceApi,
        DataCollectorApi,
        DetectionApi,
        FeatureFlagApi,
        FileScanningApi,
        FileUploadApi,
        FirewallServiceApi,
        GenerativeValidationApi,
        ImageRegistryApi,
        IntegrationServiceApi,
        JobReaderApi,
        ModelCardServiceApi,
        ModelTestingApi,
        MonitorServiceApi,
        NotificationSettingApi,
        ProjectServiceApi,
        RegistryServiceApi,
        ResultsReaderApi,
        RIMEInfoApi,
        ScheduleServiceApi,
        SecurityDBApi,
        UserApi,
        WorkspaceServiceApi,
    )
    from ri.fwclient.api import FirewallApi
    from ri.fwclient.api import FirewallInstanceManagerApi
    from ri.utils.utils import RIUtils


class RIClient(BaseClient):
    """Robust Intelligence client to interact with the RI API.

    :param domain: str
        The base URL of the API server.
    :param api_key: str
        The API key used for authentication. Each entry in the dict specifies an API key.
        The dict key is the name of the security scheme in the OAS specification.
        The dict value is the API key secret.
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
        """Initialize the Robust Intelligence client."""
        super().__init__(
            domain=domain,
            api_key=api_key,
            api_key_prefix=api_key_prefix,
            channel_timeout=channel_timeout,
            username=username,
            password=password,
            access_token=access_token,
            ssl_ca_cert=ssl_ca_cert,
            verify_ssl=verify_ssl,
            cert_file=cert_file,
            key_file=key_file,
            proxy=proxy,
            server_index=server_index,
            server_variables=server_variables,
            server_operation_index=server_operation_index,
            server_operation_variables=server_operation_variables,
            api_key_header_name=RIME_API_KEY_NAME,
        )

    @cached_property
    def agent_manager(self) -> "AgentManagerApi":
        """Access the agent manager api.

        :return: AgentManagerApi: the agent manager api
        """
        from ri.apiclient.api import AgentManagerApi

        return AgentManagerApi(self._api_client)

    @cached_property
    def customer_managed_key_service(self) -> "CustomerManagedKeyServiceApi":
        """Access the customer managed key service api.

        :return: CustomerManagedKeyServiceApi: the customer managed key service api
        """
        from ri.apiclient.api import CustomerManagedKeyServiceApi

        return CustomerManagedKeyServiceApi(self._api_client)

    @cached_property
    def data_collector(self) -> "DataCollectorApi":
        """Access the data collector api.

        :return: DataCollectorApi: the data collector api
        """
        from ri.apiclient.api import DataCollectorApi

        return DataCollectorApi(self._api_client)

    @cached_property
    def detection(self) -> "DetectionApi":
        """Access the detection api.

        :return: DetectionApi: the detection api
        """
        from ri.apiclient.api import DetectionApi

        return DetectionApi(self._api_client)

    @cached_property
    def feature_flag(self) -> "FeatureFlagApi":
        """Access the feature flag api.

        :return: FeatureFlagApi: the feature flag api
        """
        from ri.apiclient.api import FeatureFlagApi

        return FeatureFlagApi(self._api_client)

    @cached_property
    def file_scanning(self) -> "FileScanningApi":
        """Access the file scanning api.

        :return: FileScanningApi: the file scanning api
        """
        from ri.apiclient.api import FileScanningApi

        return FileScanningApi(self._api_client)

    @cached_property
    def file_upload(self) -> "FileUploadApi":
        """Access the file upload api.

        :return: FileUploadApi: the file upload api
        """
        from ri.apiclient.api import FileUploadApi

        return FileUploadApi(self._api_client)

    @cached_property
    def firewall_service(self) -> "FirewallServiceApi":
        """Access the firewall service api.

        :return: FirewallServiceApi: the firewall service api
        """
        from ri.apiclient.api import FirewallServiceApi

        return FirewallServiceApi(self._api_client)

    @cached_property
    @deprecated(
        "this property is deprecated and will be removed in 2.11, use generative_validation instead"
    )
    def generative_testing(self) -> "GenerativeValidationApi":
        """Access the Generative AI validation api.

        :return: GenerativeValidationApi: the Generative AI validation  api
        """
        from ri.apiclient.api import GenerativeValidationApi

        return GenerativeValidationApi(self._api_client)

    @cached_property
    def generative_validation(self) -> "GenerativeValidationApi":
        """Access the Generative AI validation api.

        :return: GenerativeValidationApi: the Generative AI validation  api
        """
        from ri.apiclient.api import GenerativeValidationApi

        return GenerativeValidationApi(self._api_client)

    @cached_property
    def image_registry(self) -> "ImageRegistryApi":
        """Access the image registry api.

        :return: ImageRegistryApi: the image registry api
        """
        from ri.apiclient.api import ImageRegistryApi

        return ImageRegistryApi(self._api_client)

    @cached_property
    def integration_service(self) -> "IntegrationServiceApi":
        """Access the integration service api.

        :return: IntegrationServiceApi: the integration service api
        """
        from ri.apiclient.api import IntegrationServiceApi

        return IntegrationServiceApi(self._api_client)

    @cached_property
    def job_reader(self) -> "JobReaderApi":
        """Access the job reader api.

        :return: JobReaderApi: the job reader api
        """
        from ri.apiclient.api import JobReaderApi

        return JobReaderApi(self._api_client)

    @cached_property
    def model_card_service(self) -> "ModelCardServiceApi":
        """Access the model card service api.

        :return: ModelCardServiceApi: the model card service api
        """
        from ri.apiclient.api import ModelCardServiceApi

        return ModelCardServiceApi(self._api_client)

    @cached_property
    def model_testing(self) -> "ModelTestingApi":
        """Access the model testing api.

        :return: ModelTestingApi: the model testing api
        """
        from ri.apiclient.api import ModelTestingApi

        return ModelTestingApi(self._api_client)

    @cached_property
    def monitor_service(self) -> "MonitorServiceApi":
        """Access the monitor service api.

        :return: MonitorServiceApi: the monitor service api
        """
        from ri.apiclient.api import MonitorServiceApi

        return MonitorServiceApi(self._api_client)

    @cached_property
    def notification_setting(self) -> "NotificationSettingApi":
        """Access the notification setting api.

        :return: NotificationSettingApi: the notification setting api
        """
        from ri.apiclient.api import NotificationSettingApi

        return NotificationSettingApi(self._api_client)

    @cached_property
    def project_service(self) -> "ProjectServiceApi":
        """Access the project service api.

        :return: ProjectServiceApi: the project service api
        """
        from ri.apiclient.api import ProjectServiceApi

        return ProjectServiceApi(self._api_client)

    @cached_property
    def registry_service(self) -> "RegistryServiceApi":
        """Access the registry service api.

        :return: RegistryServiceApi: the registry service api
        """
        from ri.apiclient.api import RegistryServiceApi

        return RegistryServiceApi(self._api_client)

    @cached_property
    def results_reader(self) -> "ResultsReaderApi":
        """Access the results reader api.

        :return: ResultsReaderApi: the results reader api
        """
        from ri.apiclient.api import ResultsReaderApi

        return ResultsReaderApi(self._api_client)

    @cached_property
    def rime_info(self) -> "RIMEInfoApi":
        """Access the rime info api.

        :return: RIMEInfoApi: the rime info api
        """
        from ri.apiclient.api import RIMEInfoApi

        return RIMEInfoApi(self._api_client)

    @cached_property
    def schedule_service(self) -> "ScheduleServiceApi":
        """Access the schedule service api.

        :return: ScheduleServiceApi: the schedule service api
        """
        from ri.apiclient.api import ScheduleServiceApi

        return ScheduleServiceApi(self._api_client)

    @cached_property
    def security_db(self) -> "SecurityDBApi":
        """Access the security db api.

        :return: SecurityDBApi: the security db api
        """
        from ri.apiclient.api import SecurityDBApi

        return SecurityDBApi(self._api_client)

    @cached_property
    def user(self) -> "UserApi":
        """Access the user api.

        :return: UserApi: the user api
        """
        from ri.apiclient.api import UserApi

        return UserApi(self._api_client)

    @cached_property
    def utils(self) -> "RIUtils":
        """Access the utility functions.

        :return: RIUtils: the utility functions
        """
        from ri.utils.utils import RIUtils

        return RIUtils(self)

    @cached_property
    def workspace_service(self) -> "WorkspaceServiceApi":
        """Access the workspace service api.

        :return: WorkspaceServiceApi: the workspace service api
        """
        from ri.apiclient.api import WorkspaceServiceApi

        return WorkspaceServiceApi(self._api_client)


class FirewallClient(BaseClient):
    """Robust Intelligence firewall client to interact with the Firewall API.

    :param domain: str
        The base URL of the API server.
    :param auth_token: str
        The API key used for authentication. Each entry in the dict specifies an API key.
        The dict key is the name of the security scheme in the OAS specification.
        The dict value is the API key secret.
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
        auth_token: str,
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
        """Initialize the Robust Intelligence firewall client."""
        super().__init__(
            domain=domain,
            api_key=auth_token,
            api_key_header_name=FIREWALL_AUTH_TOKEN_NAME,
            api_key_prefix=api_key_prefix,
            channel_timeout=channel_timeout,
            username=username,
            password=password,
            access_token=access_token,
            ssl_ca_cert=ssl_ca_cert,
            verify_ssl=verify_ssl,
            cert_file=cert_file,
            key_file=key_file,
            proxy=proxy,
            server_index=server_index,
            server_variables=server_variables,
            server_operation_index=server_operation_index,
            server_operation_variables=server_operation_variables,
        )
        self._firewall: Optional[FirewallApi] = None
        self._firewall_instance_manager: Optional[FirewallInstanceManagerApi] = None

    @property
    def firewall(self) -> "FirewallApi":
        """Access the firewall api.

        :return: FirewallApi: the firewall api
        """
        if not self._firewall:
            from ri.fwclient.api import FirewallApi

            self._firewall = FirewallApi(self._api_client)

        return self._firewall

    @property
    def firewall_instance_manager(self) -> "FirewallInstanceManagerApi":
        """Access the firewall instance manager api.

        :return: FirewallInstanceManagerApi: the firewall instance manager api
        """
        if not self._firewall_instance_manager:
            from ri.fwclient.api import FirewallInstanceManagerApi

            self._firewall_instance_manager = FirewallInstanceManagerApi(
                self._api_client
            )

        return self._firewall_instance_manager

from typing import Any, Optional, Dict, Union

from chilo_api.core.types.server_settings import ServerSettings
from chilo_api.core.router import Router


class ServerArguments:
    '''
    A class to handle server arguments for the Chilo API.
    This class is responsible for initializing server arguments from command line or API settings.
    Attributes
    ----------
    host: str
        The host address for the server.
    port: int
        The port number for the server.
    reload: bool
        Whether to enable auto-reload for the server.
    verbose: bool
        Whether to enable verbose logging for the server.
    timeout: Optional[int]
        The timeout duration for the server in seconds.
    handlers: str
        The handler files pattern for the server.
    protobufs: Optional[str]
        The directory containing protobuf files for gRPC endpoints.
    openapi_validate_request: bool
        Whether to validate requests against OpenAPI specifications.
    openapi_validate_response: bool
        Whether to validate responses against OpenAPI specifications.
    api_type: str
        The type of API (e.g., REST, gRPC).
    api_config: Any
        The API configuration object containing additional settings.
    reflection: bool
        Whether to enable server reflection for gRPC services.
    private_key: Optional[str]
        The path to the private key file for secure connections.
    certificate: Optional[str]
        The path to the certificate file for secure connections.
    max_workers: Optional[int]
        The maximum number of worker threads for the server.
    Methods
    ----------
    route(environ, server_response):
        Routes the request to the appropriate handler based on the environment and server response.
    '''

    def __init__(self, args: ServerSettings, api: Router) -> None:
        self.__source: Dict[str, str] = {}
        self.__api_config: Router = api
        self.__api_type: str = api.api_type
        self.__timeout: Optional[Union[int, float]] = api.timeout
        self.__handlers: str = api.handlers
        self.__protobufs: Optional[str] = api.protobufs
        self.__host: str = self.__get_setting('host', args, api)
        self.__port: int = self.__get_setting('port', args, api)
        self.__reload: bool = self.__get_setting('reload', args, api)
        self.__verbose: bool = self.__get_setting('verbose', args, api)
        self.__openapi_validate_request: bool = api.openapi_validate_request
        self.__openapi_validate_response: bool = api.openapi_validate_response
        self.__reflection: bool = self.__get_setting('reflection', args, api)
        self.__private_key: Union[str, None] = self.__get_setting('private_key', args, api)
        self.__certificate: Union[str, None] = self.__get_setting('certificate', args, api)
        self.__max_workers: Union[int, None] = self.__get_setting('max_workers', args, api)

    @property
    def host(self) -> str:
        return self.__host

    @property
    def port(self) -> int:
        return self.__port

    @property
    def reload(self) -> bool:
        return self.__reload

    @property
    def verbose(self) -> bool:
        return self.__verbose

    @property
    def source(self) -> Dict[str, str]:
        return self.__source

    @property
    def timeout(self) -> Optional[Union[int, float]]:
        return self.__timeout

    @property
    def handlers(self) -> str:
        return self.__handlers

    @property
    def protobufs(self) -> Optional[str]:
        return self.__protobufs

    @property
    def openapi_validate_request(self) -> bool:
        return self.__openapi_validate_request

    @property
    def openapi_validate_response(self) -> bool:
        return self.__openapi_validate_response

    @property
    def api_type(self) -> str:
        return self.__api_type

    @property
    def api_config(self) -> Router:
        return self.__api_config

    @property
    def reflection(self) -> bool:
        return self.__reflection

    @property
    def private_key(self) -> Union[str, None]:
        return self.__private_key

    @property
    def certificate(self) -> Union[str, None]:
        return self.__certificate

    @property
    def max_workers(self) -> Union[int, None]:
        return self.__max_workers

    def __get_setting(self, key: str, args: ServerSettings, api: Router) -> Any:
        arg_value = getattr(args, key, None)
        if arg_value is not None:
            self.__source[key] = 'command-line'
            # Convert string values to appropriate types
            if key == 'port':
                return int(arg_value) if isinstance(arg_value, str) else arg_value
            if key in ['reload', 'verbose']:
                if isinstance(arg_value, str):
                    return arg_value.lower() in ('true', '1', 'yes', 'on')  # pragma: no cover
                return bool(arg_value)
            return str(arg_value)
        self.__source[key] = 'api-settings'  # pragma: no cover
        return getattr(api, key)  # pragma: no cover

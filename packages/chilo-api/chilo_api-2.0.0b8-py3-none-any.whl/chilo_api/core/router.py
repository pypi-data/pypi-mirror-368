from typing import Any, Callable, Iterator, Optional, Union, cast
from typing_extensions import Unpack

from werkzeug.wrappers import Request as WSGIRequest, Response as WSGIResponse

from chilo_api.core.validator.config import ConfigValidator
from chilo_api.core.executor import Executor
from chilo_api.core.rest.request import RestRequest as Request
from chilo_api.core.rest.response import RestResponse as Response
from chilo_api.core.resolver import Resolver
from chilo_api.core.rest.pipeline import RestPipeline
from chilo_api.core.types.router_settings import RouterSettings


class Router:
    '''
    A class to route request to appropriate file/endpoint and run the appropriate middleware

    Attributes
    ----------
    handlers: str
        glob pattern location of the handler files eligible for being a handler
    base_path: str
        base path of the url to route from (ex. http://locahost/{base_path}/your-endpoint)
    host: str
        host url to run the api on (defaults to 127.0.0.1)
    port: int
        default to port to run (defaults to 3000)
    reload: bool
        determines if system will watch files and automatically reload
    verbose: bool
        determines if verbose logging is enabled
    timeout: int
        global value to timeout all handlers after certain amout of time
    openapi_validate_request: bool
        determines if api should validate request against spece openapi spec
    openapi_validate_response: bool
        determines if api should validate response against spece openapi spec
    private_key: Optional[str]
        the path to the private key file for secure connections
    certificate: Optional[str]
        the path to the certificate file for secure connections
    api_type: str
        type of api (ex. rest, grpc)
    cors: bool or str
        determines if cors is enabled; can be a boolean or a string with allowed origins
    reflection: bool
        whether to enable server reflection for gRPC services
    before_all: Optional[Callable[[Any, Any, Any], None]]
        function to run before all requests
    after_all: Optional[Callable[[Any, Any, Any], None]]
        function to run after all requests; if not errors were detected
    when_auth_required: Optional[Callable[[Any, Any, Any], None]]
        function to run when `auth_required` is true on the endpoint requirements dectorator
    on_error: Optional[Callable[[Any, Any, Any], None]]
        function to run when 500 level is raised
    on_timeout: Optional[Callable[[Any, Any, Any], None]]
        function to run when timeout error is raised
    protobufs: Optional[str]
        glob pattern location of where the protobufs are located

    Methods
    ----------
    route(environ, server_response):
        routes request to the correct endpoint and runs approprite middleware
    '''

    def __init__(self, **kwargs: Unpack[RouterSettings]) -> None:
        '''
        Constructs all necessary configuration for the router

        Parameters
        ----------
        handlers: str
            glob pattern location of the handler files eligible for being a handler
        base_path: str, optional
            base path of the url to route from (ex. http://locahost/{base_path}/your-endpoint); default /
        protobufs: str
            glob pattern location of where the protobufs are located
        host: str, optional
            host url to run the api on (default is 127.0.0.1)
        port: int, optional
            default to port to run (default is 3000)
        reload: bool, optional
            determines if system will watch files and automatically reload (default is False)
        verbose: bool, optional 
            determines if verbose logging is enabled (default is False)
        before_all: callable, optional
            function to run before all requests
        after_all: callable, optional
            function to run after all requests; if not errors were detected
        when_auth_required: callable, optional
            function to run when `auth_required` is true on the endpoint requirements dectorator
        on_error: callable, optional
            function to run when 500 level is raised
        on_timeout: callable, optional
            function to run when timeout error is raised
        cors: bool, optional
            determines if cors is enabled (default is True)
        timeout: int, optional
            global value to timeout all handlers after certain amout of time (default is None)
        cache_size: int, optional
            size of the router cache (NOT response cache); allows for faster routing (default is 128)
        cache_mode: str, enum(all, static-only, dynamic-only)
            determies if router caches all routes or just static or dynamic routes (default is all)
        openapi_validate_request: bool, optional
            determines if api should validate request against spece openapi spec (default is False)
        openapi_validate_response: bool, optional
            determines if api should validate response against spece openapi spec (default is False)
        reflection: bool, optional
            whether to enable server reflection for gRPC services (default is False)
        private_key: str, optional
            the path to the private key file for secure connections (default is None)
        certificate: str, optional
            the path to the certificate file for secure connections (default is None)
        '''
        ConfigValidator.validate(**kwargs)
        self.__handlers: str = kwargs['handlers']
        self.__base_path: str = kwargs.get('base_path', '/')
        self.__protobufs: Optional[str] = kwargs.get('protobufs')
        self.__api_type: str = kwargs.get('api_type', 'rest')
        self.__host: str = kwargs.get('host', '127.0.0.1')
        self.__port: int = kwargs.get('port', 3000)
        self.__reload: bool = kwargs.get('reload', False)
        self.__verbose: bool = kwargs.get('verbose', False)
        self.__before_all: Optional[Callable[[Any, Any, Any], None]] = kwargs.get('before_all')
        self.__after_all: Optional[Callable[[Any, Any, Any], None]] = kwargs.get('after_all')
        self.__when_auth_required: Optional[Callable[[Any, Any, Any], None]] = kwargs.get('when_auth_required')
        self.__on_error: Optional[Callable[[Any, Any, Any], None]] = kwargs.get('on_error')
        self.__on_timeout: Optional[Callable[[Any, Any, Any], None]] = kwargs.get('on_timeout')
        self.__cors: Union[bool, str] = kwargs.get('cors', False)
        self.__timeout: Optional[int] = kwargs.get('timeout', None)
        self.__output_error: bool = kwargs.get('output_error', False)
        self.__openapi_validate_request: bool = kwargs.get('openapi_validate_request', False)
        self.__openapi_validate_response: bool = kwargs.get('openapi_validate_response', False)
        self.__reflection: bool = kwargs.get('reflection', False)
        self.__private_key: Optional[str] = kwargs.get('private_key')
        self.__certificate: Optional[str] = kwargs.get('certificate')
        self.__max_workers: Optional[int] = cast(Optional[int], kwargs.get('max_workers', 10))
        self.__executor: Executor = Executor(RestPipeline(**kwargs), Resolver(**kwargs), **kwargs)

    @property
    def handlers(self) -> str:
        return self.__handlers

    @property
    def base_path(self) -> str:
        return self.__base_path

    @property
    def api_type(self) -> str:
        return self.__api_type

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
    def timeout(self) -> Optional[int]:
        return self.__timeout

    @property
    def output_error(self) -> bool:
        return self.__output_error

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
    def on_error(self) -> Optional[Callable[[Any, Any, Any], None]]:
        return self.__on_error

    @property
    def before_all(self) -> Optional[Callable[[Any, Any, Any], None]]:
        return self.__before_all

    @property
    def after_all(self) -> Optional[Callable[[Any, Any, Any], None]]:
        return self.__after_all

    @property
    def when_auth_required(self) -> Optional[Callable[[Any, Any, Any], None]]:
        return self.__when_auth_required

    @property
    def on_timeout(self) -> Optional[Callable[[Any, Any, Any], None]]:
        return self.__on_timeout

    @property
    def cors(self) -> Union[bool, str]:
        return self.__cors

    @property
    def reflection(self) -> bool:
        return self.__api_type == 'grpc' and self.__reflection

    @property
    def private_key(self) -> Optional[str]:
        return self.__private_key

    @property
    def certificate(self) -> Optional[str]:
        return self.__certificate

    @property
    def max_workers(self) -> Optional[int]:
        return self.__max_workers

    def route(self, environ, server_response) -> Union[WSGIResponse, Iterator[bytes]]:
        request: Request = Request(wsgi=WSGIRequest(environ), timeout=self.__timeout)
        response: Response = Response(cors=self.__cors, wsgi=WSGIResponse, environ=environ, server_response=server_response)
        return self.__executor.run(request, response)

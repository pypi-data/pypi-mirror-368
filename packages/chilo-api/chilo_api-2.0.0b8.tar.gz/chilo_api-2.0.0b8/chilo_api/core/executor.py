import datetime
from typing import Any, Callable, Generator, Optional, Dict, Union
from typing_extensions import Unpack

from werkzeug.wrappers import Response as WSGIResponse

from chilo_api.core.exception import ApiException, ApiTimeOutException
from chilo_api.core.logger.common import CommonLogger
from chilo_api.core.rest.json_helper import JsonHelper
from chilo_api.core.rest.pipeline import RestPipeline
from chilo_api.core.grpc.pipeline import GRPCPipeline
from chilo_api.core.resolver import Resolver
from chilo_api.core.types.router_settings import RouterSettings


class Executor:
    '''
    A class to execute the routing and middleware for the API.
    This class is responsible for handling the request and response lifecycle, including error handling and logging.
    Attributes
    ----------
    pipeline: RestPipeline or GRPCPipeline
        The pipeline to use for processing the request and response.
    resolver: Resolver
        The resolver to use for finding the appropriate endpoint for the request.
    is_grpc: bool
        Whether the API is using gRPC or not.
    grpc_endpoint: Any
        The gRPC endpoint to use if the API is using gRPC.
    verbose: Optional[bool]
        Whether to log verbose output or not.
    output_error: Optional[bool]
        Whether to output error messages in the response.
    on_error: Callable[[Request, Response, Exception], None]
        A function to call when an error occurs during request processing.
    on_timeout: Callable[[Request, Response, Exception], None]
        A function to call when a request times out.
    logger: CommonLogger
        The logger to use for logging messages.
    error_message: str
        The default error message to use in the response when an error occurs.
    exception_mapping: Dict[str, Callable[[Request, Response, Exception], None]]
        A mapping of exception types to functions that handle those exceptions.
    is_grpc: bool
        Whether the API is using gRPC or not.
    grpc_endpoint: Any
        The gRPC endpoint to use if the API is using gRPC.
    Methods
    ----------
    run(request: Request, response: Response) -> WSGIResponse:
        Runs the request through the pipeline and returns the response. 
    stream(request: Request, response: Response) -> Generator:
        Streams the request through the pipeline and yields the response.
    '''

    def __init__(self, pipeline, resolver, **kwargs: Unpack[RouterSettings]) -> None:
        self.__is_grpc: bool = bool(kwargs.get('is_grpc', False))
        self.__grpc_endpoint: Any = kwargs.get('grpc_endpoint')
        self.__verbose: Optional[bool] = kwargs.get('verbose')
        self.__output_error: Optional[bool] = kwargs.get('output_error')
        self.__on_error: Callable[[Any, Any, Exception], None] = kwargs.get('on_error', lambda request, response, error: None)
        self.__on_timeout: Callable[[Any, Any, Exception], None] = kwargs.get('on_timeout', lambda request, response, error: None)
        self.__logger: CommonLogger = CommonLogger()
        self.__pipeline: Union[RestPipeline, GRPCPipeline] = pipeline
        self.__resolver: Resolver = resolver
        self.__resolver.auto_load()
        self.__error_message: str = str(kwargs.get('default_error_message', 'internal service error'))
        self.__exception_mapping: Dict[str, Callable[[Any, Any, Exception], None]] = {
            'ApiTimeOutException': self.__on_timeout,
            'ApiException': self.__on_error
        }

    def run(self, request: Any, response: Any) -> WSGIResponse:
        try:
            endpoint = self.__get_endpoint(request)
            self.__run_route_procedure(request, response, endpoint)
        except (ApiTimeOutException, ApiException, Exception) as error:  # NOSONAR
            self.__handle_error(request, response, error)
        finally:
            self.__log_verbose(request, response)
            self.__resolver.reset()
        return response.get_response()

    def stream(self, request: Any, response: Any) -> Generator:
        try:
            endpoint = self.__get_endpoint(request)
            yield from self.__stream_route_procedure(request, response, endpoint)
        except (ApiTimeOutException, ApiException, Exception) as error:  # NOSONAR
            self.__handle_error(request, response, error)
        finally:
            self.__log_verbose(request, response)

    def __run_route_procedure(self, request: Any, response: Any, endpoint: Any) -> Any:
        for step in self.__pipeline.steps:
            if not response.has_errors and step['should_run'] and callable(step['method']):
                step['method'](request, response, endpoint)
        return response

    def __stream_route_procedure(self, request: Any, response: Any, endpoint: Any) -> Generator:
        for step in self.__pipeline.stream_steps:
            if not response.has_errors and step['should_run'] and callable(step['method']):
                step['method'](request, response, endpoint)
        yield from endpoint.stream(request, response)

    def __get_endpoint(self, request: Any) -> Any:
        if not self.__is_grpc:
            return self.__resolver.get_endpoint(request)
        return self.__grpc_endpoint

    def __handle_error(self, request: Any, response: Any, error: Exception) -> None:
        try:
            response.code = getattr(error, 'code', 500)
            response.set_error(
                key_path=getattr(error, 'key_path', 'unknown'),
                message=getattr(error, 'message', str(error) if self.__output_error and response.code == 500 else self.__error_message)
            )
            error_func = self.__exception_mapping.get(type(error).__name__)
            if error_func is not None and callable(error_func):
                error_func(request, response, error)
            self.__logger.log(level='ERROR', log={'request': request, 'response': response, 'error': error})
        except Exception as exception:
            self.__logger.log(level='ERROR', log=exception)

    def __log_verbose(self, request: Any, response: Any) -> None:
        if not self.__verbose:
            return
        self.__logger.log(
            level='DEBUG',
            log={
                '_timestamp': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'request': JsonHelper.decode(str(request)),
                'response': JsonHelper.decode(str(response))
            }
        )

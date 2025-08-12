from typing import Any, Callable, Generator, Union, Optional
import functools
import inspect
import signal

from chilo_api.core.exception import ApiTimeOutException
from chilo_api.core.rest.request import RestRequest as Request
from chilo_api.core.rest.response import RestResponse as Response


class RequirementsHandler:
    '''
    A class to handle requirements for API endpoints.
    This class is responsible for managing the requirements for an endpoint, including timeouts, before and after functions, and custom request classes.

    Attributes
    ----------
    settings: Settings
        The settings for the requirements handler, including timeout, before and after functions, and request class
    Methods
    ----------
    raise_timeout():
        Raises a timeout exception when the request exceeds the specified timeout
    start_timeout(timeout: Optional[int] = None):
        Starts a timeout countdown for the request, using the specified timeout or the default from settings
    end_timeout():
        Ends the timeout countdown, stopping any further timeout checks
    run_before(request: Request, response: Response):
        Runs the before function if it is defined in the settings, allowing for pre-processing of the request
    run_after(request: Request, response: Response):
        Runs the after function if it is defined in the settings, allowing for post-processing of the response
    wrap_function(function: Callable[[Any, Any], Any]) -> Callable[[Request, Response], Response]:
        Wraps a function to handle the request and response lifecycle, including timeout management
    '''

    def __init__(self, settings: Any) -> None:
        self.settings = settings
        self.__timeout: Optional[int] = settings.get('timeout')
        self.__before: Optional[Callable[[Request, Response, Any], None]] = settings.get('before')
        self.__after: Optional[Callable[[Request, Response, Any], None]] = settings.get('after')
        self.__request_class: Optional[Callable[[Request], Any]] = settings.get('request_class')
        self.__stream: bool = settings.get('stream_response', False)

    def raise_timeout(self, *_: Any) -> None:
        raise ApiTimeOutException()

    def start_timeout(self, timeout: Optional[int] = None) -> None:
        countdown = self.__timeout or timeout
        if countdown is not None:
            signal.signal(signal.SIGALRM, self.raise_timeout)
            signal.alarm(countdown)

    def end_timeout(self) -> None:
        signal.alarm(0)

    def run_before(self, request: Request, response: Response) -> None:
        if self.__before and callable(self.__before):
            self.__before(request, response, self.settings)

    def run_after(self, request: Request, response: Response) -> None:
        if self.__after and callable(self.__after):
            self.__after(request, response, self.settings)

    def wrap_function(self, function: Callable[[Any, Any], Any]) -> Callable[[Any, Any], Any]:
        if self.__stream:
            return self.__wrap_stream_function(function)
        return self.__wrap_function(function)

    def __get_request_instance(self, request: Request) -> Union[Request, Any]:
        if self.__request_class and inspect.isclass(self.__request_class):
            return self.__request_class(request=request)
        return request

    def __run_start_functions(self, request: Request, response: Response) -> None:
        self.run_before(request, response)
        self.start_timeout(request.timeout if request.api_type == 'rest' else None)

    def __wrap_function(self, function: Callable[[Any, Any], Any]) -> Callable[[Request, Response], Response]:
        @functools.wraps(function)
        def function_wrapper(request: Request, response: Response) -> Response:
            self.__run_start_functions(request, response)
            if response.has_errors:
                return response
            try:
                request_instance = self.__get_request_instance(request)
                function(request_instance, response)
            finally:
                self.end_timeout()
            if not response.has_errors:
                self.run_after(request, response)
            return response
        setattr(function_wrapper, 'requirements', self.settings)
        return function_wrapper

    def __wrap_stream_function(self, function: Callable[[Any, Any], Any]) -> Callable[[Any, Any], Any]:
        @functools.wraps(function)
        def stream_wrapper(request: Request, response: Response) -> Generator[Any, None, Response]:
            self.__run_start_functions(request, response)
            if response.has_errors:
                return response
            try:
                request_instance = self.__get_request_instance(request)
                yield from function(request_instance, response)
            finally:
                self.end_timeout()
            return response  # pragma: no cover
        setattr(stream_wrapper, 'requirements', self.settings)
        return stream_wrapper

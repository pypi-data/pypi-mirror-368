from typing import Any, Dict, Generator, List, Optional, Tuple
from types import ModuleType

from chilo_api.core.exception import ApiException
from chilo_api.core import logger
from chilo_api.core.rest.request import RestRequest as Request
from chilo_api.core.rest.response import RestResponse as Response


class Endpoint:
    '''    
    A class to represent an API endpoint.
    This class encapsulates the logic for handling requests to a specific endpoint, including method execution and response handling.
    Attributes
    ----------
    module: ModuleType
        The module containing the endpoint logic.
    method: str
        The HTTP method (e.g., 'get', 'post') associated with the endpoint.
    module_method: Optional[Any]
        The method from the module that corresponds to the HTTP method, if it exists.
    requirements: Dict[str, Any]
        The requirements for the endpoint, such as authentication and required responses.
    Methods
    ----------
    run(request: Request, response: Response) -> Response:
        Executes the endpoint logic for the request and returns a response.
    stream(request: Request, response: Response) -> Generator:
        Executes the endpoint logic for streaming requests and yields responses.
    '''
    SUPPORTED_METHODS: List[str] = ['any', 'delete', 'get', 'patch', 'post', 'put']

    def __init__(self, module: ModuleType, method: str) -> None:
        self.__module: ModuleType = module
        self.__method: str = method
        self.__module_method: Optional[Any] = None if method in {'options', 'head'} else getattr(module, method)
        self.__requirements: Dict[str, Any] = {} if method in {'options', 'head'} else getattr(self.__module_method, 'requirements', {})

    @property
    def module(self) -> ModuleType:
        return self.__module

    @property
    def has_requirements(self) -> bool:
        return bool(self.__requirements)

    @property
    def requirements(self) -> Dict[str, Any]:
        return self.__requirements

    @property
    def requires_auth(self) -> Optional[bool]:
        return self.__requirements.get('auth_required')

    @property
    def has_required_response(self) -> bool:
        return bool(self.__requirements.get('required_response'))

    @property
    def has_required_route(self) -> bool:
        return bool(self.__requirements.get('required_route'))

    @property
    def required_route(self) -> str:
        return self.__requirements.get('required_route', '')

    def run(self, request: Request, response: Response) -> Response:
        if self.__method == 'options':
            return self.__run_options(request, response)
        if self.__method == 'head':
            return self.__run_head(request, response)
        if self.__module_method is not None:
            return self.__module_method(request, response)
        raise ApiException(code=405, message=f'Method \"{self.__method}\" not allowed for this endpoint')  # pragma: no cover

    def stream(self, request: Request, response: Response) -> Generator:
        if self.__module_method is not None:
            yield from self.__module_method(request, response)
        else:
            raise ApiException(code=1011, message='Stream connection not allowed for this endpoint')

    def __run_options(self, _: Request, response: Response) -> Response:
        methods, headers = self.__get_module_methods_and_headers()
        response.headers = ('Accept-Encoding', '*')
        response.headers = ('Access-Control-Request-Method', ','.join(methods))
        response.headers = ('Access-Control-Request-Headers', ','.join(headers))
        return response

    def __run_head(self, request: Request, response: Response) -> Response:
        try:
            method_func = getattr(self.__module, 'get')
            method_func(request, response)
            response.body = None
            return response
        except Exception as error:  # pragma: no cover
            logger.log(level='ERROR', log=error)
            raise ApiException(code=403, message='method not allowed') from error

    def __get_module_methods_and_headers(self) -> Tuple[List[str], List[str]]:
        methods: List[str] = []
        headers: List[str] = ['content-type']
        for method in dir(self.__module):
            if method.lower() in self.SUPPORTED_METHODS:
                methods.append(method.upper())
                method_func = getattr(self.__module, method)
                method_requirements: Dict[str, Any] = getattr(method_func, 'requirements', {})
                available_headers: List[str] = method_requirements.get('available_headers', [])
                required_headers: List[str] = method_requirements.get('required_headers', [])
                headers.extend(available_headers + required_headers)
        return methods, headers

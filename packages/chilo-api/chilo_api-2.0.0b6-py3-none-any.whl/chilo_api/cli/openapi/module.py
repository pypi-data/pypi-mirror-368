import os
from typing import Any, Dict, List, Optional, Union, Type
from types import ModuleType

from pydantic import BaseModel


class OpenAPIHandlerModule:
    '''
    A class to represent an OpenAPI handler module.
    This class encapsulates the details of a handler module, including its file path, method,
    and associated module. It provides properties to access various attributes related to the OpenAPI handler.
    Attributes
    ----------
    file_path: str
        The file path of the handler module
    module: Any
        The module associated with the handler
    method: str
        The method name of the handler
    operation_id: str
        A unique identifier for the operation, derived from the method and route path
    route_path: str
        The route path for the handler, constructed from the file path and base path
    deprecated: bool
        Indicates whether the handler is deprecated
    summary: str
        A brief summary of the handler's functionality
    tags: List[str]
        A list of tags associated with the handler, typically used for grouping in OpenAPI documentation
    requires_auth: bool
        Indicates whether authentication is required for the handler
    required_headers: List[str]
        A list of headers that are required for the handler
    available_headers: List[str]
        A list of headers that are available for the handler
    required_query: List[str]
        A list of query parameters that are required for the handler
    available_query: List[str]
        A list of query parameters that are available for the handler
    required_path_params: List[str]
        A list of path parameters that are required for the handler
    request_body_schema_name: str
        The name of the schema for the request body, derived from the method and route path
    request_body_schema: dict
        The schema for the request body, typically in JSON Schema format
    response_body_schema_name: str
        The name of the schema for the response body, derived from the method and route path
    response_body_schema: dict
        The schema for the response body, typically in JSON Schema format
    '''

    def __init__(self, **kwargs: Any) -> None:
        self.__handler_base: str = kwargs.get('handler_base', '')
        self.__file_path: str = kwargs.get('file_path', '')
        self.__module: ModuleType = kwargs['module']
        self.__method: str = kwargs.get('method', '')
        self.__base_path: str = kwargs.get('base', '').strip(os.sep)
        self.__func: Any = getattr(self.__module, self.__method, None)
        self.__requirements: Dict[str, Any] = getattr(self.__func, 'requirements', {})
        self.__route_path: str = ''

    @property
    def file_path(self) -> str:
        return self.__file_path

    @property
    def module(self) -> ModuleType:
        return self.__module

    @property
    def method(self) -> str:
        return self.__method.lower()

    @property
    def operation_id(self) -> str:
        id_prefix: str = ''.join(r for r in self.route_path.title() if r.isalnum())
        return f'{self.method.title()}{id_prefix}ChiloGenerated'

    @property
    def route_path(self) -> str:
        if self.__requirements.get('required_route'):
            self.__route_path = f"{self.__base_path}{self.__requirements['required_route']}"
        if not self.__route_path:
            self.__route_path = self.__compose_route_path()
        return self.__route_path if self.__route_path.startswith('/') else f'/{self.__route_path}'

    @property
    def deprecated(self) -> bool:
        return bool(self.__requirements.get('deprecated'))

    @property
    def summary(self) -> Optional[str]:
        return self.__requirements.get('summary')

    @property
    def tags(self) -> List[str]:
        if not self.__base_path:
            self.__base_path = 'chilo'
        return [self.__base_path.replace(os.sep, '-')]

    @property
    def requires_auth(self) -> Optional[bool]:
        return self.__requirements.get('auth_required')

    @property
    def required_headers(self) -> List[str]:
        return self.__requirements.get('required_headers', [])

    @property
    def available_headers(self) -> List[str]:
        return self.__requirements.get('available_headers', [])

    @property
    def required_query(self) -> List[str]:
        return self.__requirements.get('required_query', [])

    @property
    def available_query(self) -> List[str]:
        return self.__requirements.get('available_query', [])

    @property
    def required_path_params(self) -> List[str]:
        path_params: List[str] = []
        for path_part in self.route_path.split('/'):
            if '{' in path_part and '}' in path_part:
                cleaned_part: str = path_part.replace('{', '').replace('}', '')
                path_params.append(cleaned_part)
        return path_params

    @property
    def request_body_schema_name(self) -> str:
        return f'{self.method}{self.route_path.replace("/", "-").replace("_", "-").replace("{", "").replace("}", "")}-request-body'

    @property
    def request_body_schema(self) -> Optional[Dict[str, Any]]:
        return self.__get_schema_body('required_body')

    @property
    def response_body_schema_name(self) -> str:
        return f'{self.method}{self.route_path.replace("/", "-").replace("_", "-").replace("{", "").replace("}", "")}-response-body'

    @property
    def response_body_schema(self) -> Optional[Dict[str, Any]]:
        return self.__get_schema_body('required_response')

    def __compose_route_path(self) -> str:
        dirty_route: str = self.__file_path.split(self.__handler_base)[1]
        no_py_route: str = dirty_route.replace('.py', '')
        no_init_route: str = no_py_route.replace('__init__', '')
        hyphonated: str = no_init_route.replace('_', '-')
        clean_route: List[str] = [self.__base_path]
        for route in hyphonated.split(os.sep):
            if route.startswith('_'):  # pragma: no cover
                route = ''.join(route.split('_')[1])
                route = f'{{{route}}}'
            if route:
                clean_route.append(route)
        return '/'.join(clean_route)

    def __get_schema_body(self, schema_key: str) -> Optional[Dict[str, Any]]:  # pragma: no cover
        schema_body: Union[str, Dict[str, Any], Type[BaseModel], None] = self.__requirements.get(schema_key)
        if not schema_body or isinstance(schema_body, str):
            return None
        if isinstance(schema_body, dict):
            return schema_body
        if isinstance(schema_body, type) and issubclass(schema_body, BaseModel):
            return schema_body.model_json_schema()
        return None

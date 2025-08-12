from collections.abc import Mapping
from typing import Dict, Any, List
from types import ModuleType

from openapi_spec_validator import validate as openapi_validate_spec

from chilo_api.core.resolver.importer import ResolverImporter
from chilo_api.core.validator.schema import Schema


class OpenApiValidator:
    '''A class to validate OpenAPI specifications against the defined routes and methods.
    This class checks if the OpenAPI schema is valid, verifies that required bodies and responses exist in the schema,
    and ensures that routes and methods defined in the code match those in the OpenAPI schema.
    Attributes
    ----------
    handlers: str
        glob pattern location of the handler files eligible for being a handler
    base_path: str
        base path of the url to route from (ex. http://localhost/{base_path}/your-endpoint)
    openapi_validate_request: bool
        determines if API should validate request against specified OpenAPI spec
    openapi_validate_spec: bool
        determines if API should validate the OpenAPI spec itself
    schema: Schema
        instance of Schema class to handle OpenAPI schema loading and manipulation
    importer: ResolverImporter
        instance of ResolverImporter to import handler files and resolve routes and methods
    Methods
    ----------
    validate_openapi():
        Validates the OpenAPI schema against the defined routes and methods.
    '''
    SUPPORTED_METHODS: List[str] = ['any', 'delete', 'get', 'patch', 'post', 'put']

    def __init__(self, **kwargs: Any) -> None:
        self.__handlers: str = kwargs['handlers']
        self.__base_path: str = kwargs.get('base_path', '')
        self.__openapi_validate_request: bool = kwargs.get('openapi_validate_request', False)
        self.__openapi_validate_spec: bool = kwargs.get('openapi_validate_spec', True)
        self.__schema: Schema = Schema(**kwargs)
        self.__importer: ResolverImporter = ResolverImporter(handlers=self.__handlers)

    def validate_openapi(self) -> None:
        self.__schema.load_schema_file()
        if not self.__schema.spec:
            return
        if self.__openapi_validate_spec:
            self.__validate_openapi_spec()
        module_dict = self.__get_module_dict()
        self.__verify_required_body_exist_in_openapi(module_dict)
        self.__verify_required_response_exist_in_openapi(module_dict)
        if self.__openapi_validate_request:
            self.__verify_routes_method_exist_in_openapi(module_dict)

    def __validate_openapi_spec(self) -> None:
        if self.__schema.spec is None:
            raise RuntimeError('OpenAPI schema spec is None and cannot be validated')  # pragma: no cover
        try:
            # Ensure keys are str for openapi_spec_validator.validate
            spec_dict = dict(self.__schema.spec) if not isinstance(self.__schema.spec, Mapping) else self.__schema.spec
            spec_with_str_keys: Dict[str, Any] = {str(k): v for k, v in spec_dict.items()}
            openapi_validate_spec(spec_with_str_keys)
        except Exception as openapi_error:
            raise RuntimeError('there was a problem with your openapi schema; see above') from openapi_error

    def __get_module_dict(self) -> Dict[str, Dict[str, Any]]:
        route_list: List[str] = self.__importer.get_file_list()
        sep: str = self.__importer.file_separator
        modules: Dict[str, Dict[str, Any]] = self.__get_modules_from_routes(sep, route_list)
        return modules

    def __get_modules_from_routes(self, sep: str, route_list: List[str]) -> Dict[str, Dict[str, Any]]:
        modules: Dict[str, Dict[str, Any]] = {}
        for route_item in route_list:
            file_path: str = self.__handlers.split(f'{sep}*')[0] + route_item
            import_path: str = file_path.replace(sep, '.').replace('.py', '')
            file_route: str = self.__clean_up_route(route_item)
            module: ModuleType = self.__importer.get_imported_module_from_file(file_path, import_path)
            self.__add_routes_and_methods_to_modules(file_route, modules, module)
        return modules

    def __add_routes_and_methods_to_modules(self, file_route: str, modules: Dict[str, Dict[str, Any]], module: ModuleType) -> None:
        for method in dir(module):
            if method in self.SUPPORTED_METHODS:
                route: str = self.__determine_route(file_route, getattr(module, method))
                base: str = self.__base_path.strip('/')
                path: str = f'{base}{route}'.strip('/')
                route_path: str = f'/{path}'
                if not modules.get(route_path):
                    modules[route_path] = {'methods': []}
                modules[route_path]['methods'].append(method)
                modules[route_path]['request_schemas'] = self.__get_required_body_schemas(module)
                modules[route_path]['response_schemas'] = self.__get_required_response_schemas(module)

    def __clean_up_route(self, route_item: str) -> str:
        route_no_extension: str = route_item.replace('.py', '').replace('__init__', '')
        route_forward_slash: str = route_no_extension.replace(self.__importer.file_separator, '/')
        route_hyphonated: str = route_forward_slash.replace('_', '-')
        route_dynamic: str = self.__replace_dynamic_files_with_variales(route_hyphonated)
        route: str = route_dynamic.strip('/')
        return route

    def __replace_dynamic_files_with_variales(self, route_hyphonated: str) -> str:
        replaced: List[str] = []
        for route in route_hyphonated.split('/'):
            route_variable: str = route
            if route.startswith('-'):
                dynamic_hyphonated: str = route.replace('-', '', 1)
                dynamic_file: str = dynamic_hyphonated.replace('-', '_')
                route_variable = f'{{{dynamic_file}}}'
            replaced.append(route_variable)
        return '/'.join(replaced)

    def __determine_route(self, file_route: str, module_method: Any) -> str:
        requirements: Dict[str, Any] = getattr(module_method, 'requirements', {})
        if requirements.get('required_route'):
            required_route: str = requirements['required_route'].strip('/')
            return f'/{required_route}'
        return f'/{file_route}'

    def __get_required_body_schemas(self, module: ModuleType) -> List[str]:
        schemas: List[str] = []
        for method in dir(module):
            if method in self.SUPPORTED_METHODS:
                module_method: Any = getattr(module, method)
                requirements: Dict[str, Any] = getattr(module_method, 'requirements', {})
                if requirements.get('required_body') and isinstance(requirements['required_body'], str):
                    schemas.append(requirements['required_body'])
        return schemas

    def __get_required_response_schemas(self, module: ModuleType) -> List[str]:
        schemas: List[str] = []
        for method in dir(module):
            if method in self.SUPPORTED_METHODS:
                module_method: Any = getattr(module, method)
                requirements: Dict[str, Any] = getattr(module_method, 'requirements', {})
                if requirements.get('required_response') and isinstance(requirements['required_response'], str):
                    schemas.append(requirements['required_response'])
        return schemas

    def __verify_routes_method_exist_in_openapi(self, module_dict: Dict[str, Dict[str, Any]]) -> None:
        for route in module_dict.keys():
            if not isinstance(self.__schema.paths, dict) or not self.__schema.paths.get(route):
                raise RuntimeError(f'openapi_validate_request is enabled and route {route} does not exist in openapi')
            for method in module_dict[route]['methods']:
                if not isinstance(self.__schema.paths[route], dict) or not self.__schema.paths[route].get(method):
                    raise RuntimeError(f'openapi_validate_request is enabled and method {method} in route {route} does not exist in openapi')

    def __verify_required_body_exist_in_openapi(self, module_dict: Dict[str, Dict[str, Any]]) -> None:
        for route, values in module_dict.items():
            for schema in values.get('request_schemas', []):
                if not (
                    self.__schema.spec
                    and self.__schema.spec.get('components')
                    and self.__schema.spec['components'].get('schemas')
                    and self.__schema.spec['components']['schemas'].get(schema)
                ):
                    raise RuntimeError(f'required_body schema {schema} from {route} not found in openapi')

    def __verify_required_response_exist_in_openapi(self, module_dict: Dict[str, Dict[str, Any]]) -> None:
        for route, values in module_dict.items():
            for schema in values.get('response_schemas', []):
                if not (
                    self.__schema.spec
                    and self.__schema.spec.get('components')
                    and self.__schema.spec['components'].get('schemas')
                    and self.__schema.spec['components']['schemas'].get(schema)
                ):
                    raise RuntimeError(f'required_response schema {schema} from {route} not found in openapi')

from importlib import util
from importlib.machinery import ModuleSpec
import os
from typing import List, Any, Optional, Type, Callable

from chilo_api import Chilo
from chilo_api.cli.openapi.module import OpenAPIHandlerModule


class CLIImporter:
    '''
    Handles the importing of API modules and their associated gRPC classes.
    This class provides methods to retrieve API modules, servicer classes, response classes,
    and server methods based on the provided protobuf paths and class names. 
    Methods
    ----------
    get_api_module(api_file_name):
        Retrieves the API module based on the provided file name.
    get_imported_modules(file_list):
        Imports and returns a list of modules from the provided file paths.
    get_imported_servicer_class(protobufs_path, class_name):
        Retrieves the gRPC servicer class from the specified protobuf path and class name.
    get_imported_response_class(protobufs_path, class_name, response_name):
        Retrieves the response class from the specified protobuf path and class name.
    get_add_server_method(protobufs_path, class_name):
        Retrieves the method to add the servicer to the server from the specified protobuf path and class name.
    get_handler_modules_from_file_paths(file_paths, handlers_base, base_path):
        Retrieves the handler modules from the specified file paths.
    get_imported_module_from_file(import_path, file_path):
        Imports a module from the specified import path and file path.
    '''

    def get_api_module(self, api_file_name: str) -> Chilo:
        cwd = os.getcwd()
        api_file_location = api_file_name if '.py' in api_file_name else f'{api_file_name}.py'
        file_path = f'{cwd}/{api_file_location}'
        import_path = file_path.replace('/', '.')
        module = self.get_imported_module_from_file(import_path, file_path)
        matches = [v for v in module.__dict__.values() if isinstance(v, Chilo)]
        return matches[0]

    def get_imported_modules(self, file_list: List[str]) -> List[Any]:
        modules: List[Any] = []
        for file_path in file_list:
            import_path = self.__get_import_path_from_file(file_path)
            module = self.get_imported_module_from_file(import_path, file_path)
            modules.append(module)
        return modules

    def get_imported_servicer_class(self, protobufs_path: str, class_name: str) -> Type[Any]:
        module = self.__get_spec_module_from_file(class_name, protobufs_path, suffix='_pb2_grpc')
        servicer_class = getattr(module, class_name.capitalize() + 'Servicer', None)
        if servicer_class is None:
            raise ImportError(f'Servicer class {class_name} not found in {protobufs_path}')  # pragma: no cover
        return servicer_class

    def get_imported_response_class(self, protobufs_path: str, class_name: str, response_name: str) -> Type[Any]:
        module = self.__get_spec_module_from_file(class_name, protobufs_path)
        response_class = getattr(module, response_name, None)
        if response_class is None:
            raise ImportError(f'Response class {response_name} not found in {protobufs_path}')  # pragma: no cover
        return response_class

    def get_add_server_method(self, protobufs_path: str, class_name: str) -> Callable[..., Any]:
        server_method_name = 'add_' + class_name.capitalize() + 'Servicer_to_server'
        module = self.__get_spec_module_from_file(class_name.lower(), protobufs_path, suffix='_pb2_grpc')
        server_method = getattr(module, server_method_name, None)
        if server_method is None:
            raise ImportError(f'Server method {server_method_name} not found in {protobufs_path}')  # pragma: no cover
        return server_method

    def get_handler_modules_from_file_paths(self, file_paths: List[str], handlers_base: str, base_path: str) -> List[OpenAPIHandlerModule]:
        SUPPORTED_METHODS = ['any', 'delete', 'get', 'head', 'options', 'patch', 'post', 'put']
        modules: List[OpenAPIHandlerModule] = []
        for file_path in file_paths:
            try:
                import_path = self.__get_import_path_from_file(file_path)
                module = self.get_imported_module_from_file(import_path, file_path)
                for method in dir(module):
                    if method.lower() in SUPPORTED_METHODS:
                        modules.append(OpenAPIHandlerModule(
                            handler_base=handlers_base,
                            file_path=file_path,
                            module=module,
                            method=method,
                            base=base_path
                        ))
            except:  # NOSONAR noqa: E722 pragma: no cover
                pass
        return modules

    def get_imported_module_from_file(self, import_path: str, file_path: str) -> Any:
        spec: Optional[ModuleSpec] = util.spec_from_file_location(import_path, file_path)
        if spec is None or spec.loader is None:
            raise ImportError(f'Could not load spec or loader for {file_path}')  # pragma: no cover
        module = util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def get_imported_pb2_module(self, protobufs_path: str, service_name: str) -> Optional[Any]:
        file_path = f'{protobufs_path}/generated/{service_name.lower()}_pb2.py'
        import_path = f'{protobufs_path}/generated/{service_name.lower()}_pb2'.replace('/', '.')
        return self.get_imported_module_from_file(file_path=file_path, import_path=import_path)

    def __get_import_path_from_file(self, file_path: str) -> str:
        return file_path.replace(os.sep, '.').replace('.py', '')

    def __get_spec_module_from_file(self, class_name: str, protobufs_path: str, suffix: str = '_pb2') -> Any:
        file_name = f'{class_name}{suffix}'
        file_path = f'{protobufs_path}/generated/{file_name}.py'
        import_path = self.__get_import_path_from_file(file_path)
        return self.get_imported_module_from_file(import_path, file_path)

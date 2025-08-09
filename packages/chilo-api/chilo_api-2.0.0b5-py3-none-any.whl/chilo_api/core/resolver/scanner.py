from typing import Any, Dict, List, Tuple
from types import ModuleType

from chilo_api.core.exception import ApiException
from chilo_api.core.resolver.importer import ResolverImporter
from chilo_api.core.rest.request import RestRequest as Request


class ResolverScanner:
    '''
    A class to scan and resolve API endpoints from handler files.
    This class is responsible for scanning the file system for handler files, determining the correct import paths,
    and resolving the endpoints based on the request path.
    Attributes
    ----------
    importer: ResolverImporter
        An instance of ResolverImporter to handle the import of handler files.
    base_path: str
        The base path of the URL to route from (e.g., http://localhost/{base_path}/your-endpoint).
    has_dynamic_route: bool
        Indicates if the resolver has encountered a dynamic route.
    file_tree_climbed: bool
        Indicates if the file tree has been successfully traversed.
    dynamic_parts: Dict[int, str]
        A dictionary to store dynamic parts of the path, where keys are indices and values are the corresponding path segments.
    import_path: List[str]
        A list to store the import path of the resolved endpoint.

    Methods
    ----------
    reset():
        Resets the state of the resolver scanner, clearing dynamic parts and import paths.
    load_importer_files():
        Loads the handler files into the importer.
    get_endpoint_module(request: Request) -> ModuleType:
        Retrieves the endpoint module based on the request path.
    '''

    def __init__(self, **kwargs: Any) -> None:
        self.importer: ResolverImporter = ResolverImporter(handlers=kwargs.get('handlers', ''))
        self.base_path: str = self.importer.clean_path(kwargs.get('base_path', ''))
        self.has_dynamic_route: bool = False
        self.file_tree_climbed: bool = True
        self.dynamic_parts: Dict[int, str] = {}
        self.import_path: List[str] = []
        self.__handler_pattern: str = kwargs['handlers']
        self.__init_file = '__init__.py'

    def reset(self) -> None:
        self.has_dynamic_route = False
        self.dynamic_parts = {}
        self.file_tree_climbed = True
        self.import_path = []

    def load_importer_files(self) -> None:
        self.importer.get_handlers_file_tree()

    def get_endpoint_module(self, request: Request) -> ModuleType:
        file_path, import_path = self.__get_file_and_import_path(request.path)
        return self.importer.get_imported_module_from_file(file_path, import_path)

    def __get_file_and_import_path(self, request_path: str) -> Tuple[str, str]:
        split_path: List[str] = self.__get_request_path_as_list(request_path)
        route_path: str = self.__get_relative_path(split_path)
        file_path: str = self.__handler_pattern.split(f'{self.importer.file_separator}*')[0] + self.importer.file_separator + route_path
        import_path: str = self.__get_import_path(file_path)
        return file_path, import_path

    def __get_request_path_as_list(self, request_path: str) -> List[str]:
        base_path: str = request_path.replace(self.base_path, '')
        clean_base: str = self.importer.clean_path(base_path)
        return clean_base.split('/')

    def __get_relative_path(self, split_path: List[str]) -> str:
        file_tree: Dict[str, Any] = self.importer.get_handlers_file_tree()
        file_pattern: str = self.__get_file_pattern()
        self.__get_import_path_file_tree(split_path, 0, file_tree, file_pattern)
        return f'{self.importer.file_separator}'.join(self.import_path)

    def __get_import_path(self, relative_file_path: str) -> str:
        return relative_file_path.replace(self.importer.file_separator, '.').replace('.py', '')

    def __get_file_pattern(self) -> str:
        split_pattern: List[str] = self.__handler_pattern.split(self.importer.file_separator)
        file_pattern: str = split_pattern[-1]
        return file_pattern

    def __get_import_path_file_tree(self, split_path: List[str], split_index: int, file_tree: Dict[str, Any], file_pattern: str) -> None:
        if split_index < len(split_path):
            route_part: str = split_path[split_index].replace('-', '_')
            possible_directory, possible_file = self.__get_possible_directory_and_file(route_part, file_pattern)
            if possible_directory in file_tree:
                self.__handle_directory_path_part(possible_directory, split_path, split_index, file_tree, file_pattern)
            elif possible_file in file_tree:
                self.__handle_file_path_part(possible_file, split_path, split_index, file_tree, file_pattern)
            elif file_tree.get('__dynamic_files'):
                self.__handle_dynamic_path_part(split_path, split_index, file_tree, file_pattern)
            else:
                raise ApiException(code=404, message='route not found')

    def __get_possible_directory_and_file(self, route_part: str, file_pattern: str) -> Tuple[str, str]:
        possible_directory: str = f'{route_part}'
        possible_file: str = file_pattern.replace('*', route_part) if '*' in file_pattern else f'{possible_directory}.py'
        possible_file = self.__init_file if possible_file == '.py' else possible_file
        return possible_directory, possible_file

    def __handle_directory_path_part(self, possible_directory: str, split_path: List[str], split_index: int, file_tree: Dict[str, Any], file_pattern: str) -> None:
        self.__append_import_path(possible_directory)
        if split_index+1 < len(split_path):
            file_leaf: Dict[str, Any] = self.__determine_which_file_leaf(file_tree, possible_directory)
            self.__get_import_path_file_tree(split_path, split_index+1, file_leaf, file_pattern)
        else:
            index_file: str = file_pattern.replace('*', possible_directory) if '*' in file_pattern else self.__init_file
            self.__append_import_path(index_file)

    def __handle_file_path_part(self, possible_file: str, split_path: List[str], split_index: int, file_tree: Dict[str, Any], file_pattern: str) -> None:
        self.__append_import_path(possible_file)
        file_leaf: Dict[str, Any] = self.__determine_which_file_leaf(file_tree, possible_file)
        self.__get_import_path_file_tree(split_path, split_index+1, file_leaf, file_pattern)

    def __handle_dynamic_path_part(self, split_path: List[str], split_index: int, file_tree: Dict[str, Any], file_pattern: str) -> None:
        file_part: str = list(file_tree['__dynamic_files'])[0]
        self.__append_import_path(file_part)
        if '.py' not in file_part and split_index+1 == len(split_path):  # pragma: no cover
            index_file: str = file_pattern.replace('*', file_part) if '*' in file_pattern else self.__init_file
            self.__append_import_path(index_file)
        file_leaf: Dict[str, Any] = self.__determine_which_file_leaf(file_tree, file_part)
        self.has_dynamic_route = True
        self.dynamic_parts[split_index] = split_path[split_index]
        self.__get_import_path_file_tree(split_path, split_index+1, file_leaf, file_pattern)

    def __append_import_path(self, path_part: str) -> None:
        if self.file_tree_climbed:
            self.import_path.append(path_part)

    def __determine_which_file_leaf(self, file_tree: Dict[str, Any], file_branch: str) -> Dict[str, Any]:
        if file_tree.get(file_branch) and file_tree[file_branch] != '*':
            self.file_tree_climbed = True
            return file_tree[file_branch]
        self.file_tree_climbed = False
        return file_tree

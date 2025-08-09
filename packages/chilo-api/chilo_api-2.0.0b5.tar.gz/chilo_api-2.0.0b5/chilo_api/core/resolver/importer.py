import importlib.util
import glob
import os
from typing import Any, Dict, List, Set
from types import ModuleType


class ResolverImporter:
    '''
    A class to handle the importing of API endpoint handler files.
    This class provides methods to load handler files, clean paths, and retrieve modules based on request paths.
    Attributes
    ----------
    handlers: str
        The glob pattern location of the handler files eligible for being a handler.
    handlers_tree: Dict[str, Any]
        A dictionary representing the file tree structure of the handler files.
    Methods
    ----------
    get_imported_module_from_file(file_path: str, import_path: str) -> ModuleType:
        Imports a module from the specified file path and import path.
    file_separator: str
        The file separator used in the file paths.
    handlers: str
        The glob pattern location of the handler files.
    clean_path(dirty_path: str) -> str:
        Cleans the provided path by stripping unnecessary characters.
    get_file_list() -> List[str]:
        Retrieves a list of all handler files matching the glob pattern.
    get_handlers_file_tree() -> Dict[str, Any]:
        Builds and returns the file tree structure of the handler files.
    '''

    def __init__(self, **kwargs: Any) -> None:
        self.__handlers: str = self.clean_path(kwargs.get('handlers', ''))
        self.__handlers_tree: Dict[str, Any] = {}

    @staticmethod
    def get_imported_module_from_file(file_path: str, import_path: str) -> ModuleType:
        spec = importlib.util.spec_from_file_location(import_path, file_path)
        if spec is None or spec.loader is None:
            raise ImportError(f"Cannot load spec for {import_path} from {file_path}")  # pragma: no cover
        handler_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(handler_module)
        return handler_module

    @property
    def file_separator(self) -> str:
        return os.sep

    @property
    def handlers(self) -> str:
        return self.__handlers

    def clean_path(self, dirty_path: str) -> str:
        return dirty_path.strip(self.file_separator)

    def get_file_list(self) -> List[str]:
        glob_pattern: str = self.__get_glob_pattern()
        file_list: List[str] = glob.glob(glob_pattern, recursive=True)
        return [item.replace(self.__get_handlers_root(), '') for item in file_list]

    def get_handlers_file_tree(self) -> Dict[str, Any]:
        if not self.__handlers_tree:
            file_list: List[str] = self.get_file_list()
            if len(file_list) == 0:
                raise RuntimeError(
                    f'no files found in handler path {self.__get_glob_pattern()}; please make sure all spelling and spacing are correct'
                )
            for file_path in file_list:
                sections: List[str] = file_path.split(self.file_separator)
                sections = [section for section in sections if section]
                self.__recurse_section(self.__handlers_tree, sections, 0)
        return self.__handlers_tree

    def __get_glob_pattern(self) -> str:
        if '*' in self.__handlers and '.py' in self.__handlers:
            return self.handlers
        return self.handlers + self.file_separator + '**' + self.file_separator + '*.py'

    def __get_handlers_root(self) -> str:
        if '*' in self.__handlers and '.py' in self.__handlers:
            sep_split: List[str] = self.handlers.split(self.file_separator)
            cleaned_split: List[str] = [directory for directory in sep_split if self.__is_directory(directory)]
            return self.clean_path(f'{self.file_separator}'.join(cleaned_split))
        return self.handlers

    def __is_directory(self, directory: str) -> bool:
        if '*' not in directory and '.py' not in directory:
            return True
        return False

    def __recurse_section(self, file_leaf: Dict[str, Any], sections: List[str], index: int) -> None:
        if index >= len(sections):
            return
        section: str = sections[index]
        if not section:  # pragma: no cover
            self.__recurse_section(file_leaf, sections, index + 1)
        if section not in file_leaf:
            file_leaf[section] = {} if index + 1 < len(sections) else '*'
        if isinstance(file_leaf, dict) and '__dynamic_files' not in file_leaf:
            file_leaf['__dynamic_files'] = set()
        if section.startswith('_') and not section.startswith('__'):
            file_leaf['__dynamic_files'].add(section)
        self.__check_multiple_dynamic_files(file_leaf, sections)
        self.__check_file_and_directory_share_name(file_leaf, section, sections)
        self.__recurse_section(file_leaf[section], sections, index + 1)

    def __check_multiple_dynamic_files(self, file_leaf: Dict[str, Any], sections: List[str]) -> None:
        dynamic_files: Set[str] = file_leaf['__dynamic_files']
        if len(dynamic_files) > 1:
            files: str = ', '.join(list(dynamic_files))
            sections.pop()
            location: str = f'{self.file_separator}'.join(sections)
            raise RuntimeError(f'Cannot have two dynamic files in the same directory. Files: {files}, Location: {location}')

    def __check_file_and_directory_share_name(self, file_leaf: Dict[str, Any], section: str, sections: List[str]) -> None:
        opposite_type: str = section.replace('.py', '') if '.py' in section else f'{section}.py'
        if opposite_type in file_leaf:
            location: str = f'{self.file_separator}'.join(sections)
            raise RuntimeError(f'Cannot have file and directory share same name. Files: {section}, Location: {location}')

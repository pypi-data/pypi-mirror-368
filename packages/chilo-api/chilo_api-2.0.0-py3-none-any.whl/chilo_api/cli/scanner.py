import glob
import os
from typing import List, Optional


class CLIScanner:
    '''
    Scans for handler files in the specified directory.
    This class provides methods to retrieve handler file paths and glob patterns.
    Attributes
    ----------
    handlers: str
        glob pattern location of the handler files eligible for being a handler
    file_separator: str
        the file separator used in the operating system (e.g., '/' for Unix, '\' for Windows)
    handlers_base: str
        base path of the handler files, cleaned of leading and trailing separators
    Methods
    ----------
    get_handler_file_paths():
        Returns a list of handler file paths based on the glob pattern.
    get_handler_glob_pattern(handlers_base):
        Returns the glob pattern for handler files based on the handlers base path.
    get_generated_glob_pattern(protobuf_base):
        Returns the glob pattern for generated protobuf files based on the protobuf base path.
    get_gprc_handers(handlers_base):
        Returns a list of gRPC handler files based on the handlers base path.
    clean_path(dirty_path):
        Cleans the given path by stripping leading and trailing file separators.
    '''

    def __init__(self, handlers: Optional[str] = None) -> None:
        if handlers is None:
            raise RuntimeError('handlers parameter is required')
        self.__handlers: str = self.clean_path(handlers)

    @property
    def file_separator(self) -> str:
        return os.sep

    @property
    def handlers(self) -> str:
        return self.__handlers

    @property
    def handlers_base(self) -> str:
        return self.clean_path(self.__handlers.split('*')[0])

    def clean_path(self, dirty_path: str) -> str:
        return dirty_path.strip(self.file_separator)

    def get_handler_file_paths(self) -> List[str]:
        glob_pattern = self.__get_glob_pattern()
        return self.__glob_glob(glob_pattern)

    def get_handler_glob_pattern(self, handlers_base: str) -> str:
        if '*' in handlers_base and '.py' in handlers_base:
            return handlers_base
        return handlers_base + os.sep + '**' + os.sep + '*.py'

    def get_generated_glob_pattern(self, protobuf_base: str) -> str:
        return protobuf_base + os.sep + '**' + os.sep + '*_pb2*.py'

    def get_gprc_handers(self, handlers_base: str) -> List[str]:
        handler_pattern = self.get_handler_glob_pattern(handlers_base)
        return self.__glob_glob(handler_pattern)

    def __get_glob_pattern(self) -> str:
        if '*' in self.__handlers and '.py' in self.__handlers:
            return self.handlers
        return self.handlers + self.file_separator + '**' + self.file_separator + '*.py'

    def __glob_glob(self, pattern: str) -> List[str]:
        return glob.glob(pattern, recursive=True)

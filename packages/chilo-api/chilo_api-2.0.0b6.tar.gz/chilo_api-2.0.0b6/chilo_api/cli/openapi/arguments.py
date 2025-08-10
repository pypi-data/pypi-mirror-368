from typing import Any, List
from argparse import Namespace


class OpenAPIArguments:
    '''
    A class to handle and validate command-line arguments for the OpenAPI generator.
    This class provides methods to parse command line arguments and set up the OpenAPI generation configuration.
    Attributes
    ----------
    base: str
        The base path for the OpenAPI documentation.
    handlers: str
        The directory containing handler modules for the OpenAPI documentation.
    output: str
        The directory where the OpenAPI documentation will be saved.
    formats: list
        The formats in which the OpenAPI documentation will be generated (e.g., 'yml', 'json').
    delete: bool
        Whether to delete unused paths and methods in the OpenAPI documentation.
    '''

    def __init__(self, api: Any, args: Namespace) -> None:
        self.__base: str = api.base_path
        self.__handlers: str = api.handlers
        self.__output: str = args.output or api.handlers
        self.__formats: str = args.format or 'yml'
        self.__delete: bool = args.delete or False

    @property
    def base(self) -> str:
        return self.__base

    @property
    def handlers(self) -> str:
        return self.__handlers

    @property
    def output(self) -> str:
        return self.__output

    @property
    def formats(self) -> List[str]:
        return self.__formats.split(',')

    @property
    def delete(self) -> bool:
        return self.__delete

import os
from typing import Union, Any
from argparse import Namespace


class CLIValidator:
    '''
    Validates CLI arguments for the Chilo API.
    This class checks if the provided server port is within the valid range
    and if the output directory exists.
    Methods
    ----------
    validate_server(server):
        Validates the server port, ensuring it is between 0 and 9999.
    validate_arguments(input_args):
        Validates the input arguments, specifically checking if the output directory exists.
    '''

    def validate_server(self, server: Union[Namespace, Any]) -> None:
        if not 0 <= server.port <= 9999:
            raise RuntimeError(f'port {server.port} is not between well known ports 0 - 9999')

    def validate_arguments(self, input_args: Union[Namespace, Any]) -> None:
        self.__check_directory(input_args.output)

    def __check_directory(self, possible_dir: str) -> None:
        if not os.path.exists(possible_dir):
            raise RuntimeError(f'{possible_dir} is not a valid directory path')

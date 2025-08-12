import pathlib
import subprocess

from chilo_api.core.types.server_settings import ServerSettings
from chilo_api.core.grpc.endpoint import GRPCEndpoint


class CLICommander:
    '''
    A class to handle grpc code generation commands.
    This class provides methods to generate gRPC code for endpoints based on the server configuration.
    Methods
    ----------
    generate_grpc_code(endpoint, server):
        Generates gRPC code for the specified endpoint using the server's protobufs directory.
    '''

    @staticmethod
    def generate_grpc_code(endpoint: GRPCEndpoint, server: ServerSettings) -> None:

        generated: str = f'{server.protobufs}/generated'
        path: pathlib.Path = pathlib.Path(generated)
        file: str = f'{server.protobufs}/{endpoint.protobuf}'
        command: list[str] = ['python', '-m', 'grpc_tools.protoc']
        args: str = f'-I{generated}={server.protobufs} --python_out=. --pyi_out=. --grpc_python_out=. {file}'
        command.extend(args.split())
        path.mkdir(parents=True, exist_ok=True)

        try:
            subprocess.run(command, capture_output=True, text=True, check=True)
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f'Error generating gRPC code for {endpoint.name}: {e.stderr.strip()}') from e
        except Exception as e:  # pragma: no cover
            raise RuntimeError(f'Unexpected error generating gRPC code for {endpoint.name}: {str(e)}') from e

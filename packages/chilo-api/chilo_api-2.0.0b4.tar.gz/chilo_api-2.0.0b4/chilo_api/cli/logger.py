from typing import Optional
from art import tprint

from chilo_api.core.types.server_settings import ServerSettings


class CLILogger:  # pragma: no cover
    '''
    Logger for the CLI application.
    This class provides methods to log messages, banners, and server settings.
    It uses the `art` library to print ASCII art logos and banners.
    Methods
    ----------
    log_logo(font='medium'):
        Prints the Chilo logo in the specified font style.
    log_banner_message(message):
        Prints a banner message with the specified text.
    log_subheader_message(message=''):
        Prints a subheader message with the specified text.
    log_message(message):
        Prints a regular message with the specified text.
    log_server_start():
        Logs the start of the server with a banner and logo.
    log_openapi_generation_start():
        Logs the start of OpenAPI generation with a banner and logo.
    log_server_settings(server):
        Logs the server settings including API type, host, port, reload status, verbose mode,
        timeout, and OpenAPI validation settings.
    log_end(message=None):
        Logs the end of the process with a banner and logo, optionally with a custom message.
    '''

    def log_logo(self, font: str = 'medium') -> None:
        tprint('CHILO', font=font)

    def log_banner_message(self, message: Optional[str] = None) -> None:
        print(f'=========== {message} ===========')

    def log_subheader_message(self, message: str = '') -> None:
        print(f'|---------------------{message}---------------------|')

    def log_message(self, message: str) -> None:
        print(f'| {message}')

    def log_server_start(self) -> None:
        self.log_banner_message('SERVER STARTING')
        self.log_logo()

    def log_openapi_generation_start(self) -> None:
        self.log_banner_message('GENERATING')
        self.log_logo()

    def log_server_settings(self, server: ServerSettings) -> None:
        self.log_subheader_message('SETTINGS')
        self.log_message(f'API TYPE: {server.api_type}')
        self.log_message(f'HOST: {server.host} (from {server.source["host"]})')
        self.log_message(f'PORT: {server.port} (from {server.source["port"]})')
        self.log_message(f'RELOAD: {server.reload} (from {server.source["reload"]})')
        self.log_message(f'VERBOSE: {server.verbose} (from {server.source["verbose"]})')
        self.log_message(f'TIMEOUT: {server.timeout}')
        if server.api_type == 'rest':
            self.log_message(f'OPENAPI REQUEST VALIDATION: {"Enabled" if server.openapi_validate_request else "Disabled"}')
            self.log_message(f'OPENAPI RESPONSE VALIDATION: {"Enabled" if server.openapi_validate_response else "Disabled"}')
        if server.api_type == 'grpc':
            self.log_message(f'PROTOBUF PATH: {server.protobufs}')
            statsu = 'Enabled' if server.enable_reflection else 'Disabled'
            self.log_message(f'REFLECTION: {statsu} (from {server.source.get("enable_reflection", "default")})')
        self.log_subheader_message('--------')

    def log_end(self, message: Optional[str] = None) -> None:
        self.log_banner_message(message)
        self.log_logo(font='small')
        self.log_message('Thank you for using Chilo! Goodbye!')

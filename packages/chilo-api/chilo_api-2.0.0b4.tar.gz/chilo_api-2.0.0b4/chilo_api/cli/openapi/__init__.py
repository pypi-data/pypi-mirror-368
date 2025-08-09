from typing import Any, List
from argparse import Namespace

from chilo_api.cli.scanner import CLIScanner
from chilo_api.cli.openapi.arguments import OpenAPIArguments
from chilo_api.cli.validator import CLIValidator
from chilo_api.cli.openapi.generator import OpenAPIGenerator
from chilo_api.cli.openapi.file_writer import OpenAPIFileWriter
from chilo_api.cli.openapi.module import OpenAPIHandlerModule
from chilo_api.cli.importer import CLIImporter
from chilo_api.cli.logger import CLILogger


class OpenAPI:
    '''
    A class to generate OpenAPI documentation for a FastAPI application.
    This class provides methods to handle command line arguments, generate OpenAPI documentation,
    and write the documentation to files in specified formats.
    Methods
    ----------
    generate():
        Parses command line arguments and generates OpenAPI documentation based on the provided API.
        Writes the generated documentation to files in the specified formats (JSON, YAML).
    '''

    def __init__(self, args: Namespace) -> None:
        self.args: Namespace = args
        self.logger: CLILogger = CLILogger()
        self.importer: CLIImporter = CLIImporter()
        self.inputs: OpenAPIArguments = self.__get_input_arguments()
        self.generator: OpenAPIGenerator = OpenAPIGenerator(self.inputs.output)
        self.writer: OpenAPIFileWriter = OpenAPIFileWriter()
        self.validator: CLIValidator = CLIValidator()

    def generate(self) -> None:
        self.logger.log_openapi_generation_start()
        self.validator.validate_arguments(self.inputs)
        self.__generate_openapi_doc()
        self.__write_openapi_file()
        self.logger.log_message('OpenAPI documentation generation completed successfully.')
        self.logger.log_end('FINISHED')

    def __get_input_arguments(self) -> OpenAPIArguments:
        api: Any = self.importer.get_api_module(self.args.api)
        self.logger.log_message(f'Scanning handlers: {api.handlers}...')
        return OpenAPIArguments(api, self.args)

    def __generate_openapi_doc(self) -> None:
        modules: List[OpenAPIHandlerModule] = self.__get_modules_from_handlers()
        for module in modules:
            self.generator.add_path_and_method(module)
        if self.inputs.delete:
            self.logger.log_message('Deleting paths and methods not found in code base...')
            self.generator.delete_unused_paths()

    def __get_modules_from_handlers(self) -> List[OpenAPIHandlerModule]:
        self.logger.log_message('Importing handler endpoint modules...')
        scanner: CLIScanner = CLIScanner(self.inputs.handlers)
        file_paths: List[str] = scanner.get_handler_file_paths()
        return self.importer.get_handler_modules_from_file_paths(file_paths, scanner.handlers_base, self.inputs.base)

    def __write_openapi_file(self) -> None:
        self.logger.log_message(f'Writing OpenAPI documentation to: {self.inputs.output}')
        self.writer.write_openapi(self.generator.doc, self.inputs.output, self.inputs.formats)

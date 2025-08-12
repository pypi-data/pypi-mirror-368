from concurrent import futures
from typing import List, Dict, Any, Optional, Type, Callable
import grpc
from grpc_reflection.v1alpha import reflection

from chilo_api.cli.commander import CLICommander
from chilo_api.core.grpc.endpoint import GRPCEndpoint
from chilo_api.cli.importer import CLIImporter
from chilo_api.cli.server.proto_parser import GRPCProtoParser  # type: ignore
from chilo_api.cli.scanner import CLIScanner
from chilo_api.cli.logger import CLILogger
from chilo_api.core.types.server_settings import ServerSettings
from chilo_api.core.grpc.mediator import GRPCMediator


class GRPCServer:
    '''
    A class to handle the gRPC server operations.
    This class is responsible for initializing the server, generating gRPC code for endpoints,
    pairing generated code to endpoints, assigning gRPC classes to endpoints, and adding them to the server.
    Attributes
    ----------
    server_args: ServerArgsProtocol
        The arguments for the server, including port and protobufs directory.
    logger: LoggerProtocol
        The logger instance for logging messages.
    Methods
    ----------
    run():
        Starts the gRPC server and listens for incoming requests.
    '''

    def __init__(self, server_args: ServerSettings, logger: CLILogger) -> None:
        self.server_args: ServerSettings = server_args
        self.importer: CLIImporter = CLIImporter()
        self.scanner: CLIScanner = CLIScanner(server_args.handlers)
        self.__dynamic_servers: Dict[str, Type[Any]] = {}
        self.__existing_methods: Dict[str, str] = {}
        self.logger = logger

    def run(self) -> None:
        server: grpc.Server = grpc.server(futures.ThreadPoolExecutor(max_workers=self.server_args.max_workers))
        endpoints: List[GRPCEndpoint] = self.__get_endpoints_from_server()
        self.__generate_grpc_code_from_endpoints(endpoints)
        self.__pair_generated_code_to_endpoints(endpoints)
        self.__assign_grpc_classes_to_endpoints(endpoints)
        self.__assign_grpc_server_methods(endpoints)
        self.__add_to_server(server, endpoints)
        self.__enable_server_reflection(server)
        self.__add_port_to_server(server)
        self.__run_server(server)

    def __get_endpoints_from_server(self) -> List[GRPCEndpoint]:
        handlers: List[str] = self.scanner.get_gprc_handers(self.server_args.handlers)
        modules: List[Any] = self.importer.get_imported_modules(handlers)
        if not modules:
            raise RuntimeError(f'No gRPC handlers found in the specified directory: {self.server_args.handlers}.')
        endpoints: List[GRPCEndpoint] = []
        for module in modules:
            endpoint_list: List[GRPCEndpoint] = GRPCEndpoint.get_endpoints_from_module(module)
            endpoints.append(endpoint_list)  # type: ignore
        # Flatten the list of lists into a single list
        flat_endpoints: List[GRPCEndpoint] = [ep for sublist in endpoints for ep in sublist]  # type: ignore

        if not flat_endpoints:
            raise RuntimeError('No gRPC endpoint methods found in the provided modules.')
        return flat_endpoints

    def __generate_grpc_code_from_endpoints(self, endpoints: List[GRPCEndpoint]) -> None:
        for endpoint in endpoints:
            CLICommander.generate_grpc_code(endpoint, self.server_args)

    def __pair_generated_code_to_endpoints(self, endpoints: List[GRPCEndpoint]) -> None:
        parser: GRPCProtoParser = GRPCProtoParser()
        for endpoint in endpoints:
            parsed = parser.parse_proto_file(self.server_args, endpoint)  # type: ignore
            servicer_file_name: str = self.__get_servicer_file_name_from_proto(parsed.statements)  # type: ignore
            protobufs_path: str = self.server_args.protobufs if self.server_args.protobufs is not None else ''
            servicer_class: Optional[Type[Any]] = self.importer.get_imported_servicer_class(protobufs_path, servicer_file_name)
            response_is_stream: bool = self.__determine_if_stream(parsed.statements, endpoint)  # type: ignore
            if servicer_class is not None and servicer_class.__name__ == endpoint.servicer_class_name:
                endpoint.response_is_stream = response_is_stream
                endpoint.servicer = servicer_class
                rpc_response_name = self.__get_response_class_name_from_proto(parsed.statements)
                if rpc_response_name is None:
                    continue  # pragma: no cover
                endpoint.rpc_response_name = rpc_response_name
                endpoint.rpc_response = self.importer.get_imported_response_class(protobufs_path, servicer_file_name, rpc_response_name)

    def __get_servicer_file_name_from_proto(self, statements: List[Any]) -> Optional[str]:
        for statement in statements:
            if hasattr(statement, 'identifier'):
                return statement.identifier[0]
        return None  # pragma: no cover

    def __determine_if_stream(self, statements: List[Any], endpoint) -> bool:
        for statement in statements:
            if hasattr(statement, 'body') and len(statement.body) > 0:
                if self.__method_has_stream_response(statement.body, endpoint.rpc_request_name):
                    return True
        return False

    def __method_has_stream_response(self, methods: List[Any], rpc_request_name: str) -> bool:
        for method in methods:
            if hasattr(method, 'name') and method.name == rpc_request_name:
                if hasattr(method, 'response_stream') and method.response_stream:
                    return True
        return False

    def __get_response_class_name_from_proto(self, statements: List[Any]) -> Optional[str]:
        for statement in statements:
            if hasattr(statement, 'body'):
                for return_statement in statement.body:
                    if hasattr(return_statement, 'response_message_type'):
                        return return_statement.response_message_type
        return None  # pragma: no cover

    def __assign_grpc_classes_to_endpoints(self, endpoints: List[GRPCEndpoint]) -> None:
        for endpoint in endpoints:
            mediator: GRPCMediator = GRPCMediator(self.server_args.api_config, endpoint)
            if endpoint.servicer_class_name not in self.__dynamic_servers:
                self.__setup_new_dynamic_server(mediator, endpoint)
            else:
                self.__setup_existing_dynamic_server(mediator, endpoint)
            self.__existing_methods[endpoint.name] = endpoint.rpc_request_method.__name__
            endpoint.dynamic_servicer = self.__dynamic_servers[endpoint.servicer_class_name]

    def __setup_new_dynamic_server(self, mediator: GRPCMediator, endpoint: GRPCEndpoint) -> None:
        methods: Dict[str, Callable[..., Any]] = {}
        try:
            methods[endpoint.rpc_request_name] = mediator.get_endpoint_request_method()
            self.__dynamic_servers[endpoint.servicer_class_name] = type(endpoint.servicer_class_name, (endpoint.servicer,), methods)  # type: ignore
        except Exception as e:
            if 'metaclass conflict' in str(e):
                raise RuntimeError(f'No matching servicer class found for {endpoint.servicer_class_name}. {str(e).capitalize()}') from e
            raise RuntimeError(f'Unknown error while setting up dynamic server for {endpoint.servicer_class_name}: {str(e)}') from e

    def __setup_existing_dynamic_server(self, mediator: GRPCMediator, endpoint: GRPCEndpoint) -> None:
        if endpoint.name in self.__existing_methods:
            existing: str = self.__existing_methods[endpoint.name]
            raise RuntimeError(f'Cannot add {endpoint.rpc_request_method.__name__} -> {endpoint.name}. Method already exists: {existing}.')
        setattr(self.__dynamic_servers[endpoint.servicer_class_name], endpoint.rpc_request_name, mediator.get_endpoint_request_method())

    def __assign_grpc_server_methods(self, endpoints: List[GRPCEndpoint]) -> None:
        for endpoint in endpoints:
            protobufs_path: str = self.server_args.protobufs if self.server_args.protobufs is not None else ''
            endpoint.add_server_method = self.importer.get_add_server_method(protobufs_path, endpoint.service)

    def __add_to_server(self, server: grpc.Server, endpoints: List[GRPCEndpoint]) -> None:
        for endpoint in endpoints:
            if endpoint.servicer is not None and endpoint.add_server_method is not None:
                endpoint.add_server_method(endpoint.dynamic_servicer(), server)  # type: ignore

    def __get_service_names_for_reflection(self) -> tuple:
        service_names = set()
        service_names.add(reflection.SERVICE_NAME)
        for endpoint in self.__get_unique_services():
            try:
                protobufs_path = self.server_args.protobufs if self.server_args.protobufs is not None else ''
                pb2_module = self.importer.get_imported_pb2_module(protobufs_path, endpoint.service)
                if pb2_module and hasattr(pb2_module, 'DESCRIPTOR'):
                    for _, service_descriptor in pb2_module.DESCRIPTOR.services_by_name.items():
                        service_names.add(service_descriptor.full_name)
            except Exception as e:  # pragma: no cover
                self.logger.log_message(f'Warning: Could not add reflection for service {endpoint.service}: {e}')
                continue
        return tuple(service_names)

    def __get_unique_services(self) -> List[GRPCEndpoint]:
        unique_services = {}
        for servicer_class_name in self.__dynamic_servers.keys():
            for endpoint_name, _ in self.__existing_methods.items():
                service_name = endpoint_name.split('.')[0]
                if f'{service_name}Servicer' == servicer_class_name:
                    if service_name not in unique_services:
                        endpoint = GRPCEndpoint(
                            service=service_name,
                            requirements={},
                            protobuf='',
                            rpc_request_name='',
                            rpc_request_method=lambda: None
                        )
                        unique_services[service_name] = endpoint
                    break
        return list(unique_services.values())

    def __enable_server_reflection(self, server: grpc.Server) -> None:
        if not self.server_args.reflection:
            return  # pragma: no cover
        service_names = self.__get_service_names_for_reflection()
        if service_names:
            reflection.enable_server_reflection(service_names, server)

    def __add_port_to_server(self, server: grpc.Server) -> None:
        if self.server_args.private_key is not None and self.server_args.certificate is not None:
            with open(self.server_args.private_key, 'rb') as server_key_file:
                private_key = server_key_file.read()
            with open(self.server_args.certificate, 'rb') as server_cert_file:
                certificate = server_cert_file.read()
            server_credentials = grpc.ssl_server_credentials([(private_key, certificate)])
            server.add_secure_port(f'[::]:{self.server_args.port}', server_credentials)
        else:
            server.add_insecure_port(f'[::]:{self.server_args.port}')

    def __run_server(self, server: grpc.Server) -> None:
        try:
            server.start()
            server.wait_for_termination()
        except KeyboardInterrupt:
            server.stop(grace=3)
            self.logger.log_message('Server stopped by user.')
        except Exception as e:
            server.stop(grace=0)
            self.logger.log_message(f'An error occurred while running the gRPC server: {e}')

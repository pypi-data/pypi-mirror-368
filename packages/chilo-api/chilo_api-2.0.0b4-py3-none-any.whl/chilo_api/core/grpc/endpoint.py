import json
from typing import Any, Dict, List, Optional, Callable, Union, Generator
from types import ModuleType


class GRPCEndpoint:
    '''
    A class to represent a gRPC endpoint.
    This class encapsulates the logic for handling requests to a specific gRPC endpoint, including method execution and response handling.
    Attributes
    ----------
    service: str
        The name of the gRPC service this endpoint belongs to.
    servicer: Optional[Any]
        The servicer class that implements the gRPC service logic.
    dynamic_servicer: Optional[Any]
        A dynamic servicer class that can be used for runtime modifications or extensions.
    requirements: Dict[str, Any]
        The requirements for the endpoint, such as authentication and required responses.
    protobuf: str
        The protobuf definition associated with the endpoint.
    rpc_request_name: str
        The name of the RPC request method.
    rpc_request_method: Callable[[Any, Any], Any]
        The method that handles the RPC request logic.
    requirements: Dict[str, Any]
        The requirements for the endpoint, such as authentication and required responses.
    has_requirements: bool
        Indicates whether the endpoint has any specific requirements.
    requires_auth: Optional[bool]
        Indicates whether authentication is required for this endpoint.
    rpc_response_name: Optional[str]
        The name of the RPC response method, if applicable.
    rpc_response: Optional[Any]
        The class that represents the RPC response.
    response_is_stream: bool
        Indicates whether the response is a stream.
    add_server_method: Optional[Callable[..., Any]]
        A method to add the endpoint to a gRPC server.
    '''

    def __init__(self, **kwargs: Any) -> None:
        self.__service: str = kwargs['service']
        self.__servicer: Optional[Any] = None
        self.__dynamic_servicer: Optional[Any] = None
        self.__requirements: Dict[str, Any] = kwargs['requirements']
        self.__protobuf: str = kwargs['protobuf']
        self.__rpc_request_name: str = kwargs['rpc_request_name']
        self.__rpc_request_method: Callable[[Any, Any], Any] = kwargs['rpc_request_method']
        self.__response_is_stream: bool = False
        self.__rpc_response_name: Optional[str] = ''
        self.__rpc_response: Optional[Any] = None
        self.__add_server_method: Optional[Callable[..., Any]] = None

    @classmethod
    def get_endpoints_from_module(cls, module: ModuleType) -> List['GRPCEndpoint']:
        endpoints: List['GRPCEndpoint'] = []
        funcs: List[str] = [function for function in dir(module) if function]
        for func in funcs:
            rpc_method: Any = getattr(module, func)
            requirements: Dict[str, Any] = getattr(rpc_method, 'requirements', {})
            if requirements.get('protobuf') and requirements.get('service') and requirements.get('rpc'):
                endpoint: 'GRPCEndpoint' = cls(
                    rpc_request_method=rpc_method,
                    protobuf=requirements['protobuf'],
                    service=requirements['service'],
                    rpc_request_name=requirements['rpc'],
                    requirements=requirements
                )
                endpoints.append(endpoint)
        return endpoints

    @property
    def service(self) -> str:
        return self.__service

    @property
    def servicer_class_name(self) -> str:
        return f'{self.service}Servicer'

    @property
    def servicer(self) -> Optional[Any]:
        return self.__servicer

    @servicer.setter
    def servicer(self, servicer: Any) -> None:
        self.__servicer = servicer

    @property
    def name(self) -> str:
        return f'{self.service}.{self.rpc_request_name}'

    @property
    def protobuf(self) -> str:
        return self.__protobuf

    @property
    def requirements(self) -> Dict[str, Any]:
        return self.__requirements

    @property
    def has_requirements(self) -> bool:
        return bool(self.__requirements)

    @property
    def requires_auth(self) -> Optional[bool]:
        return self.__requirements.get('auth_required')

    @property
    def rpc_request_name(self) -> str:
        return self.__rpc_request_name

    @property
    def rpc_response_name(self) -> Optional[str]:
        return self.__rpc_response_name

    @rpc_response_name.setter
    def rpc_response_name(self, rpc_response_name: str) -> None:
        self.__rpc_response_name = rpc_response_name

    @property
    def rpc_response(self) -> Optional[Any]:
        return self.__rpc_response

    @rpc_response.setter
    def rpc_response(self, rpc_response: Any) -> None:
        self.__rpc_response = rpc_response

    @property
    def dynamic_servicer(self) -> Optional[Any]:
        return self.__dynamic_servicer

    @dynamic_servicer.setter
    def dynamic_servicer(self, dynamic_servicer: Any) -> None:
        self.__dynamic_servicer = dynamic_servicer

    @property
    def add_server_method(self) -> Optional[Callable[..., Any]]:
        return self.__add_server_method

    @add_server_method.setter
    def add_server_method(self, add_server_method: Callable[..., Any]) -> None:
        self.__add_server_method = add_server_method

    @property
    def response_is_stream(self) -> bool:
        return self.__response_is_stream

    @response_is_stream.setter
    def response_is_stream(self, response_is_stream: bool) -> None:
        self.__response_is_stream = response_is_stream

    @property
    def rpc_request_method(self) -> Callable[[Any, Any], Union[Any, Generator[Any, None, Any]]]:
        return self.__rpc_request_method

    def run(self, request: Any, response: Any) -> Any:
        self.rpc_request_method(request, response)
        return response.get_response()

    def stream(self, request: Any, response: Any) -> Generator[Any, None, None]:
        yield from self.rpc_request_method(request, response)

    def __str__(self) -> str:
        return json.dumps({
            'service': self.service,
            'servicer_class_name': self.servicer_class_name,
            'servicer': str(type(self.servicer)),
            'dynamic_servicer': str(type(self.dynamic_servicer)),
            'add_server_method': str(type(self.add_server_method)),
            'rpc_request_name': self.rpc_request_name,
            'rpc_request_method': str(type(self.rpc_request_method)),
            'rpc_response_name': self.rpc_response_name,
            'rpc_response': str(type(self.rpc_response)),
            'requirements': self.requirements,
            'protobuf': self.protobuf
        })

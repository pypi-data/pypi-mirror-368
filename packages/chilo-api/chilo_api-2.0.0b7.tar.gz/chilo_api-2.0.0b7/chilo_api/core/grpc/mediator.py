from typing import Any, Dict, Generator, Tuple, Callable, Union

from chilo_api.core.executor import Executor
from chilo_api.core.grpc.endpoint import GRPCEndpoint
from chilo_api.core.grpc.pipeline import GRPCPipeline
from chilo_api.core.grpc.request import GRPCRequest
from chilo_api.core.grpc.response import GRPCResponse
from chilo_api.core.placeholders.resolver import ResolverPlaceholder
from chilo_api.core.router import Router


class GRPCMediator:

    def __init__(self, api_config: Router, endpoint: GRPCEndpoint) -> None:
        executor_kwargs: Dict[str, Any] = {**{'is_grpc': True, 'grpc_endpoint': endpoint}, **api_config.__dict__}
        self.executor: Executor = Executor(GRPCPipeline(**api_config.__dict__), ResolverPlaceholder(), **executor_kwargs)
        self.endpoint: GRPCEndpoint = endpoint

    def get_endpoint_request_method(self) -> Callable[[Any, Any], Union[Any, Generator[Any, None, Any]]]:
        if self.endpoint.response_is_stream:
            return self.execute_endpoint_request_stream
        return self.execute_endpoint_request_method

    def execute_endpoint_request_method(self, rpc_request: Any, context: Any) -> Any:
        request, response = self.__get_request_response(rpc_request, context)
        return self.executor.run(request, response)

    def execute_endpoint_request_stream(self, stream_request: Any, context: Any) -> Generator[Any, None, Any]:
        request, response = self.__get_request_response(stream_request, context)
        yield from self.executor.stream(request, response)

    def __get_request_response(self, request: Any, context: Any) -> Tuple[GRPCRequest, GRPCResponse]:
        grpc_request: GRPCRequest = GRPCRequest(request, context)
        grpc_response: GRPCResponse = GRPCResponse(rpc_response=self.endpoint.rpc_response, context=context)
        return grpc_request, grpc_response

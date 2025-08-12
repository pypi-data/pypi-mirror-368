from typing import Any
from google.protobuf.json_format import MessageToDict

from chilo_api.core.interfaces.request import RequestInterface


class GRPCRequest(RequestInterface):
    '''
    A class to represent a gRPC request.
    Attributes
    ----------
    api_type: str
        The type of API, such as 'rest' or 'grpc'
    body: Any
        The request body in its dict format
    raw: Any
        The raw request data as sent by the client
    context: Any
        The gRPC context for the request, used for metadata and other gRPC-specific features
    '''

    def __init__(self, rpc_request, context) -> None:
        super().__init__()
        self.__rpc_request = rpc_request
        self._context = context

    @property
    def api_type(self) -> str:
        return 'grpc'

    @property
    def body(self) -> Any:
        try:
            return self.protobuf
        except Exception:
            return self.raw

    @property
    def raw(self) -> Any:
        return self.__rpc_request

    def _as_dict(self) -> Any:
        return MessageToDict(self.__rpc_request, preserving_proto_field_name=True)

    @property
    def json(self) -> Any:
        return self._as_dict()

    @property
    def protobuf(self) -> Any:
        return self._as_dict()

    @property
    def context(self) -> Any:
        return self._context

    @context.setter
    def context(self, context: Any) -> None:
        pass  # Context is managed by gRPC and does not require setting in this normalizer NOSONAR

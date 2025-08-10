from typing import Any, Callable, Type, Optional

import grpc

from chilo_api.core.interfaces.response import ResponseInterface


class GRPCResponse(ResponseInterface):
    '''
    A class to represent a gRPC response.
    Attributes
    ----------
    body: Any
        The return body of the response in its original format
    code: int
        Status code to be returned to requester
    grpc_code: grpc.StatusCode
        gRPC status code corresponding to the HTTP status code
    context: Any
        gRPC context for response handling
    has_errors: bool
        Determines if the response contains errors
    rpc_response: Any
        The gRPC response object to be returned
    Methods
    ----------
    set_error(key_path: str, message: str):
        Sets an error in the response with a consistent format
    get_response() -> Any:
        Returns the gRPC response object, setting the context code and details if there are errors.
        This method is used to finalize the response before sending it back to the client.
        It checks if there are errors or if the body is None, returning an empty response in those cases.
        Otherwise, it returns the gRPC response with the body data.
    '''

    def __init__(self, **kwargs) -> None:
        super().__init__()
        self.__rpc_response: Type[Any] = kwargs['rpc_response']
        self.__context: Optional[Any] = kwargs.get('context')
        self.__http_grpc_code_mapping: dict[int, grpc.StatusCode] = {
            200: grpc.StatusCode.OK,
            400: grpc.StatusCode.INVALID_ARGUMENT,
            401: grpc.StatusCode.UNAUTHENTICATED,
            404: grpc.StatusCode.NOT_FOUND,
            408: grpc.StatusCode.DEADLINE_EXCEEDED,
            429: grpc.StatusCode.RESOURCE_EXHAUSTED,
            403: grpc.StatusCode.PERMISSION_DENIED,
            500: grpc.StatusCode.INTERNAL,
            501: grpc.StatusCode.UNIMPLEMENTED,
            502: grpc.StatusCode.UNAVAILABLE,
            503: grpc.StatusCode.UNAVAILABLE,
            504: grpc.StatusCode.DEADLINE_EXCEEDED,
            505: grpc.StatusCode.UNIMPLEMENTED,
            511: grpc.StatusCode.UNAVAILABLE
        }

    @property
    def body(self) -> Any:
        return self._body

    @body.setter
    def body(self, body) -> None:
        self._body = body

    @property
    def code(self) -> int:
        if self._code == 200 and self.has_errors:
            self._code = 400
        return self._code

    @code.setter
    def code(self, code: int) -> None:
        self._code = code

    @property
    def grpc_code(self) -> grpc.StatusCode:
        return self.__http_grpc_code_mapping.get(self.code, grpc.StatusCode.UNKNOWN)

    @property
    def context(self) -> Any:
        return self.__context

    @context.setter
    def context(self, context: Any) -> None:
        pass  # Context is managed by gRPC and does not require setting in this normalizer NOSONAR

    @property
    def has_errors(self) -> bool:
        return self._has_errors

    @property
    def rpc_response(self) -> Callable[..., Any]:
        return self.__rpc_response

    def set_error(self, key_path: str, message: str) -> None:
        self._has_errors = True
        self.context.set_details(f'{key_path}: {message}')

    def get_response(self) -> Any:
        self.context.set_code(self.grpc_code)
        if self.has_errors or self.body is None:
            return self.rpc_response()  # Return an empty response if there are errors
        return self.rpc_response(**self.body)

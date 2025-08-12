import abc
from typing import Any, Optional


class ResponseInterface(abc.ABC):
    '''
    An interface for response handling classes.
    This interface defines the methods and properties that any response handling class must implement.
    '''

    def __init__(self):
        self._code: int = 200  # NOSONAR Overwrite WSGI behavior for gRPC context
        self._body: Optional[Any] = None
        self._has_errors: bool = False

    @property
    @abc.abstractmethod
    def body(self) -> Any:
        raise NotImplementedError

    @body.setter
    @abc.abstractmethod
    def body(self, body: Any) -> None:
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def code(self) -> int:
        raise NotImplementedError

    @code.setter
    @abc.abstractmethod
    def code(self, code: int) -> None:
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def has_errors(self) -> bool:
        raise NotImplementedError

    @abc.abstractmethod
    def set_error(self, key_path: str, message: str) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def get_response(self) -> Any:
        raise NotImplementedError

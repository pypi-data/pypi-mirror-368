from typing import Any


class ApiException(Exception):
    '''Base class for API exceptions. It can be extended to create specific exceptions with custom error codes and messages'''

    def __init__(self, **kwargs: Any) -> None:
        self.code: int = kwargs.get('code', 500)
        self.key_path: str = kwargs.get('key_path', 'unknown')
        self.message: str = kwargs.get('message', 'internal server error')
        super().__init__(self.message)


class ApiTimeOutException(Exception):
    '''Exception raised when an API request times out. It can be extended to create specific timeout exceptions with custom error codes and messages'''

    def __init__(self, **kwargs: Any) -> None:
        self.code: int = kwargs.get('code', 408)
        self.key_path: str = kwargs.get('key_path', 'unknown')
        self.message: str = kwargs.get('message', 'request timeout')
        super().__init__(self.message)

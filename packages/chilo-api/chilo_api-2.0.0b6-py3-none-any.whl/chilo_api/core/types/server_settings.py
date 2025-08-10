from typing import Protocol, Dict, Union, Any


class ServerSettings(Protocol):
    """Protocol for server objects with required attributes"""
    api_type: str
    host: str
    port: int
    reload: bool
    verbose: bool
    timeout: Union[int, float]
    openapi_validate_request: bool
    openapi_validate_response: bool
    source: Dict[str, str]
    protobufs: Union[str, None]
    handlers: str
    api_config: Any
    reflection: bool
    private_key: Union[str, None]
    certificate: Union[str, None]
    max_workers: Union[int, None]

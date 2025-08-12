from typing import Callable
from typing_extensions import Any

from chilo_api.core.requirements.handler import RequirementsHandler

__all__ = ['requirements']


def requirements(**kwargs: Any) -> Callable[[Any], Any]:  # NOSONAR
    '''
    All available parameters you can use with requirements, allows for custom params to be sent either directly as additional kwargs or if 
    using type checkers, can be passed in through the `custom=` param

    Parameters
    ----------
    required_headers: list[str] (optional)
        list of required headers for the request
    available_headers: list[str] (optional)
        list of available headers for the request; is strict and will raise error on ANY additional headers
    required_query: list[str] (optional)
        list of required query string params for the request
    available_query: list[str] (optional)
        list of available query string params for the request
    required_body: str, dict, pydantic model (optional)
        required body for the request to pass validation; can be a string reference to a schema defined in the openapi, a dict in the jsonschema structure or a pydantic model
    required_route: str (optional)
        the path required hit this endpoint; required for dynamic endpoints
    required_response: str (optional)
        the body requirements for the response
    auth_required: bool (optional)
        whether this endpoint requires authentiction; will automatically trigger function defined in when_auth_required (if available)
    before: callable (optional)
        function to run before the method is called
    after: callable (optional)
        function to run after the method is called
    request_class: any (optional)
        class to send instead of a standard request class; this class will get a kwarg, request=request, which is the standard request class
    timeout: int (optional)
        how long the endpoint has to run, will override any value provided in the Chilo class definition
    custom: any (optional)
        add additional custom params here, will be passed to before_all, before, after, after_all, when_auth_required
    summary: str (optional)
        will fill out summary key in openapi file when generated
    deprecated: bool (optional)
        will fill out deprecated field in openapi file when generated (default is False)
    protobuf: str (optional)
        the protobuf file to use for this endpoint; will be used to generate the request and response
    service: str (optional)
        the service name for this endpoint; will be used to generate the request and response
    rpc: str (optional)
        the rpc name for this endpoint; will be used to generate the request and response
    stream: bool (optional)
        whether this endpoint is a stream endpoint; will use the stream decorator to handle the request and response
    Note: if stream is set to True, the function will be wrapped in a generator and will yield the response instead of returning it directly.
    If you want to use a custom request class, you must set the request_class parameter to the class you want to use.
    Additional parameters can be added to the kwargs and will be passed to the before, after, when_auth_required functions.
    If you want to use a custom request class, you must set the request_class parameter to the class you want to use.
    '''
    def decorator_func(func: Callable) -> Callable[[Any, Any], Any]:
        handler = RequirementsHandler(kwargs)
        return handler.wrap_function(func)
    return decorator_func

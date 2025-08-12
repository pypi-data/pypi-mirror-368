import abc
from typing import Any, Dict, List, Callable, Optional, Union


class PipelineInterface(abc.ABC):
    '''
    An abstract base class to represent a processing pipeline.
    This class defines the structure and required methods for any pipeline implementation.
    It includes properties and methods for handling various stages of request processing,
    such as authentication, validation, endpoint execution, and response handling.
    Each method can be overridden to provide custom behavior for specific stages of the pipeline.
    Attributes
    ----------
    _openapi_validate_request: Optional[bool]
        A flag indicating whether to validate requests against OpenAPI specifications.
    _openapi_validate_response: Optional[bool]
        A flag indicating whether to validate responses against OpenAPI specifications.
    _before_all: Callable[[Any, Any, Any], None]
        A callable to be executed before all other steps in the pipeline.
    _after_all: Callable[[Any, Any, Any], None]
        A callable to be executed after all other steps in the pipeline.
    _when_auth_required: Callable[[Any, Any, Any], None]
        A callable to be executed when authentication is required.
    _validator: Any
        An instance of a validator used for request and response validation.
    Methods
    -------
    steps() -> List[Dict[str, Union[Callable[[Any, Any, Any], None], bool]]]
        An abstract property that should return the steps in the pipeline.
    stream_steps() -> List[Dict[str, Union[Callable[[Any, Any, Any], None], bool]]]
        An abstract property that should return the steps for streaming requests.
    should_run_endpoint() -> bool
        A property that indicates whether the endpoint step should run.
    endpoint(request: Any, response: Any, endpoint: Any) -> None
        A method to execute the endpoint logic.
    should_run_before_all() -> bool
        A property that indicates whether the before_all step should run.
    before_all(request: Any, response: Any, endpoint: Any) -> None
        A method to execute logic before all other steps.
    should_run_when_auth_required() -> bool
        A property that indicates whether the when_auth_required step should run.
    when_auth_required(request: Any, response: Any, endpoint: Any) -> None
        A method to execute logic when authentication is required.
    should_run_request_validation() -> bool
        A property that indicates whether request validation should run.
    run_request_validation(request: Any, response: Any, endpoint: Any) -> None
        A method to perform request validation.
    should_run_request_validation_openapi() -> bool
        A property that indicates whether OpenAPI request validation should run.
    run_request_validation_openapi(request: Any, response: Any, endpoint: Any) -> None
        A method to perform OpenAPI request validation.
    should_run_response_validation() -> bool
        A property that indicates whether response validation should run.
    run_response_validation(request: Any, response: Any, endpoint: Any) -> None
        A method to perform response validation.
    should_run_response_validation_openapi() -> bool
        A property that indicates whether OpenAPI response validation should run.
    run_response_validation_openapi(request: Any, response: Any, endpoint: Any) -> None
        A method to perform OpenAPI response validation.
    should_run_after_all() -> bool
        A property that indicates whether the after_all step should run.
    after_all(request: Any, response: Any, endpoint: Any) -> None
        A method to execute logic after all other steps.
    '''

    def __init__(self, **kwargs: Any) -> None:
        self._openapi_validate_request: Optional[bool] = kwargs.get('openapi_validate_request')
        self._openapi_validate_response: Optional[bool] = kwargs.get('openapi_validate_response')
        self._before_all: Callable[[Any, Any, Any], None] = kwargs.get('before_all', lambda request, response, endpoint: None)
        self._after_all: Callable[[Any, Any, Any], None] = kwargs.get('after_all', lambda request, response, endpoint: None)
        self._when_auth_required: Callable[[Any, Any, Any], None] = kwargs.get('when_auth_required', lambda request, response, endpoint: None)
        self._validator: Any = kwargs.get('validator', None)

    @property
    @abc.abstractmethod
    def steps(self) -> List[Dict[str, Union[Callable[[Any, Any, Any], None], bool]]]:
        '''Return the steps in the pipeline.'''
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def stream_steps(self) -> List[Dict[str, Union[Callable[[Any, Any, Any], None], bool]]]:
        '''Return the steps for streaming requests.'''
        raise NotImplementedError

    @property
    def should_run_endpoint(self) -> bool:
        return True

    def endpoint(self, request: Any, response: Any, endpoint: Any) -> None:
        endpoint.run(request, response)

    @property
    def should_run_before_all(self) -> bool:
        return self._before_all is not None and callable(self._before_all)

    def before_all(self, request: Any, response: Any, endpoint: Any) -> None:
        self._before_all(request, response, endpoint.requirements)

    @property
    def should_run_when_auth_required(self) -> bool:
        return self._when_auth_required is not None and callable(self._when_auth_required)

    def when_auth_required(self, request: Any, response: Any, endpoint: Any) -> None:
        if not endpoint.requires_auth:
            return
        self._when_auth_required(request, response, endpoint.requirements)

    @property
    def should_run_request_validation(self) -> bool:
        return not self._openapi_validate_request

    def run_request_validation(self, request: Any, response: Any, endpoint: Any) -> None:
        if not endpoint.has_requirements:
            return
        self._validator.validate_request_with_openapi(request, response, endpoint.requirements)

    @property
    def should_run_request_validation_openapi(self) -> bool:
        return bool(self._openapi_validate_request)

    def run_request_validation_openapi(self, request: Any, response: Any, endpoint: Any) -> None:
        self._validator.validate_request_with_openapi(request, response, endpoint.requirements)

    @property
    def should_run_response_validation(self) -> bool:
        return not self._openapi_validate_response

    def run_response_validation(self, request: Any, response: Any, endpoint: Any) -> None:
        if not endpoint.has_required_response:
            return
        self._validator.validate_response_with_openapi(request, response, endpoint.requirements)

    @property
    def should_run_response_validation_openapi(self) -> bool:
        return bool(self._openapi_validate_response)

    def run_response_validation_openapi(self, request: Any, response: Any, endpoint: Any) -> None:
        self._validator.validate_response_with_openapi(request, response, endpoint.requirements)

    @property
    def should_run_after_all(self) -> bool:
        return self._after_all is not None and callable(self._after_all)

    def after_all(self, request: Any, response: Any, endpoint: Any) -> None:
        self._after_all(request, response, endpoint.requirements)

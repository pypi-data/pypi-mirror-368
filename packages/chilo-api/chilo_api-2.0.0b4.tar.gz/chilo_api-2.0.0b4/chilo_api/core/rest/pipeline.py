from typing import Any, Dict, List, Callable, Union

from chilo_api.core.interfaces.pipeline import PipelineInterface
from chilo_api.core.validator import Validator


class RestPipeline(PipelineInterface):
    '''
    A class to represent a REST pipeline

    Attributes
    ----------
    steps: List[Dict[str, Union[Callable[[Any, Any, Any], None], bool]]]
        The steps in the pipeline.
    stream_steps: List[Dict[str, Union[Callable[[Any, Any, Any], None], bool]]]
        The steps for streaming requests.
    '''

    def __init__(self, **kwargs: Any) -> None:
        validator: Validator = Validator(**kwargs)
        validator.auto_load()
        kwargs['validator'] = validator
        super().__init__(**kwargs)

    @property
    def steps(self) -> List[Dict[str, Union[Callable[[Any, Any, Any], None], bool]]]:
        return [
            {'method': self.before_all, 'should_run': self.should_run_before_all},
            {'method': self.when_auth_required, 'should_run': self.should_run_when_auth_required},
            {'method': self.run_request_validation, 'should_run': self.should_run_request_validation},
            {'method': self.run_request_validation_openapi, 'should_run': self.should_run_request_validation_openapi},
            {'method': self.endpoint, 'should_run': self.should_run_endpoint},
            {'method': self.run_response_validation, 'should_run': self.should_run_response_validation},
            {'method': self.run_response_validation_openapi, 'should_run': self.should_run_response_validation_openapi},
            {'method': self.after_all, 'should_run': self.should_run_after_all},
        ]

    @property
    def stream_steps(self) -> List[Dict[str, Union[Callable[[Any, Any, Any], None], bool]]]:
        return [
            {'method': self.before_all, 'should_run': self.should_run_before_all},
            {'method': self.when_auth_required, 'should_run': self.should_run_when_auth_required}
        ]  # pragma: no cover

    def when_auth_required(self, request: Any, response: Any, endpoint: Any) -> None:
        if not ((self._openapi_validate_request and self._validator.request_has_security(request)) or endpoint.requires_auth):
            return  # pragma: no cover
        self._when_auth_required(request, response, endpoint.requirements)

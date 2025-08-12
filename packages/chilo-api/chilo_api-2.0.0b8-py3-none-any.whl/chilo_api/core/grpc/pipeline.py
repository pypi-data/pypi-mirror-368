from typing import Any, Dict, List, Callable, Union

from chilo_api.core.interfaces.pipeline import PipelineInterface


class GRPCPipeline(PipelineInterface):
    '''
    A class to represent a gRPC pipeline

    Attributes
    ----------
    steps: List[Dict[str, Union[Callable[[Any, Any, Any], None], bool]]]
        The steps in the pipeline.
    stream_steps: List[Dict[str, Union[Callable[[Any, Any, Any], None], bool]]]
        The steps for streaming requests.
    '''

    @property
    def steps(self) -> List[Dict[str, Union[Callable[[Any, Any, Any], None], bool]]]:
        return [
            {'method': self.before_all, 'should_run': self.should_run_before_all},
            {'method': self.when_auth_required, 'should_run': self.should_run_when_auth_required},
            {'method': self.endpoint, 'should_run': self.should_run_endpoint},
            {'method': self.after_all, 'should_run': self.should_run_after_all},
        ]

    @property
    def stream_steps(self) -> List[Dict[str, Union[Callable[[Any, Any, Any], None], bool]]]:
        return [
            {'method': self.before_all, 'should_run': self.should_run_before_all},
            {'method': self.when_auth_required, 'should_run': self.should_run_when_auth_required}
        ]

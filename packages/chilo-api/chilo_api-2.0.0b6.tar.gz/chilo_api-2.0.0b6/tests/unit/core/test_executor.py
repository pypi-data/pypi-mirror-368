import unittest
from unittest.mock import Mock, patch
import datetime
from werkzeug.wrappers import Response as WSGIResponse

from chilo_api.core.executor import Executor
from chilo_api.core.exception import ApiException, ApiTimeOutException
from chilo_api.core.rest.pipeline import RestPipeline
from chilo_api.core.rest.request import RestRequest as Request
from chilo_api.core.rest.response import RestResponse as Response
from chilo_api.core.resolver import Resolver


class ExecutorTest(unittest.TestCase):

    def setUp(self):
        self.mock_pipeline = Mock(spec=RestPipeline)
        self.mock_resolver = Mock(spec=Resolver)
        self.mock_request = Mock(spec=Request)
        self.mock_response = Mock(spec=Response)
        self.mock_endpoint = Mock()
        self.mock_wsgi_response = Mock(spec=WSGIResponse)

        self.mock_response.has_errors = False
        self.mock_response.get_response.return_value = self.mock_wsgi_response
        self.mock_resolver.get_endpoint.return_value = self.mock_endpoint

        self.default_kwargs = {
            'handlers': 'test/handlers',
            'verbose': False,
            'output_error': False,
            'default_error_message': 'An error occurred'
        }

    def test_executor_initialization_with_defaults(self):
        _ = Executor(self.mock_pipeline, self.mock_resolver, **self.default_kwargs)
        self.mock_resolver.auto_load.assert_called_once()

    def test_executor_initialization_with_grpc(self):
        mock_grpc_endpoint = Mock()
        _ = Executor(
            self.mock_pipeline,
            self.mock_resolver,
            is_grpc=True,
            grpc_endpoint=mock_grpc_endpoint,
            **self.default_kwargs
        )
        self.mock_resolver.auto_load.assert_called_once()

    def test_executor_initialization_with_all_kwargs(self):
        mock_on_error = Mock()
        mock_on_timeout = Mock()
        mock_grpc_endpoint = Mock()

        _ = Executor(
            self.mock_pipeline,
            self.mock_resolver,
            is_grpc=True,
            grpc_endpoint=mock_grpc_endpoint,
            verbose=True,
            output_error=True,
            on_error=mock_on_error,
            on_timeout=mock_on_timeout,
            default_error_message="Custom error message",
            handlers='custom/handlers'
        )
        self.mock_resolver.auto_load.assert_called_once()

    def test_run_successful_request(self):
        self.mock_pipeline.steps = [
            {'method': Mock(), 'should_run': True},
            {'method': Mock(), 'should_run': True}
        ]

        executor = Executor(self.mock_pipeline, self.mock_resolver, **self.default_kwargs)
        result = executor.run(self.mock_request, self.mock_response)

        self.mock_resolver.get_endpoint.assert_called_once_with(self.mock_request)

        for step in self.mock_pipeline.steps:
            step['method'].assert_called_once_with(self.mock_request, self.mock_response, self.mock_endpoint)

        self.mock_response.get_response.assert_called_once()
        self.mock_resolver.reset.assert_called_once()
        self.assertEqual(result, self.mock_wsgi_response)

    def test_run_with_grpc_endpoint(self):
        mock_grpc_endpoint = Mock()
        self.mock_pipeline.steps = [
            {'method': Mock(), 'should_run': True}
        ]

        executor = Executor(
            self.mock_pipeline,
            self.mock_resolver,
            is_grpc=True,
            grpc_endpoint=mock_grpc_endpoint,
            **self.default_kwargs
        )

        result = executor.run(self.mock_request, self.mock_response)

        self.mock_resolver.get_endpoint.assert_not_called()

        for step in self.mock_pipeline.steps:
            step['method'].assert_called_once_with(self.mock_request, self.mock_response, mock_grpc_endpoint)

        self.assertEqual(result, self.mock_wsgi_response)

    def test_run_skips_steps_when_response_has_errors(self):
        self.mock_response.has_errors = True
        self.mock_pipeline.steps = [
            {'method': Mock(), 'should_run': True},
            {'method': Mock(), 'should_run': True}
        ]

        executor = Executor(self.mock_pipeline, self.mock_resolver, **self.default_kwargs)
        executor.run(self.mock_request, self.mock_response)

        for step in self.mock_pipeline.steps:
            step['method'].assert_not_called()

    def test_run_skips_steps_when_should_run_false(self):
        self.mock_pipeline.steps = [
            {'method': Mock(), 'should_run': False},
            {'method': Mock(), 'should_run': True}
        ]

        executor = Executor(self.mock_pipeline, self.mock_resolver, **self.default_kwargs)
        executor.run(self.mock_request, self.mock_response)

        self.mock_pipeline.steps[0]['method'].assert_not_called()
        self.mock_pipeline.steps[1]['method'].assert_called_once()

    def test_run_skips_steps_when_method_not_callable(self):
        self.mock_pipeline.steps = [
            {'method': "not_callable", 'should_run': True},
            {'method': Mock(), 'should_run': True}
        ]

        executor = Executor(self.mock_pipeline, self.mock_resolver, **self.default_kwargs)
        executor.run(self.mock_request, self.mock_response)

        self.mock_pipeline.steps[1]['method'].assert_called_once()

    @patch('chilo_api.core.executor.CommonLogger')
    def test_run_handles_api_exception(self, mock_logger_class):
        mock_logger = Mock()
        mock_logger_class.return_value = mock_logger

        api_exception = ApiException(code=400, message="Bad request", key_path="test.field")
        self.mock_resolver.get_endpoint.side_effect = api_exception

        executor = Executor(self.mock_pipeline, self.mock_resolver, **self.default_kwargs)
        result = executor.run(self.mock_request, self.mock_response)

        self.mock_response.set_error.assert_called_once_with(
            key_path="test.field",
            message="Bad request"
        )
        self.assertEqual(self.mock_response.code, 400)
        mock_logger.log.assert_called_once()
        self.assertEqual(result, self.mock_wsgi_response)

    @patch('chilo_api.core.executor.CommonLogger')
    def test_run_handles_timeout_exception(self, mock_logger_class):
        mock_logger = Mock()
        mock_logger_class.return_value = mock_logger
        mock_on_timeout = Mock()

        timeout_exception = ApiTimeOutException(code=408, message="Request timeout")
        self.mock_resolver.get_endpoint.side_effect = timeout_exception

        executor = Executor(
            self.mock_pipeline,
            self.mock_resolver,
            on_timeout=mock_on_timeout,
            **self.default_kwargs
        )

        executor.run(self.mock_request, self.mock_response)

        mock_on_timeout.assert_called_once_with(self.mock_request, self.mock_response, timeout_exception)

    @patch('chilo_api.core.executor.CommonLogger')
    def test_run_handles_general_exception(self, mock_logger_class):
        mock_logger = Mock()
        mock_logger_class.return_value = mock_logger

        general_exception = Exception("Something went wrong")
        self.mock_resolver.get_endpoint.side_effect = general_exception

        executor = Executor(
            self.mock_pipeline,
            self.mock_resolver,
            output_error=True,
            handlers='test/handlers'
        )

        executor.run(self.mock_request, self.mock_response)

        self.mock_response.set_error.assert_called_once_with(
            key_path="unknown",
            message="Something went wrong"
        )
        self.assertEqual(self.mock_response.code, 500)

    @patch('chilo_api.core.executor.CommonLogger')
    def test_run_uses_default_error_message_when_output_error_false(self, mock_logger_class):
        mock_logger = Mock()
        mock_logger_class.return_value = mock_logger

        general_exception = Exception("Something went wrong")
        self.mock_resolver.get_endpoint.side_effect = general_exception

        executor = Executor(
            self.mock_pipeline,
            self.mock_resolver,
            output_error=False,
            default_error_message="Custom default error",
            handlers='test/handlers'
        )

        executor.run(self.mock_request, self.mock_response)

        self.mock_response.set_error.assert_called_once_with(
            key_path="unknown",
            message="Custom default error"
        )

    @patch('chilo_api.core.executor.CommonLogger')
    def test_run_handles_custom_on_error_callback(self, mock_logger_class):
        mock_logger = Mock()
        mock_logger_class.return_value = mock_logger
        mock_on_error = Mock()

        api_exception = ApiException(code=400, message="Bad request")
        self.mock_resolver.get_endpoint.side_effect = api_exception

        executor = Executor(
            self.mock_pipeline,
            self.mock_resolver,
            on_error=mock_on_error,
            **self.default_kwargs
        )

        executor.run(self.mock_request, self.mock_response)

        mock_on_error.assert_called_once_with(self.mock_request, self.mock_response, api_exception)

    @patch('chilo_api.core.executor.CommonLogger')
    @patch('chilo_api.core.executor.datetime')
    @patch('chilo_api.core.executor.JsonHelper')
    def test_run_logs_verbose_when_enabled(self, mock_json_helper, mock_datetime, mock_logger_class):
        mock_logger = Mock()
        mock_logger_class.return_value = mock_logger
        mock_datetime.datetime.now.return_value.strftime.return_value = "2023-01-01 12:00:00"
        mock_json_helper.decode.side_effect = lambda x: f"decoded_{x}"

        self.mock_pipeline.steps = []

        executor = Executor(
            self.mock_pipeline,
            self.mock_resolver,
            verbose=True,
            handlers='test/handlers'
        )

        executor.run(self.mock_request, self.mock_response)

        self.assertEqual(mock_logger.log.call_count, 1)
        log_call = mock_logger.log.call_args[1]
        self.assertEqual(log_call['level'], 'DEBUG')
        self.assertIn('_timestamp', log_call['log'])
        self.assertIn('request', log_call['log'])
        self.assertIn('response', log_call['log'])

    @patch('chilo_api.core.executor.CommonLogger')
    def test_run_doesnt_log_verbose_when_disabled(self, mock_logger_class):
        mock_logger = Mock()
        mock_logger_class.return_value = mock_logger

        self.mock_pipeline.steps = []

        executor = Executor(
            self.mock_pipeline,
            self.mock_resolver,
            verbose=False,
            handlers='test/handlers'
        )

        executor.run(self.mock_request, self.mock_response)

        mock_logger.log.assert_not_called()

    def test_stream_successful_request(self):
        self.mock_pipeline.stream_steps = [
            {'method': Mock(), 'should_run': True}
        ]
        self.mock_endpoint.stream.return_value = iter(['chunk1', 'chunk2'])

        executor = Executor(self.mock_pipeline, self.mock_resolver, **self.default_kwargs)
        generator = executor.stream(self.mock_request, self.mock_response)
        results = list(generator)

        self.mock_resolver.get_endpoint.assert_called_once_with(self.mock_request)

        for step in self.mock_pipeline.stream_steps:
            step['method'].assert_called_once_with(self.mock_request, self.mock_response, self.mock_endpoint)

        self.mock_endpoint.stream.assert_called_once_with(self.mock_request, self.mock_response)
        self.assertEqual(results, ['chunk1', 'chunk2'])

    def test_stream_with_grpc_endpoint(self):
        mock_grpc_endpoint = Mock()
        mock_grpc_endpoint.stream.return_value = iter(['grpc_chunk'])
        self.mock_pipeline.stream_steps = []

        executor = Executor(
            self.mock_pipeline,
            self.mock_resolver,
            is_grpc=True,
            grpc_endpoint=mock_grpc_endpoint,
            **self.default_kwargs
        )

        generator = executor.stream(self.mock_request, self.mock_response)
        results = list(generator)

        self.mock_resolver.get_endpoint.assert_not_called()
        mock_grpc_endpoint.stream.assert_called_once_with(self.mock_request, self.mock_response)
        self.assertEqual(results, ['grpc_chunk'])

    def test_stream_skips_steps_when_response_has_errors(self):
        self.mock_response.has_errors = True
        self.mock_pipeline.stream_steps = [
            {'method': Mock(), 'should_run': True}
        ]
        self.mock_endpoint.stream.return_value = iter([])

        executor = Executor(self.mock_pipeline, self.mock_resolver, **self.default_kwargs)
        list(executor.stream(self.mock_request, self.mock_response))

        for step in self.mock_pipeline.stream_steps:
            step['method'].assert_not_called()

    @patch('chilo_api.core.executor.CommonLogger')
    def test_stream_handles_exception(self, mock_logger_class):
        mock_logger = Mock()
        mock_logger_class.return_value = mock_logger

        api_exception = ApiException(code=400, message="Stream error")
        self.mock_resolver.get_endpoint.side_effect = api_exception

        executor = Executor(self.mock_pipeline, self.mock_resolver, **self.default_kwargs)
        generator = executor.stream(self.mock_request, self.mock_response)
        list(generator)

        self.mock_response.set_error.assert_called_once_with(
            key_path="unknown",
            message="Stream error"
        )
        mock_logger.log.assert_called_once()

    @patch('chilo_api.core.executor.CommonLogger')
    def test_error_handling_catches_exception_in_error_handler(self, mock_logger_class):
        mock_logger = Mock()
        mock_logger_class.return_value = mock_logger

        self.mock_response.set_error.side_effect = Exception("Error in error handler")
        general_exception = Exception("Original error")
        self.mock_resolver.get_endpoint.side_effect = general_exception

        executor = Executor(self.mock_pipeline, self.mock_resolver, **self.default_kwargs)
        executor.run(self.mock_request, self.mock_response)

        self.assertEqual(mock_logger.log.call_count, 1)

    def test_exception_mapping_with_unknown_exception_type(self):
        class CustomException(Exception):
            def __init__(self, message):
                self.code = 422
                self.message = message
                super().__init__(message)

        custom_exception = CustomException("Custom error")
        self.mock_resolver.get_endpoint.side_effect = custom_exception

        executor = Executor(self.mock_pipeline, self.mock_resolver, **self.default_kwargs)
        executor.run(self.mock_request, self.mock_response)

        self.assertEqual(self.mock_response.code, 422)

    def test_error_attributes_fallback_to_defaults(self):
        class MinimalException(Exception):
            pass

        minimal_exception = MinimalException("Minimal error")
        self.mock_resolver.get_endpoint.side_effect = minimal_exception

        executor = Executor(
            self.mock_pipeline,
            self.mock_resolver,
            output_error=True,
            handlers='test/handlers'
        )

        executor.run(self.mock_request, self.mock_response)

        self.assertEqual(self.mock_response.code, 500)
        self.mock_response.set_error.assert_called_once_with(
            key_path="unknown",
            message="Minimal error"
        )

    def test_callable_check_for_error_functions(self):
        non_callable_error = "not_a_function"

        executor = Executor(
            self.mock_pipeline,
            self.mock_resolver,
            on_error=non_callable_error,  # type: ignore
            **self.default_kwargs
        )

        api_exception = ApiException(code=400, message="Test error")
        self.mock_resolver.get_endpoint.side_effect = api_exception

        executor.run(self.mock_request, self.mock_response)

        self.mock_response.set_error.assert_called_once()

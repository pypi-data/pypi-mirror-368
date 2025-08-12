import unittest
from unittest.mock import Mock, patch, MagicMock
from types import GeneratorType

from chilo_api.core.grpc.mediator import GRPCMediator
from chilo_api.core.grpc.endpoint import GRPCEndpoint
from chilo_api.core.grpc.request import GRPCRequest
from chilo_api.core.grpc.response import GRPCResponse
from chilo_api.core.grpc.pipeline import GRPCPipeline
from chilo_api.core.placeholders.resolver import ResolverPlaceholder
from chilo_api.core.executor import Executor
from chilo_api.core.router import Router


class GRPCMediatorTest(unittest.TestCase):

    def setUp(self):
        self.mock_api_config = Mock(spec=Router)
        self.mock_api_config.__dict__ = {
            'handlers': 'test/handlers',
            'verbose': False,
            'output_error': False,
            'default_error_message': 'An error occurred'
        }

        self.mock_endpoint = Mock(spec=GRPCEndpoint)
        self.mock_endpoint.response_is_stream = False
        self.mock_endpoint.rpc_response = Mock()

        self.mock_rpc_request = Mock()
        self.mock_context = Mock()
        self.mock_executor_result = Mock()

    @patch('chilo_api.core.grpc.mediator.Executor')
    @patch('chilo_api.core.grpc.mediator.GRPCPipeline')
    @patch('chilo_api.core.grpc.mediator.ResolverPlaceholder')
    def test_initialization(self, mock_resolver_class, mock_pipeline_class, mock_executor_class):
        mock_pipeline = Mock()
        mock_resolver = Mock()
        mock_executor = Mock()

        mock_pipeline_class.return_value = mock_pipeline
        mock_resolver_class.return_value = mock_resolver
        mock_executor_class.return_value = mock_executor

        mediator = GRPCMediator(self.mock_api_config, self.mock_endpoint)

        mock_pipeline_class.assert_called_once_with(**self.mock_api_config.__dict__)
        mock_resolver_class.assert_called_once()

        expected_executor_kwargs = {
            'is_grpc': True,
            'grpc_endpoint': self.mock_endpoint,
            **self.mock_api_config.__dict__
        }
        mock_executor_class.assert_called_once_with(
            mock_pipeline,
            mock_resolver,
            **expected_executor_kwargs
        )

        self.assertEqual(mediator.executor, mock_executor)
        self.assertEqual(mediator.endpoint, self.mock_endpoint)

    def test_get_endpoint_request_method_returns_stream_method_when_stream_response(self):
        self.mock_endpoint.response_is_stream = True

        mediator = GRPCMediator(self.mock_api_config, self.mock_endpoint)

        result = mediator.get_endpoint_request_method()

        self.assertEqual(result, mediator.execute_endpoint_request_stream)

    def test_get_endpoint_request_method_returns_regular_method_when_not_stream_response(self):
        self.mock_endpoint.response_is_stream = False

        mediator = GRPCMediator(self.mock_api_config, self.mock_endpoint)

        result = mediator.get_endpoint_request_method()

        self.assertEqual(result, mediator.execute_endpoint_request_method)

    @patch('chilo_api.core.grpc.mediator.GRPCRequest')
    @patch('chilo_api.core.grpc.mediator.GRPCResponse')
    def test_execute_endpoint_request_method(self, mock_response_class, mock_request_class):
        mock_request = Mock()
        mock_response = Mock()
        mock_request_class.return_value = mock_request
        mock_response_class.return_value = mock_response

        mediator = GRPCMediator(self.mock_api_config, self.mock_endpoint)
        mediator.executor = Mock()
        mediator.executor.run.return_value = self.mock_executor_result

        result = mediator.execute_endpoint_request_method(self.mock_rpc_request, self.mock_context)

        mock_request_class.assert_called_once_with(self.mock_rpc_request, self.mock_context)
        mock_response_class.assert_called_once_with(
            rpc_response=self.mock_endpoint.rpc_response,
            context=self.mock_context
        )
        mediator.executor.run.assert_called_once_with(mock_request, mock_response)
        self.assertEqual(result, self.mock_executor_result)

    @patch('chilo_api.core.grpc.mediator.GRPCRequest')
    @patch('chilo_api.core.grpc.mediator.GRPCResponse')
    def test_execute_endpoint_request_stream(self, mock_response_class, mock_request_class):
        mock_request = Mock()
        mock_response = Mock()
        mock_request_class.return_value = mock_request
        mock_response_class.return_value = mock_response

        mock_stream_data = ['chunk1', 'chunk2', 'chunk3']

        mediator = GRPCMediator(self.mock_api_config, self.mock_endpoint)
        mediator.executor = Mock()
        mediator.executor.stream.return_value = iter(mock_stream_data)

        result = mediator.execute_endpoint_request_stream(self.mock_rpc_request, self.mock_context)

        self.assertIsInstance(result, GeneratorType)

        collected_data = list(result)

        mock_request_class.assert_called_once_with(self.mock_rpc_request, self.mock_context)
        mock_response_class.assert_called_once_with(
            rpc_response=self.mock_endpoint.rpc_response,
            context=self.mock_context
        )
        mediator.executor.stream.assert_called_once_with(mock_request, mock_response)
        self.assertEqual(collected_data, mock_stream_data)

    @patch('chilo_api.core.grpc.mediator.GRPCRequest')
    @patch('chilo_api.core.grpc.mediator.GRPCResponse')
    def test_get_request_response_creates_correct_objects_via_stream(self, mock_response_class, mock_request_class):
        mock_request = Mock()
        mock_response = Mock()
        mock_request_class.return_value = mock_request
        mock_response_class.return_value = mock_response
        mediator = GRPCMediator(self.mock_api_config, self.mock_endpoint)
        mediator.executor = Mock()
        mediator.executor.stream.return_value = iter(["chunk1", "chunk2"])
        result = mediator.execute_endpoint_request_stream(self.mock_rpc_request, self.mock_context)
        list(result)
        mock_request_class.assert_called_once_with(self.mock_rpc_request, self.mock_context)
        mock_response_class.assert_called_once_with(
            rpc_response=self.mock_endpoint.rpc_response,
            context=self.mock_context
        )
        mediator.executor.stream.assert_called_once_with(mock_request, mock_response)

    def test_stream_method_yields_from_executor(self):
        self.mock_endpoint.response_is_stream = True

        mediator = GRPCMediator(self.mock_api_config, self.mock_endpoint)
        mediator.executor = Mock()

        def mock_stream_generator():
            yield "first"
            yield "second"
            yield "third"

        mediator.executor.stream.return_value = mock_stream_generator()

        with patch.object(mediator, '_GRPCMediator__get_request_response') as mock_get_req_resp:
            mock_request = Mock()
            mock_response = Mock()
            mock_get_req_resp.return_value = (mock_request, mock_response)

            generator = mediator.execute_endpoint_request_stream(self.mock_rpc_request, self.mock_context)
            results = list(generator)

            self.assertEqual(results, ["first", "second", "third"])
            mock_get_req_resp.assert_called_once_with(self.mock_rpc_request, self.mock_context)
            mediator.executor.stream.assert_called_once_with(mock_request, mock_response)

    def test_regular_method_returns_executor_result(self):
        self.mock_endpoint.response_is_stream = False

        mediator = GRPCMediator(self.mock_api_config, self.mock_endpoint)
        mediator.executor = Mock()
        mediator.executor.run.return_value = "execution_result"

        with patch.object(mediator, '_GRPCMediator__get_request_response') as mock_get_req_resp:
            mock_request = Mock()
            mock_response = Mock()
            mock_get_req_resp.return_value = (mock_request, mock_response)

            result = mediator.execute_endpoint_request_method(self.mock_rpc_request, self.mock_context)

            self.assertEqual(result, "execution_result")
            mock_get_req_resp.assert_called_once_with(self.mock_rpc_request, self.mock_context)
            mediator.executor.run.assert_called_once_with(mock_request, mock_response)

    def test_method_selection_based_on_stream_flag(self):
        test_cases = [
            (True, 'execute_endpoint_request_stream'),
            (False, 'execute_endpoint_request_method')
        ]

        for is_stream, expected_method_name in test_cases:
            with self.subTest(is_stream=is_stream):
                self.mock_endpoint.response_is_stream = is_stream

                mediator = GRPCMediator(self.mock_api_config, self.mock_endpoint)
                method = mediator.get_endpoint_request_method()

                self.assertEqual(method.__name__, expected_method_name)

    @patch('chilo_api.core.grpc.mediator.GRPCRequest')
    @patch('chilo_api.core.grpc.mediator.GRPCResponse')
    def test_request_response_creation_with_different_contexts(self, mock_response_class, mock_request_class):
        different_contexts = [Mock(), None, "string_context", 123]

        mediator = GRPCMediator(self.mock_api_config, self.mock_endpoint)
        mediator.executor = Mock()
        mediator.executor.run.return_value = "test_result"

        for context in different_contexts:
            with self.subTest(context=context):
                mock_request_class.reset_mock()
                mock_response_class.reset_mock()

                mediator.execute_endpoint_request_method(self.mock_rpc_request, context)

                mock_request_class.assert_called_once_with(self.mock_rpc_request, context)
                mock_response_class.assert_called_once_with(
                    rpc_response=self.mock_endpoint.rpc_response,
                    context=context
                )

    def test_endpoint_attribute_access(self):
        mediator = GRPCMediator(self.mock_api_config, self.mock_endpoint)

        self.assertEqual(mediator.endpoint, self.mock_endpoint)
        self.assertEqual(mediator.endpoint.response_is_stream, self.mock_endpoint.response_is_stream)
        self.assertEqual(mediator.endpoint.rpc_response, self.mock_endpoint.rpc_response)

    @patch('chilo_api.core.grpc.mediator.Executor')
    def test_executor_configuration_includes_all_api_config_attributes(self, mock_executor_class):
        additional_config = {
            'custom_setting': 'value',
            'another_setting': 42,
            'bool_setting': True
        }
        self.mock_api_config.__dict__.update(additional_config)

        _ = GRPCMediator(self.mock_api_config, self.mock_endpoint)

        call_args = mock_executor_class.call_args
        passed_kwargs = call_args[1]

        self.assertTrue(passed_kwargs['is_grpc'])
        self.assertEqual(passed_kwargs['grpc_endpoint'], self.mock_endpoint)

        for key, value in additional_config.items():
            self.assertEqual(passed_kwargs[key], value)

    def test_multiple_mediator_instances_are_independent(self):
        endpoint1 = Mock()
        endpoint1.response_is_stream = True
        endpoint1.rpc_response = Mock()

        endpoint2 = Mock()
        endpoint2.response_is_stream = False
        endpoint2.rpc_response = Mock()

        mediator1 = GRPCMediator(self.mock_api_config, endpoint1)
        mediator2 = GRPCMediator(self.mock_api_config, endpoint2)

        self.assertNotEqual(mediator1.endpoint, mediator2.endpoint)
        self.assertNotEqual(mediator1.executor, mediator2.executor)

        method1 = mediator1.get_endpoint_request_method()
        method2 = mediator2.get_endpoint_request_method()

        self.assertEqual(method1.__name__, 'execute_endpoint_request_stream')
        self.assertEqual(method2.__name__, 'execute_endpoint_request_method')

    @patch('chilo_api.core.grpc.mediator.GRPCRequest')
    @patch('chilo_api.core.grpc.mediator.GRPCResponse')
    def test_empty_stream_handling(self, mock_response_class, mock_request_class):
        mock_request = Mock()
        mock_response = Mock()
        mock_request_class.return_value = mock_request
        mock_response_class.return_value = mock_response

        mediator = GRPCMediator(self.mock_api_config, self.mock_endpoint)
        mediator.executor = Mock()
        mediator.executor.stream.return_value = iter([])

        result = mediator.execute_endpoint_request_stream(self.mock_rpc_request, self.mock_context)
        collected_data = list(result)

        self.assertEqual(collected_data, [])
        mediator.executor.stream.assert_called_once_with(mock_request, mock_response)

import unittest
from unittest.mock import Mock, MagicMock

from chilo_api.core.grpc.pipeline import GRPCPipeline


class GRPCPipelineTest(unittest.TestCase):

    def setUp(self):
        self.mock_request = Mock()
        self.mock_response = Mock()
        self.mock_endpoint = Mock()
        self.mock_endpoint.requirements = {'test': 'requirement'}
        self.mock_endpoint.requires_auth = True

    def test_initialization_with_no_kwargs(self):
        pipeline = GRPCPipeline()

        # Test that the pipeline methods exist and are callable
        self.assertTrue(hasattr(pipeline, 'before_all'))
        self.assertTrue(hasattr(pipeline, 'when_auth_required'))
        self.assertTrue(hasattr(pipeline, 'after_all'))
        self.assertTrue(hasattr(pipeline, 'endpoint'))

        self.assertTrue(callable(pipeline.before_all))
        self.assertTrue(callable(pipeline.when_auth_required))
        self.assertTrue(callable(pipeline.after_all))
        self.assertTrue(callable(pipeline.endpoint))

    def test_initialization_with_custom_callbacks(self):
        mock_before_all = Mock()
        mock_when_auth_required = Mock()
        mock_after_all = Mock()

        pipeline = GRPCPipeline(
            before_all=mock_before_all,
            when_auth_required=mock_when_auth_required,
            after_all=mock_after_all
        )

        # Test that custom callbacks are used
        pipeline.before_all(self.mock_request, self.mock_response, self.mock_endpoint)
        pipeline.when_auth_required(self.mock_request, self.mock_response, self.mock_endpoint)
        pipeline.after_all(self.mock_request, self.mock_response, self.mock_endpoint)

        mock_before_all.assert_called_once()
        mock_when_auth_required.assert_called_once()
        mock_after_all.assert_called_once()

    def test_steps_property(self):
        pipeline = GRPCPipeline()
        steps = pipeline.steps

        self.assertEqual(len(steps), 4)

        self.assertEqual(steps[0]['method'], pipeline.before_all)
        self.assertEqual(steps[0]['should_run'], pipeline.should_run_before_all)

        self.assertEqual(steps[1]['method'], pipeline.when_auth_required)
        self.assertEqual(steps[1]['should_run'], pipeline.should_run_when_auth_required)

        self.assertEqual(steps[2]['method'], pipeline.endpoint)
        self.assertEqual(steps[2]['should_run'], pipeline.should_run_endpoint)

        self.assertEqual(steps[3]['method'], pipeline.after_all)
        self.assertEqual(steps[3]['should_run'], pipeline.should_run_after_all)

    def test_stream_steps_property(self):
        pipeline = GRPCPipeline()
        stream_steps = pipeline.stream_steps

        self.assertEqual(len(stream_steps), 2)

        self.assertEqual(stream_steps[0]['method'], pipeline.before_all)
        self.assertEqual(stream_steps[0]['should_run'], pipeline.should_run_before_all)

        self.assertEqual(stream_steps[1]['method'], pipeline.when_auth_required)
        self.assertEqual(stream_steps[1]['should_run'], pipeline.should_run_when_auth_required)

    def test_should_run_endpoint_always_true(self):
        pipeline = GRPCPipeline()
        self.assertTrue(pipeline.should_run_endpoint)

    def test_endpoint_method_calls_endpoint_run(self):
        pipeline = GRPCPipeline()

        pipeline.endpoint(self.mock_request, self.mock_response, self.mock_endpoint)

        self.mock_endpoint.run.assert_called_once_with(self.mock_request, self.mock_response)

    def test_should_run_before_all_with_default_callback(self):
        pipeline = GRPCPipeline()
        self.assertTrue(pipeline.should_run_before_all)

    def test_should_run_before_all_with_custom_callback(self):
        mock_before_all = Mock()
        pipeline = GRPCPipeline(before_all=mock_before_all)
        self.assertTrue(pipeline.should_run_before_all)

    def test_should_run_before_all_with_none_callback(self):
        pipeline = GRPCPipeline(before_all=None)
        self.assertFalse(pipeline.should_run_before_all)

    def test_should_run_before_all_with_non_callable(self):
        pipeline = GRPCPipeline(before_all="not callable")
        self.assertFalse(pipeline.should_run_before_all)

    def test_before_all_method_calls_callback(self):
        mock_before_all = Mock()
        pipeline = GRPCPipeline(before_all=mock_before_all)

        pipeline.before_all(self.mock_request, self.mock_response, self.mock_endpoint)

        mock_before_all.assert_called_once_with(
            self.mock_request,
            self.mock_response,
            self.mock_endpoint.requirements
        )

    def test_should_run_when_auth_required_with_default_callback(self):
        pipeline = GRPCPipeline()
        self.assertTrue(pipeline.should_run_when_auth_required)

    def test_should_run_when_auth_required_with_custom_callback(self):
        mock_when_auth_required = Mock()
        pipeline = GRPCPipeline(when_auth_required=mock_when_auth_required)
        self.assertTrue(pipeline.should_run_when_auth_required)

    def test_should_run_when_auth_required_with_none_callback(self):
        pipeline = GRPCPipeline(when_auth_required=None)
        self.assertFalse(pipeline.should_run_when_auth_required)

    def test_should_run_when_auth_required_with_non_callable(self):
        pipeline = GRPCPipeline(when_auth_required="not callable")
        self.assertFalse(pipeline.should_run_when_auth_required)

    def test_when_auth_required_method_calls_callback_when_auth_required(self):
        mock_when_auth_required = Mock()
        pipeline = GRPCPipeline(when_auth_required=mock_when_auth_required)
        self.mock_endpoint.requires_auth = True

        pipeline.when_auth_required(self.mock_request, self.mock_response, self.mock_endpoint)

        mock_when_auth_required.assert_called_once_with(
            self.mock_request,
            self.mock_response,
            self.mock_endpoint.requirements
        )

    def test_when_auth_required_method_skips_callback_when_auth_not_required(self):
        mock_when_auth_required = Mock()
        pipeline = GRPCPipeline(when_auth_required=mock_when_auth_required)
        self.mock_endpoint.requires_auth = False

        pipeline.when_auth_required(self.mock_request, self.mock_response, self.mock_endpoint)

        mock_when_auth_required.assert_not_called()

    def test_should_run_after_all_with_default_callback(self):
        pipeline = GRPCPipeline()
        self.assertTrue(pipeline.should_run_after_all)

    def test_should_run_after_all_with_custom_callback(self):
        mock_after_all = Mock()
        pipeline = GRPCPipeline(after_all=mock_after_all)
        self.assertTrue(pipeline.should_run_after_all)

    def test_should_run_after_all_with_none_callback(self):
        pipeline = GRPCPipeline(after_all=None)
        self.assertFalse(pipeline.should_run_after_all)

    def test_should_run_after_all_with_non_callable(self):
        pipeline = GRPCPipeline(after_all="not callable")
        self.assertFalse(pipeline.should_run_after_all)

    def test_after_all_method_calls_callback(self):
        mock_after_all = Mock()
        pipeline = GRPCPipeline(after_all=mock_after_all)

        pipeline.after_all(self.mock_request, self.mock_response, self.mock_endpoint)

        mock_after_all.assert_called_once_with(
            self.mock_request,
            self.mock_response,
            self.mock_endpoint.requirements
        )

    def test_default_callbacks_do_nothing(self):
        pipeline = GRPCPipeline()

        result = pipeline.before_all(self.mock_request, self.mock_response, self.mock_endpoint)
        self.assertIsNone(result)

        result = pipeline.when_auth_required(self.mock_request, self.mock_response, self.mock_endpoint)
        self.assertIsNone(result)

        result = pipeline.after_all(self.mock_request, self.mock_response, self.mock_endpoint)
        self.assertIsNone(result)

    def test_pipeline_with_all_custom_callbacks(self):
        mock_before_all = Mock()
        mock_when_auth_required = Mock()
        mock_after_all = Mock()

        pipeline = GRPCPipeline(
            before_all=mock_before_all,
            when_auth_required=mock_when_auth_required,
            after_all=mock_after_all
        )

        self.assertTrue(pipeline.should_run_before_all)
        self.assertTrue(pipeline.should_run_when_auth_required)
        self.assertTrue(pipeline.should_run_after_all)

        pipeline.before_all(self.mock_request, self.mock_response, self.mock_endpoint)
        pipeline.when_auth_required(self.mock_request, self.mock_response, self.mock_endpoint)
        pipeline.after_all(self.mock_request, self.mock_response, self.mock_endpoint)

        mock_before_all.assert_called_once()
        mock_when_auth_required.assert_called_once()
        mock_after_all.assert_called_once()

    def test_pipeline_with_mixed_callbacks(self):
        mock_before_all = Mock()

        pipeline = GRPCPipeline(
            before_all=mock_before_all,
            when_auth_required=None,
            after_all="not callable"
        )

        self.assertTrue(pipeline.should_run_before_all)
        self.assertFalse(pipeline.should_run_when_auth_required)
        self.assertFalse(pipeline.should_run_after_all)

    def test_steps_reflect_current_state(self):
        mock_before_all = Mock()
        pipeline = GRPCPipeline(
            before_all=mock_before_all,
            when_auth_required=None
        )

        steps = pipeline.steps

        self.assertTrue(steps[0]['should_run'])
        self.assertFalse(steps[1]['should_run'])
        self.assertTrue(steps[2]['should_run'])
        self.assertTrue(steps[3]['should_run'])

    def test_stream_steps_reflect_current_state(self):
        mock_when_auth_required = Mock()
        pipeline = GRPCPipeline(
            before_all=None,
            when_auth_required=mock_when_auth_required
        )

        stream_steps = pipeline.stream_steps

        self.assertFalse(stream_steps[0]['should_run'])
        self.assertTrue(stream_steps[1]['should_run'])

    def test_endpoint_requirements_passed_correctly(self):
        mock_before_all = Mock()
        mock_when_auth_required = Mock()
        mock_after_all = Mock()

        pipeline = GRPCPipeline(
            before_all=mock_before_all,
            when_auth_required=mock_when_auth_required,
            after_all=mock_after_all
        )

        custom_requirements = {'custom': 'requirement', 'auth': True}
        self.mock_endpoint.requirements = custom_requirements

        pipeline.before_all(self.mock_request, self.mock_response, self.mock_endpoint)
        pipeline.when_auth_required(self.mock_request, self.mock_response, self.mock_endpoint)
        pipeline.after_all(self.mock_request, self.mock_response, self.mock_endpoint)

        mock_before_all.assert_called_once_with(
            self.mock_request, self.mock_response, custom_requirements
        )
        mock_when_auth_required.assert_called_once_with(
            self.mock_request, self.mock_response, custom_requirements
        )
        mock_after_all.assert_called_once_with(
            self.mock_request, self.mock_response, custom_requirements
        )

    def test_additional_kwargs_ignored(self):
        pipeline = GRPCPipeline(
            before_all=Mock(),
            unknown_param="ignored",
            another_param=123
        )

        self.assertTrue(pipeline.should_run_before_all)
        self.assertTrue(pipeline.should_run_when_auth_required)
        self.assertTrue(pipeline.should_run_after_all)

import unittest
from unittest.mock import Mock, patch
import grpc

from chilo_api.core.grpc.response import GRPCResponse
from chilo_api.core.interfaces.response import ResponseInterface


class GRPCResponseTest(unittest.TestCase):

    def setUp(self):
        self.mock_rpc_response = Mock()
        self.mock_context = Mock()

    def test_grpc_response_initialization(self):
        grpc_response = GRPCResponse(rpc_response=self.mock_rpc_response, context=self.mock_context)

        self.assertIsInstance(grpc_response, ResponseInterface)
        self.assertEqual(grpc_response.rpc_response, self.mock_rpc_response)
        self.assertEqual(grpc_response.context, self.mock_context)
        self.assertIsNone(grpc_response.body)
        self.assertEqual(grpc_response.code, 200)
        self.assertFalse(grpc_response.has_errors)

    def test_grpc_response_inherits_from_response(self):
        grpc_response = GRPCResponse(rpc_response=self.mock_rpc_response)
        self.assertTrue(issubclass(GRPCResponse, ResponseInterface))
        self.assertIsInstance(grpc_response, ResponseInterface)

    def test_initialization_without_context(self):
        grpc_response = GRPCResponse(rpc_response=self.mock_rpc_response)
        self.assertEqual(grpc_response.rpc_response, self.mock_rpc_response)
        self.assertIsNone(grpc_response.context)

    def test_body_property_getter_setter(self):
        grpc_response = GRPCResponse(rpc_response=self.mock_rpc_response)

        test_body = {'test': 'data', 'value': 123}
        grpc_response.body = test_body

        self.assertEqual(grpc_response.body, test_body)

    def test_body_property_with_none(self):
        grpc_response = GRPCResponse(rpc_response=self.mock_rpc_response)

        grpc_response.body = None
        self.assertIsNone(grpc_response.body)

    def test_code_property_getter_setter(self):
        grpc_response = GRPCResponse(rpc_response=self.mock_rpc_response)

        grpc_response.code = 404
        self.assertEqual(grpc_response.code, 404)

    def test_code_property_changes_to_400_when_has_errors(self):
        grpc_response = GRPCResponse(rpc_response=self.mock_rpc_response, context=self.mock_context)

        grpc_response.set_error("test.field", "Test error message")

        self.assertEqual(grpc_response.code, 400)
        self.assertTrue(grpc_response.has_errors)

    def test_code_property_stays_same_when_not_200_with_errors(self):
        grpc_response = GRPCResponse(rpc_response=self.mock_rpc_response, context=self.mock_context)

        grpc_response.code = 500
        grpc_response.set_error("test.field", "Test error message")

        self.assertEqual(grpc_response.code, 500)

    def test_grpc_code_property_mapping(self):
        grpc_response = GRPCResponse(rpc_response=self.mock_rpc_response)

        test_cases = [
            (200, grpc.StatusCode.OK),
            (400, grpc.StatusCode.INVALID_ARGUMENT),
            (401, grpc.StatusCode.UNAUTHENTICATED),
            (404, grpc.StatusCode.NOT_FOUND),
            (408, grpc.StatusCode.DEADLINE_EXCEEDED),
            (429, grpc.StatusCode.RESOURCE_EXHAUSTED),
            (403, grpc.StatusCode.PERMISSION_DENIED),
            (500, grpc.StatusCode.INTERNAL),
            (501, grpc.StatusCode.UNIMPLEMENTED),
            (502, grpc.StatusCode.UNAVAILABLE),
            (503, grpc.StatusCode.UNAVAILABLE),
            (504, grpc.StatusCode.DEADLINE_EXCEEDED),
            (505, grpc.StatusCode.UNIMPLEMENTED),
            (511, grpc.StatusCode.UNAVAILABLE)
        ]

        for http_code, expected_grpc_code in test_cases:
            with self.subTest(http_code=http_code):
                grpc_response.code = http_code
                self.assertEqual(grpc_response.grpc_code, expected_grpc_code)

    def test_grpc_code_property_unknown_status(self):
        grpc_response = GRPCResponse(rpc_response=self.mock_rpc_response)

        grpc_response.code = 999
        self.assertEqual(grpc_response.grpc_code, grpc.StatusCode.UNKNOWN)

    def test_context_property_getter(self):
        grpc_response = GRPCResponse(rpc_response=self.mock_rpc_response, context=self.mock_context)
        self.assertEqual(grpc_response.context, self.mock_context)

    def test_context_property_setter_does_nothing(self):
        grpc_response = GRPCResponse(rpc_response=self.mock_rpc_response, context=self.mock_context)
        original_context = grpc_response.context

        new_context = Mock()
        grpc_response.context = new_context

        self.assertEqual(grpc_response.context, original_context)
        self.assertNotEqual(grpc_response.context, new_context)

    def test_has_errors_property_initially_false(self):
        grpc_response = GRPCResponse(rpc_response=self.mock_rpc_response)
        self.assertFalse(grpc_response.has_errors)

    def test_rpc_response_property(self):
        grpc_response = GRPCResponse(rpc_response=self.mock_rpc_response)
        self.assertEqual(grpc_response.rpc_response, self.mock_rpc_response)

    def test_set_error_method(self):
        grpc_response = GRPCResponse(rpc_response=self.mock_rpc_response, context=self.mock_context)

        grpc_response.set_error("user.email", "Invalid email format")

        self.assertTrue(grpc_response.has_errors)
        self.mock_context.set_details.assert_called_once_with("user.email: Invalid email format")

    def test_set_error_multiple_times(self):
        grpc_response = GRPCResponse(rpc_response=self.mock_rpc_response, context=self.mock_context)

        grpc_response.set_error("field1", "Error 1")
        grpc_response.set_error("field2", "Error 2")

        self.assertTrue(grpc_response.has_errors)
        self.assertEqual(self.mock_context.set_details.call_count, 2)

    def test_get_response_with_successful_body(self):
        self.mock_rpc_response.return_value = "response_instance"
        grpc_response = GRPCResponse(rpc_response=self.mock_rpc_response, context=self.mock_context)

        test_body = {"user_id": 123, "name": "test"}
        grpc_response.body = test_body

        result = grpc_response.get_response()

        self.mock_context.set_code.assert_called_once_with(grpc.StatusCode.OK)
        self.mock_rpc_response.assert_called_once_with(**test_body)
        self.assertEqual(result, "response_instance")

    def test_get_response_with_none_body(self):
        self.mock_rpc_response.return_value = "empty_response"
        grpc_response = GRPCResponse(rpc_response=self.mock_rpc_response, context=self.mock_context)

        grpc_response.body = None

        result = grpc_response.get_response()

        self.mock_context.set_code.assert_called_once_with(grpc.StatusCode.OK)
        self.mock_rpc_response.assert_called_once_with()
        self.assertEqual(result, "empty_response")

    def test_get_response_with_errors(self):
        self.mock_rpc_response.return_value = "error_response"
        grpc_response = GRPCResponse(rpc_response=self.mock_rpc_response, context=self.mock_context)

        grpc_response.body = {"data": "test"}
        grpc_response.set_error("field", "error message")

        result = grpc_response.get_response()

        self.mock_context.set_code.assert_called_once_with(grpc.StatusCode.INVALID_ARGUMENT)
        self.mock_rpc_response.assert_called_once_with()
        self.assertEqual(result, "error_response")

    def test_get_response_with_custom_error_code(self):
        self.mock_rpc_response.return_value = "error_response"
        grpc_response = GRPCResponse(rpc_response=self.mock_rpc_response, context=self.mock_context)

        grpc_response.code = 500
        grpc_response.set_error("field", "server error")

        _ = grpc_response.get_response()

        self.mock_context.set_code.assert_called_once_with(grpc.StatusCode.INTERNAL)
        self.mock_rpc_response.assert_called_once_with()

    def test_get_response_with_empty_body_dict(self):
        self.mock_rpc_response.return_value = "response_with_empty_dict"
        grpc_response = GRPCResponse(rpc_response=self.mock_rpc_response, context=self.mock_context)

        grpc_response.body = {}

        result = grpc_response.get_response()

        self.mock_context.set_code.assert_called_once_with(grpc.StatusCode.OK)
        self.mock_rpc_response.assert_called_once_with()
        self.assertEqual(result, "response_with_empty_dict")

    def test_error_affects_code_property(self):
        grpc_response = GRPCResponse(rpc_response=self.mock_rpc_response, context=self.mock_context)

        initial_code = grpc_response.code
        self.assertEqual(initial_code, 200)

        grpc_response.set_error("test", "error")

        error_code = grpc_response.code
        self.assertEqual(error_code, 400)

    def test_initialization_with_additional_kwargs(self):
        grpc_response = GRPCResponse(
            rpc_response=self.mock_rpc_response,
            context=self.mock_context,
            extra_param="ignored"
        )

        self.assertEqual(grpc_response.rpc_response, self.mock_rpc_response)
        self.assertEqual(grpc_response.context, self.mock_context)

    def test_body_with_complex_data_structures(self):
        grpc_response = GRPCResponse(rpc_response=self.mock_rpc_response)

        complex_body = {
            "users": [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}],
            "metadata": {"total": 2, "page": 1},
            "nested": {"deep": {"value": "test"}}
        }

        grpc_response.body = complex_body
        self.assertEqual(grpc_response.body, complex_body)

    def test_multiple_grpc_responses(self):
        responses = []

        for _ in range(3):
            mock_rpc = Mock()
            mock_ctx = Mock()
            grpc_response = GRPCResponse(rpc_response=mock_rpc, context=mock_ctx)

            responses.append(grpc_response)

            self.assertEqual(grpc_response.rpc_response, mock_rpc)
            self.assertEqual(grpc_response.context, mock_ctx)
            self.assertFalse(grpc_response.has_errors)

    def test_inheritance_chain(self):
        _ = GRPCResponse(rpc_response=self.mock_rpc_response)

        mro = GRPCResponse.__mro__
        self.assertIn(ResponseInterface, mro)
        self.assertEqual(mro[0], GRPCResponse)
        self.assertEqual(mro[1], ResponseInterface)

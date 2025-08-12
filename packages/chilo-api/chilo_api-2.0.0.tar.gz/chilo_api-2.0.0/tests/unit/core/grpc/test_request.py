import unittest
from unittest.mock import Mock, patch

from chilo_api.core.grpc.request import GRPCRequest
from chilo_api.core.interfaces.request import RequestInterface


class GRPCRequestTest(unittest.TestCase):

    def setUp(self):
        self.mock_rpc_request = Mock()
        self.mock_context = Mock()

    def test_api_type(self):
        grpc_request = GRPCRequest(self.mock_rpc_request, self.mock_context)
        self.assertEqual('grpc', grpc_request.api_type)

    def test_grpc_request_initialization(self):
        grpc_request = GRPCRequest(self.mock_rpc_request, self.mock_context)
        self.assertEqual(grpc_request.raw, self.mock_rpc_request)
        self.assertEqual(grpc_request.context, self.mock_context)

    def test_grpc_request_inherits_from_request(self):
        grpc_request = GRPCRequest(self.mock_rpc_request, self.mock_context)
        self.assertTrue(issubclass(GRPCRequest, RequestInterface))
        self.assertIsInstance(grpc_request, RequestInterface)

    @patch('chilo_api.core.grpc.request.MessageToDict')
    def test_body_property_successful_conversion(self, mock_message_to_dict):
        expected_dict = {'user_id': 123, 'username': 'testuser', 'email': 'test@example.com'}
        mock_message_to_dict.return_value = expected_dict

        grpc_request = GRPCRequest(self.mock_rpc_request, self.mock_context)
        result = grpc_request.body

        mock_message_to_dict.assert_called_once_with(
            self.mock_rpc_request,
            preserving_proto_field_name=True
        )
        self.assertEqual(result, expected_dict)

    @patch('chilo_api.core.grpc.request.MessageToDict')
    def test_protobuf_property_successful_conversion(self, mock_message_to_dict):
        expected_dict = {'user_id': 123, 'username': 'testuser', 'email': 'test@example.com'}
        mock_message_to_dict.return_value = expected_dict

        grpc_request = GRPCRequest(self.mock_rpc_request, self.mock_context)
        result = grpc_request.protobuf

        mock_message_to_dict.assert_called_once_with(
            self.mock_rpc_request,
            preserving_proto_field_name=True
        )
        self.assertEqual(result, expected_dict)

    @patch('chilo_api.core.grpc.request.MessageToDict')
    def test_json_property_successful_conversion(self, mock_message_to_dict):
        expected_dict = {'user_id': 123, 'username': 'testuser', 'email': 'test@example.com'}
        mock_message_to_dict.return_value = expected_dict

        grpc_request = GRPCRequest(self.mock_rpc_request, self.mock_context)
        result = grpc_request.json

        mock_message_to_dict.assert_called_once_with(
            self.mock_rpc_request,
            preserving_proto_field_name=True
        )
        self.assertEqual(result, expected_dict)

        mock_message_to_dict.assert_called_once_with(
            self.mock_rpc_request,
            preserving_proto_field_name=True
        )
        self.assertEqual(result, expected_dict)

    @patch('chilo_api.core.grpc.request.MessageToDict')
    def test_body_property_conversion_fails_returns_raw(self, mock_message_to_dict):
        mock_message_to_dict.side_effect = Exception("Conversion failed")

        grpc_request = GRPCRequest(self.mock_rpc_request, self.mock_context)
        result = grpc_request.body

        mock_message_to_dict.assert_called_once_with(
            self.mock_rpc_request,
            preserving_proto_field_name=True
        )
        self.assertEqual(result, self.mock_rpc_request)

    def test_raw_property_returns_rpc_request(self):
        grpc_request = GRPCRequest(self.mock_rpc_request, self.mock_context)
        self.assertEqual(grpc_request.raw, self.mock_rpc_request)

    def test_context_property_returns_context(self):
        grpc_request = GRPCRequest(self.mock_rpc_request, self.mock_context)
        self.assertEqual(grpc_request.context, self.mock_context)

    def test_context_setter_does_nothing(self):
        grpc_request = GRPCRequest(self.mock_rpc_request, self.mock_context)
        original_context = grpc_request.context

        new_context = Mock()
        grpc_request.context = new_context

        self.assertEqual(grpc_request.context, original_context)
        self.assertNotEqual(grpc_request.context, new_context)

    def test_grpc_request_with_none_values(self):
        grpc_request = GRPCRequest(None, None)
        self.assertIsNone(grpc_request.raw)
        self.assertIsNone(grpc_request.context)

    @patch('chilo_api.core.grpc.request.MessageToDict')
    def test_body_with_none_rpc_request(self, mock_message_to_dict):
        mock_message_to_dict.side_effect = Exception("Cannot convert None")

        grpc_request = GRPCRequest(None, self.mock_context)
        result = grpc_request.body

        self.assertIsNone(result)

    @patch('chilo_api.core.grpc.request.MessageToDict')
    def test_body_with_various_exception_types(self, mock_message_to_dict):
        exception_types = [
            ValueError("Invalid message"),
            TypeError("Type error"),
            AttributeError("Attribute error"),
            RuntimeError("Runtime error")
        ]

        for exception in exception_types:
            with self.subTest(exception=exception):
                mock_message_to_dict.side_effect = exception
                grpc_request = GRPCRequest(self.mock_rpc_request, self.mock_context)
                result = grpc_request.body
                self.assertEqual(result, self.mock_rpc_request)

    @patch('chilo_api.core.grpc.request.MessageToDict')
    def test_body_property_preserves_proto_field_names(self, mock_message_to_dict):
        expected_dict = {'proto_field_name': 'value', 'another_field': 123}
        mock_message_to_dict.return_value = expected_dict

        grpc_request = GRPCRequest(self.mock_rpc_request, self.mock_context)
        result = grpc_request.body

        mock_message_to_dict.assert_called_once_with(
            self.mock_rpc_request,
            preserving_proto_field_name=True
        )
        self.assertEqual(result, expected_dict)

    def test_grpc_request_inheritance_chain(self):
        _ = GRPCRequest(self.mock_rpc_request, self.mock_context)
        mro = GRPCRequest.__mro__
        self.assertIn(RequestInterface, mro)
        self.assertEqual(mro[0], GRPCRequest)
        self.assertEqual(mro[1], RequestInterface)

    def test_multiple_grpc_requests(self):
        requests = []
        contexts = []

        for _ in range(3):
            mock_req = Mock()
            mock_ctx = Mock()
            grpc_request = GRPCRequest(mock_req, mock_ctx)

            requests.append(mock_req)
            contexts.append(mock_ctx)

            self.assertEqual(grpc_request.raw, mock_req)
            self.assertEqual(grpc_request.context, mock_ctx)

    @patch('chilo_api.core.grpc.request.MessageToDict')
    def test_body_property_called_multiple_times(self, mock_message_to_dict):
        expected_dict = {'test': 'data'}
        mock_message_to_dict.return_value = expected_dict

        grpc_request = GRPCRequest(self.mock_rpc_request, self.mock_context)

        result1 = grpc_request.body
        result2 = grpc_request.body
        result3 = grpc_request.body

        self.assertEqual(mock_message_to_dict.call_count, 3)
        self.assertEqual(result1, expected_dict)
        self.assertEqual(result2, expected_dict)
        self.assertEqual(result3, expected_dict)

import unittest
from unittest.mock import Mock, patch
from types import ModuleType, GeneratorType
import json

from chilo_api.core.grpc.endpoint import GRPCEndpoint


class GRPCEndpointTest(unittest.TestCase):

    def setUp(self):
        self.default_kwargs = {
            'service': 'TestService',
            'requirements': {'auth_required': True, 'custom': 'value'},
            'protobuf': 'test.proto',
            'rpc_request_name': 'TestMethod',
            'rpc_request_method': Mock()
        }
        self.mock_request = Mock()
        self.mock_response = Mock()
        self.mock_response.get_response.return_value = "response_result"

    def test_initialization_with_required_kwargs(self):
        endpoint = GRPCEndpoint(**self.default_kwargs)

        self.assertEqual(endpoint.service, 'TestService')
        self.assertEqual(endpoint.requirements, {'auth_required': True, 'custom': 'value'})
        self.assertEqual(endpoint.protobuf, 'test.proto')
        self.assertEqual(endpoint.rpc_request_name, 'TestMethod')
        self.assertEqual(endpoint.rpc_request_method, self.default_kwargs['rpc_request_method'])

    def test_initialization_sets_default_values(self):
        endpoint = GRPCEndpoint(**self.default_kwargs)

        self.assertIsNone(endpoint.servicer)
        self.assertIsNone(endpoint.dynamic_servicer)
        self.assertFalse(endpoint.response_is_stream)
        self.assertEqual(endpoint.rpc_response_name, '')
        self.assertIsNone(endpoint.rpc_response)
        self.assertIsNone(endpoint.add_server_method)

    def test_service_property(self):
        endpoint = GRPCEndpoint(**self.default_kwargs)
        self.assertEqual(endpoint.service, 'TestService')

    def test_servicer_class_name_property(self):
        endpoint = GRPCEndpoint(**self.default_kwargs)
        self.assertEqual(endpoint.servicer_class_name, 'TestServiceServicer')

    def test_servicer_property_getter_setter(self):
        endpoint = GRPCEndpoint(**self.default_kwargs)
        mock_servicer = Mock()

        self.assertIsNone(endpoint.servicer)

        endpoint.servicer = mock_servicer
        self.assertEqual(endpoint.servicer, mock_servicer)

    def test_name_property(self):
        endpoint = GRPCEndpoint(**self.default_kwargs)
        self.assertEqual(endpoint.name, 'TestService.TestMethod')

    def test_protobuf_property(self):
        endpoint = GRPCEndpoint(**self.default_kwargs)
        self.assertEqual(endpoint.protobuf, 'test.proto')

    def test_requirements_property(self):
        endpoint = GRPCEndpoint(**self.default_kwargs)
        self.assertEqual(endpoint.requirements, {'auth_required': True, 'custom': 'value'})

    def test_has_requirements_property_with_requirements(self):
        endpoint = GRPCEndpoint(**self.default_kwargs)
        self.assertTrue(endpoint.has_requirements)

    def test_has_requirements_property_without_requirements(self):
        kwargs = self.default_kwargs.copy()
        kwargs['requirements'] = {}
        endpoint = GRPCEndpoint(**kwargs)
        self.assertFalse(endpoint.has_requirements)

    def test_requires_auth_property_when_auth_required_true(self):
        endpoint = GRPCEndpoint(**self.default_kwargs)
        self.assertTrue(endpoint.requires_auth)

    def test_requires_auth_property_when_auth_required_false(self):
        kwargs = self.default_kwargs.copy()
        kwargs['requirements'] = {'auth_required': False}
        endpoint = GRPCEndpoint(**kwargs)
        self.assertFalse(endpoint.requires_auth)

    def test_requires_auth_property_when_auth_not_specified(self):
        kwargs = self.default_kwargs.copy()
        kwargs['requirements'] = {'other': 'value'}
        endpoint = GRPCEndpoint(**kwargs)
        self.assertIsNone(endpoint.requires_auth)

    def test_rpc_request_name_property(self):
        endpoint = GRPCEndpoint(**self.default_kwargs)
        self.assertEqual(endpoint.rpc_request_name, 'TestMethod')

    def test_rpc_response_name_property_getter_setter(self):
        endpoint = GRPCEndpoint(**self.default_kwargs)

        self.assertEqual(endpoint.rpc_response_name, '')

        endpoint.rpc_response_name = 'TestResponse'
        self.assertEqual(endpoint.rpc_response_name, 'TestResponse')

    def test_rpc_response_property_getter_setter(self):
        endpoint = GRPCEndpoint(**self.default_kwargs)
        mock_response = Mock()

        self.assertIsNone(endpoint.rpc_response)

        endpoint.rpc_response = mock_response
        self.assertEqual(endpoint.rpc_response, mock_response)

    def test_dynamic_servicer_property_getter_setter(self):
        endpoint = GRPCEndpoint(**self.default_kwargs)
        mock_dynamic_servicer = Mock()

        self.assertIsNone(endpoint.dynamic_servicer)

        endpoint.dynamic_servicer = mock_dynamic_servicer
        self.assertEqual(endpoint.dynamic_servicer, mock_dynamic_servicer)

    def test_add_server_method_property_getter_setter(self):
        endpoint = GRPCEndpoint(**self.default_kwargs)
        mock_add_server_method = Mock()

        self.assertIsNone(endpoint.add_server_method)

        endpoint.add_server_method = mock_add_server_method
        self.assertEqual(endpoint.add_server_method, mock_add_server_method)

    def test_response_is_stream_property_getter_setter(self):
        endpoint = GRPCEndpoint(**self.default_kwargs)

        self.assertFalse(endpoint.response_is_stream)

        endpoint.response_is_stream = True
        self.assertTrue(endpoint.response_is_stream)

    def test_rpc_request_method_property(self):
        endpoint = GRPCEndpoint(**self.default_kwargs)
        self.assertEqual(endpoint.rpc_request_method, self.default_kwargs['rpc_request_method'])

    def test_run_method_calls_rpc_request_method_and_returns_response(self):
        endpoint = GRPCEndpoint(**self.default_kwargs)

        result = endpoint.run(self.mock_request, self.mock_response)

        self.default_kwargs['rpc_request_method'].assert_called_once_with(self.mock_request, self.mock_response)
        self.mock_response.get_response.assert_called_once()
        self.assertEqual(result, "response_result")

    def test_stream_method_yields_from_rpc_request_method(self):
        mock_rpc_method = Mock()
        mock_rpc_method.return_value = iter(['chunk1', 'chunk2', 'chunk3'])

        kwargs = self.default_kwargs.copy()
        kwargs['rpc_request_method'] = mock_rpc_method
        endpoint = GRPCEndpoint(**kwargs)

        result = endpoint.stream(self.mock_request, self.mock_response)

        self.assertIsInstance(result, GeneratorType)
        collected_data = list(result)

        mock_rpc_method.assert_called_once_with(self.mock_request, self.mock_response)
        self.assertEqual(collected_data, ['chunk1', 'chunk2', 'chunk3'])

    def test_get_endpoints_from_module_with_valid_functions(self):
        mock_module = Mock(spec=ModuleType)

        mock_func1 = Mock()
        mock_func1.requirements = {
            'protobuf': 'test1.proto',
            'service': 'Service1',
            'rpc': 'Method1'
        }

        mock_func2 = Mock()
        mock_func2.requirements = {
            'protobuf': 'test2.proto',
            'service': 'Service2',
            'rpc': 'Method2'
        }

        mock_func3 = Mock()
        mock_func3.requirements = {}

        setattr(mock_module, 'func1', mock_func1)
        setattr(mock_module, 'func2', mock_func2)
        setattr(mock_module, 'func3', mock_func3)

        with patch('builtins.dir', return_value=['func1', 'func2', 'func3', '__init__']):
            endpoints = GRPCEndpoint.get_endpoints_from_module(mock_module)

            self.assertEqual(len(endpoints), 2)
            self.assertEqual(endpoints[0].service, 'Service1')
            self.assertEqual(endpoints[0].rpc_request_name, 'Method1')
            self.assertEqual(endpoints[1].service, 'Service2')
            self.assertEqual(endpoints[1].rpc_request_name, 'Method2')

    def test_get_endpoints_from_module_with_no_valid_functions(self):
        mock_module = Mock(spec=ModuleType)

        mock_func1 = Mock()
        mock_func1.requirements = {'protobuf': 'test.proto'}

        mock_func2 = Mock()
        mock_func2.requirements = {'service': 'TestService'}

        setattr(mock_module, 'func1', mock_func1)
        setattr(mock_module, 'func2', mock_func2)

        with patch('builtins.dir', return_value=['func1', 'func2']):
            endpoints = GRPCEndpoint.get_endpoints_from_module(mock_module)

            self.assertEqual(len(endpoints), 0)

    def test_get_endpoints_from_module_with_missing_requirements(self):
        mock_module = Mock(spec=ModuleType)

        mock_func = Mock(spec=[])

        setattr(mock_module, 'func', mock_func)

        with patch('builtins.dir', return_value=['func']):
            endpoints = GRPCEndpoint.get_endpoints_from_module(mock_module)

            self.assertEqual(len(endpoints), 0)

    def test_str_method_returns_json_representation(self):
        endpoint = GRPCEndpoint(**self.default_kwargs)
        endpoint.servicer = Mock()
        endpoint.dynamic_servicer = Mock()
        endpoint.add_server_method = Mock()
        endpoint.rpc_response_name = 'TestResponse'
        endpoint.rpc_response = Mock()

        result = endpoint.__str__()

        self.assertIsInstance(result, str)
        parsed_json = json.loads(result)

        self.assertEqual(parsed_json['service'], 'TestService')
        self.assertEqual(parsed_json['servicer_class_name'], 'TestServiceServicer')
        self.assertEqual(parsed_json['rpc_request_name'], 'TestMethod')
        self.assertEqual(parsed_json['rpc_response_name'], 'TestResponse')
        self.assertEqual(parsed_json['requirements'], {'auth_required': True, 'custom': 'value'})
        self.assertEqual(parsed_json['protobuf'], 'test.proto')

    def test_multiple_endpoints_are_independent(self):
        kwargs1 = {
            'service': 'Service1',
            'requirements': {'auth_required': True},
            'protobuf': 'test1.proto',
            'rpc_request_name': 'Method1',
            'rpc_request_method': Mock()
        }

        kwargs2 = {
            'service': 'Service2',
            'requirements': {'auth_required': False},
            'protobuf': 'test2.proto',
            'rpc_request_name': 'Method2',
            'rpc_request_method': Mock()
        }

        endpoint1 = GRPCEndpoint(**kwargs1)
        endpoint2 = GRPCEndpoint(**kwargs2)

        self.assertNotEqual(endpoint1.service, endpoint2.service)
        self.assertNotEqual(endpoint1.requirements, endpoint2.requirements)
        self.assertNotEqual(endpoint1.rpc_request_method, endpoint2.rpc_request_method)

    def test_property_setters_modify_values(self):
        endpoint = GRPCEndpoint(**self.default_kwargs)

        mock_servicer = Mock()
        mock_dynamic_servicer = Mock()
        mock_add_server_method = Mock()
        mock_rpc_response = Mock()

        endpoint.servicer = mock_servicer
        endpoint.dynamic_servicer = mock_dynamic_servicer
        endpoint.add_server_method = mock_add_server_method
        endpoint.rpc_response_name = 'NewResponse'
        endpoint.rpc_response = mock_rpc_response
        endpoint.response_is_stream = True

        self.assertEqual(endpoint.servicer, mock_servicer)
        self.assertEqual(endpoint.dynamic_servicer, mock_dynamic_servicer)
        self.assertEqual(endpoint.add_server_method, mock_add_server_method)
        self.assertEqual(endpoint.rpc_response_name, 'NewResponse')
        self.assertEqual(endpoint.rpc_response, mock_rpc_response)
        self.assertTrue(endpoint.response_is_stream)

    def test_run_with_different_request_response_objects(self):
        endpoint = GRPCEndpoint(**self.default_kwargs)

        request1 = Mock()
        response1 = Mock()
        response1.get_response.return_value = "result1"

        request2 = Mock()
        response2 = Mock()
        response2.get_response.return_value = "result2"

        result1 = endpoint.run(request1, response1)
        result2 = endpoint.run(request2, response2)

        self.assertEqual(result1, "result1")
        self.assertEqual(result2, "result2")

        self.assertEqual(self.default_kwargs['rpc_request_method'].call_count, 2)

    def test_stream_with_empty_generator(self):
        mock_rpc_method = Mock()
        mock_rpc_method.return_value = iter([])

        kwargs = self.default_kwargs.copy()
        kwargs['rpc_request_method'] = mock_rpc_method
        endpoint = GRPCEndpoint(**kwargs)

        result = endpoint.stream(self.mock_request, self.mock_response)
        collected_data = list(result)

        self.assertEqual(collected_data, [])
        mock_rpc_method.assert_called_once_with(self.mock_request, self.mock_response)

    def test_name_property_with_different_services_and_methods(self):
        test_cases = [
            ('UserService', 'GetUser', 'UserService.GetUser'),
            ('OrderService', 'CreateOrder', 'OrderService.CreateOrder'),
            ('PaymentService', 'ProcessPayment', 'PaymentService.ProcessPayment')
        ]

        for service, method, expected_name in test_cases:
            with self.subTest(service=service, method=method):
                kwargs = self.default_kwargs.copy()
                kwargs['service'] = service
                kwargs['rpc_request_name'] = method

                endpoint = GRPCEndpoint(**kwargs)
                self.assertEqual(endpoint.name, expected_name)

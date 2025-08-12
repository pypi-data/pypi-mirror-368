import json
from unittest import TestCase
from unittest.mock import Mock
from types import ModuleType

from tests.unit.mocks.rest.common.environment_builder import EnvironmentBuilder

from chilo_api.core.rest.endpoint import Endpoint
from chilo_api.core.resolver.importer import ResolverImporter
from chilo_api.core.rest.request import RestRequest as Request
from chilo_api.core.rest.response import RestResponse as Response
from chilo_api.core.exception import ApiException


class EndpointTest(TestCase):
    handler_path = 'tests/unit/mocks/rest/handlers/valid'
    file_path = f'{handler_path}/basic.py'
    import_path = 'tests.mocks.handlers.basic'
    environ = EnvironmentBuilder()

    def setUp(self):
        self.request = Mock(spec=Request)
        self.response = Mock(spec=Response)

    def __get_endpoint_instance(self, method):
        importer = ResolverImporter(handlers=self.handler_path)
        endpoint_module = importer.get_imported_module_from_file(self.file_path, self.import_path)
        return Endpoint(endpoint_module, method)

    def test_module(self):
        endpoint = self.__get_endpoint_instance('post')
        self.assertEqual('tests.mocks.handlers.basic', endpoint.module.__name__)

    def test_endpoint_initializes(self):
        endpoint = self.__get_endpoint_instance('post')
        self.assertIsInstance(endpoint, Endpoint)

    def test_endpoint_has_requirements(self):
        endpoint = self.__get_endpoint_instance('post')
        self.assertTrue(endpoint.has_requirements)

    def test_endpoint_has_no_requirements(self):
        endpoint = self.__get_endpoint_instance('patch')
        self.assertFalse(endpoint.has_requirements)

    def test_endpoint_requires_auth(self):
        endpoint = self.__get_endpoint_instance('post')
        self.assertTrue(endpoint.requires_auth)

    def test_endpoint_has_required_response(self):
        endpoint = self.__get_endpoint_instance('search')
        self.assertTrue(endpoint.has_required_response)

    def test_endpoint_has_required_route(self):
        endpoint = self.__get_endpoint_instance('delete')
        self.assertTrue(endpoint.has_required_route)
        self.assertEqual('/some/route/{id}', endpoint.required_route)

    def test_endpoint_supports_custom_requirements(self):
        endpoint = self.__get_endpoint_instance('put')
        self.assertTrue(endpoint.has_requirements)
        self.assertDictEqual({'custom_list': [1, 2, 3], 'custom_dict': {'key': 'value'}, 'custom_simple': 1}, endpoint.requirements)

    def test_endpoint_runs_with_requirements(self):
        endpoint = self.__get_endpoint_instance('post')
        response = self.environ.get_response()
        request = self.environ.get_request()
        result = endpoint.run(request, response)
        body = next(result.get_response()).decode('utf-8')
        self.assertDictEqual({'router_directory_basic': ''}, json.loads(body))

    def test_endpoint_runs_without_requirements(self):
        endpoint = self.__get_endpoint_instance('patch')
        response = self.environ.get_response()
        request = self.environ.get_request()
        result = endpoint.run(request, response)
        body = next(result.get_response()).decode('utf-8')
        self.assertEqual({'router_directory_basic': 'PATCH'}, json.loads(body))

    def test_run_options(self):
        endpoint = self.__get_endpoint_instance('options')
        response = self.environ.get_response()
        request = self.environ.get_request()
        result = endpoint.run(request, response)
        control_methods = result.headers['Access-Control-Request-Method']
        self.assertEqual('DELETE,GET,PATCH,POST,PUT', control_methods)

    def test_run_head(self):
        endpoint = self.__get_endpoint_instance('head')
        response = self.environ.get_response()
        request = self.environ.get_request()
        result = endpoint.run(request, response)
        x_header = result.headers['x-new-header']
        self.assertEqual('NEW-HEADER', x_header)

    def test_stream_with_valid_module_method(self):
        mock_module = Mock(spec=ModuleType)

        def mock_stream_method(request, response):
            yield {'chunk': 1, 'data': 'first'}
            yield {'chunk': 2, 'data': 'second'}
            yield {'chunk': 3, 'data': 'third'}

        mock_module.stream = mock_stream_method
        endpoint = Endpoint(mock_module, 'stream')
        generator = endpoint.stream(self.request, self.response)
        results = list(generator)
        expected = [
            {'chunk': 1, 'data': 'first'},
            {'chunk': 2, 'data': 'second'},
            {'chunk': 3, 'data': 'third'}
        ]
        self.assertEqual(results, expected)

    def test_stream_with_single_yield(self):
        mock_module = Mock(spec=ModuleType)

        def mock_stream_method(request, response):
            yield {'message': 'single response'}

        mock_module.stream = mock_stream_method
        endpoint = Endpoint(mock_module, 'stream')
        generator = endpoint.stream(self.request, self.response)
        result = next(generator)
        self.assertEqual(result, {'message': 'single response'})
        with self.assertRaises(StopIteration):
            next(generator)

    def test_stream_with_empty_generator(self):
        mock_module = Mock(spec=ModuleType)

        def mock_stream_method(request, response):
            return
            yield  # NOSONAR type: ignore

        mock_module.stream = mock_stream_method
        endpoint = Endpoint(mock_module, 'stream')
        generator = endpoint.stream(self.request, self.response)
        results = list(generator)
        self.assertEqual(results, [])

    def test_stream_with_none_module_method(self):
        mock_module = Mock(spec=ModuleType)
        endpoint = Endpoint(mock_module, 'options')
        with self.assertRaises(ApiException) as context:
            generator = endpoint.stream(self.request, self.response)
            list(generator)

        self.assertEqual(context.exception.code, 1011)
        self.assertEqual(context.exception.message, 'Stream connection not allowed for this endpoint')

    def test_stream_with_head_method(self):
        mock_module = Mock(spec=ModuleType)
        endpoint = Endpoint(mock_module, 'head')
        with self.assertRaises(ApiException) as context:
            generator = endpoint.stream(self.request, self.response)
            list(generator)

        self.assertEqual(context.exception.code, 1011)
        self.assertEqual(context.exception.message, 'Stream connection not allowed for this endpoint')

    def test_stream_passes_request_and_response_to_module_method(self):
        mock_module = Mock(spec=ModuleType)
        mock_stream_method = Mock()
        mock_stream_method.return_value = iter([{'test': 'data'}])
        mock_module.stream = mock_stream_method
        endpoint = Endpoint(mock_module, 'stream')
        generator = endpoint.stream(self.request, self.response)
        list(generator)
        mock_stream_method.assert_called_once_with(self.request, self.response)

    def test_stream_returns_generator(self):
        mock_module = Mock(spec=ModuleType)

        def mock_stream_method(request, response):
            yield {'test': 'data'}

        mock_module.stream = mock_stream_method
        endpoint = Endpoint(mock_module, 'stream')
        result = endpoint.stream(self.request, self.response)
        self.assertTrue(hasattr(result, '__iter__'))
        self.assertTrue(hasattr(result, '__next__'))

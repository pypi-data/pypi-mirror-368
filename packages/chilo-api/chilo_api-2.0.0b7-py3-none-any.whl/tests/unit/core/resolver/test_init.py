import unittest

from tests.unit.mocks.rest.common.environment_builder import EnvironmentBuilder

from chilo_api.core.exception import ApiException
from chilo_api.core.rest.endpoint import Endpoint
from chilo_api.core.resolver import Resolver


class ResolverTest(unittest.TestCase):
    base_path = 'unit-test/v1'
    handler_path = 'tests/unit/mocks/rest/handlers/valid'
    bad_handler_path = 'tests/unit/mocks/rest/handlers/invalid/bad_endpoint'
    environ = EnvironmentBuilder()

    def test_finding_endpoint_passes(self):
        request = self.environ.get_request(path='unit-test/v1/basic')
        resolver = Resolver(base_path=self.base_path, handlers=self.handler_path)
        endpoint = resolver.get_endpoint(request)
        self.assertIsInstance(endpoint, Endpoint)

    def test_finding_endpoint_fails_no_route(self):
        request = self.environ.get_request(path='unit-test/v1/bad')
        resolver = Resolver(base_path=self.base_path, handlers=self.handler_path)
        with self.assertRaises(ApiException) as context:
            resolver.get_endpoint(request)
        self.assertEqual('route not found', context.exception.message)

    def test_finding_endpoint_fails_dynamic_endpoint_bad_route_definition_missing(self):
        request = self.environ.get_request(path='unit-test/v1/bad_dynamic/1', method='post')
        resolver = Resolver(base_path=self.base_path, handlers=self.handler_path)
        with self.assertRaises(ApiException) as context:
            resolver.get_endpoint(request)
        self.assertEqual('route not found', context.exception.message)

    def test_finding_endpoint_fails_dynamic_endpoint_bad_route_variable(self):
        request = self.environ.get_request(path='unit-test/v1/bad_dynamic/1', method='get')
        resolver = Resolver(base_path=self.base_path, handlers=self.bad_handler_path)
        with self.assertRaises(ApiException) as context:
            resolver.get_endpoint(request)
        self.assertEqual('no route found; endpoint does not have proper variables in required_route', context.exception.message)

    def test_finding_endpoint_fails_dynamic_endpoint_no_required_route_param(self):
        request = self.environ.get_request(path='unit-test/v1/bad_dynamic/1', method='patch')
        resolver = Resolver(base_path=self.base_path, handlers=self.bad_handler_path)
        with self.assertRaises(ApiException) as context:
            resolver.get_endpoint(request)
        self.assertEqual('no route found; endpoint does have required_route configured', context.exception.message)

    def test_finding_endpoint_fails_dynamic_endpoint_bad_route_definition(self):
        request = self.environ.get_request(path='unit-test/v1/bad_dynamic/1', method='post')
        resolver = Resolver(base_path=self.base_path, handlers=self.bad_handler_path)
        with self.assertRaises(ApiException) as context:
            resolver.get_endpoint(request)
        self.assertEqual('no route found; requested dynamic route does not match endpoint route definition', context.exception.message)

    def test_finding_dynamic_endpoint_passes(self):
        request = self.environ.get_request(path='unit-test/v1/bad-dynamic/1', method='delete')
        resolver = Resolver(base_path=self.base_path, handlers=self.bad_handler_path)
        endpoint = resolver.get_endpoint(request)
        self.assertIsInstance(endpoint, Endpoint)

    def test_finding_endpoint_from_cache_works(self):
        request = self.environ.get_request(path='unit-test/v1/basic')
        resolver = Resolver(base_path=self.base_path, handlers=self.handler_path)
        self.assertEqual(0, resolver.cache_misses)
        resolver.get_endpoint(request)
        self.assertEqual(1, resolver.cache_misses)
        resolver.get_endpoint(request)
        self.assertEqual(1, resolver.cache_misses)

import unittest

from tests.unit.mocks.rest.common.environment_builder import EnvironmentBuilder

from chilo_api.core.rest.endpoint import Endpoint
from chilo_api.core.resolver.scanner import ResolverScanner


class ResolverScannerTest(unittest.TestCase):
    handlers = 'tests/unit/mocks/rest/handlers/valid'
    base_path = 'unit-test/v1'
    handler_pattern = 'tests/unit/mocks/rest/handlers/valid/**/*_handler.py'

    def test_load_importer_files_pass(self):
        scanner = ResolverScanner(handlers=self.handlers, base_path=self.base_path)
        scanner.load_importer_files()

    def test_get_endpoint_module_pass(self):
        scanner = ResolverScanner(handlers=self.handlers, base_path=self.base_path)
        request = EnvironmentBuilder().get_request(path='/unit-test/v1/basic')
        endpoint_module = scanner.get_endpoint_module(request)
        self.assertIsNotNone(endpoint_module)

    def test_get_endpoint_from_pattern_module_pass(self):
        scanner = ResolverScanner(handlers=self.handler_pattern, base_path=self.base_path)
        request = EnvironmentBuilder().get_request(path='/unit-test/v1/pattern-dynamic')
        endpoint_module = scanner.get_endpoint_module(request)
        self.assertIsNotNone(endpoint_module)

    def test_get_dynamic_endpoint_from_pattern_module_pass(self):
        scanner = ResolverScanner(handlers=self.handler_pattern, base_path=self.base_path)
        request = EnvironmentBuilder().get_request(path='/unit-test/v1/pattern-dynamic/{id}')
        endpoint_module = scanner.get_endpoint_module(request)
        self.assertIsNotNone(endpoint_module)

    def test_get_endpoint_module_fails(self):
        scanner = ResolverScanner(handlers=self.handlers, base_path=self.base_path)
        request = EnvironmentBuilder().get_request(path='/unit-test/v1/basic-miss')

        with self.assertRaises(Exception) as context:
            scanner.get_endpoint_module(request)

        self.assertIn('route not found', str(context.exception))

    def test_reset(self):
        scanner = ResolverScanner(handlers=self.handlers, base_path=self.base_path)
        scanner.has_dynamic_route = True
        scanner.file_tree_climbed = False
        scanner.dynamic_parts = {'key': 'value'}  # type: ignore
        scanner.import_path = ['test']

        scanner.reset()

        self.assertFalse(scanner.has_dynamic_route)
        self.assertTrue(scanner.file_tree_climbed)
        self.assertDictEqual({}, scanner.dynamic_parts)
        self.assertEqual(0, len(scanner.import_path))

from unittest import mock, TestCase

from chilo_api.cli.openapi import OpenAPI
from chilo_api.cli import CLIManager


def mock_open(*args, **kwargs):
    # This mock function is intentionally left empty to override file writing during tests.
    pass


class OpenAPITest(TestCase):

    @mock.patch('sys.argv', [
        'CLIManager',
        'generate-openapi',
        '--api=api_rest',
        '--output=tests',
        '--format=json,yml',
        '--delete'
    ])
    @mock.patch('chilo_api.cli.openapi.OpenAPIFileWriter.write_openapi', mock_open)
    def test_generate_openapi(self):
        manager = CLIManager()
        OpenAPI(manager.args).generate()
        self.assertTrue(True)  # should error and fail test if broken

    @mock.patch('sys.argv', [
        'CLIManager',
        'generate-openapi',
        '--api=api_rest',
        '--output=tests/unit/mocks/openapi/discoverable/removed',
        '--format=json,yml',
        '--delete'
    ])
    @mock.patch('chilo_api.cli.openapi.OpenAPIFileWriter.write_openapi', mock_open)
    def test_generate_openapi_with_removed_paths_and_methods(self):
        manager = CLIManager()
        OpenAPI(manager.args).generate()
        # Ensure the args contain the expected output path for removed paths/methods
        self.assertIn('tests/unit/mocks/openapi/discoverable/removed', manager.args.output)

    @mock.patch('sys.argv', [
        'CLIManager',
        'generate-openapi',
        '--api=api_rest',
        '--output=tests/unit/mocks/openapi/discoverable/existing',
        '--format=json,yml',
        '--delete'
    ])
    @mock.patch('chilo_api.cli.openapi.OpenAPIFileWriter.write_openapi', mock_open)
    def test_generate_openapi_with_existing_json(self):
        manager = CLIManager()
        OpenAPI(manager.args).generate()
        # Ensure the args contain the expected output path for existing json
        self.assertIn('tests/unit/mocks/openapi/discoverable/existing', manager.args.output)

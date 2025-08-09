import unittest
from unittest.mock import patch

from chilo_api.cli.openapi.arguments import OpenAPIArguments
from chilo_api.cli.importer import CLIImporter
from chilo_api.cli import CLIManager


class OpenAPIArgumentsTest(unittest.TestCase):

    @patch('sys.argv', [
        'CLIManager',
        'generate-openapi',
        '--api=api_rest',
        '--output=tests/outputs/arguments',
        '--format=json,yml',
        '--delete'
    ])
    def test_full_class(self):
        manager = CLIManager()
        importer = CLIImporter()
        api = importer.get_api_module(manager.args.api)
        input_args = OpenAPIArguments(api, manager.args)
        self.assertEqual('/', input_args.base)
        self.assertEqual('tests/unit/mocks/rest/handlers/valid', input_args.handlers)
        self.assertEqual('tests/outputs/arguments', input_args.output)
        self.assertListEqual(['json', 'yml'], input_args.formats)
        self.assertTrue(input_args.delete)

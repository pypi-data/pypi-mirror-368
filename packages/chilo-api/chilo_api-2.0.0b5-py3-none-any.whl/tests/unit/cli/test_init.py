import unittest
from unittest.mock import patch

from chilo_api.cli import CLIManager


class MockServer:
    def __init__(self, args):
        self.args = args

    def run(self):
        # This mock function is intentionally left empty to replace actual implementations during testing.
        pass


class MockGenerateOpenApi:
    def __init__(self, args):
        self.args = args

    def generate(self):
        # This mock function is intentionally left empty to replace actual implementations during testing.
        pass


class CLIManagerTest(unittest.TestCase):

    @patch('chilo_api.cli.OpenAPI', MockGenerateOpenApi)
    @patch('sys.argv', [
        'CLIManager',
        'generate-openapi',
        '--api=api',
        '--output=tests',
        '--format=json,yml',
        '--delete'
    ])
    def test_args(self):
        manager = CLIManager()
        manager.run()
        self.assertEqual('api', manager.args.api)
        self.assertEqual('tests', manager.args.output)
        self.assertListEqual(['json', 'yml'], manager.args.format.split(','))
        self.assertTrue(manager.args.delete)

    @patch('chilo_api.cli.Server', MockServer)
    @patch('sys.argv', [
        'CLIManager',
        'serve',
        '--api=api'
    ])
    def test_run(self):
        manager = CLIManager()
        manager.run()
        self.assertEqual('api', manager.args.api)

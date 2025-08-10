import unittest

from chilo_api import Chilo
from chilo_api.cli.importer import CLIImporter


class ImporterTest(unittest.TestCase):

    def test_get_handler_modules_from_file_paths(self):
        importer = CLIImporter()
        file_paths = ['tests/unit/mocks/rest/handlers/valid/basic.py']
        handlers_base = 'tests/unit/mocks/rest/handlers/valid'
        base_path = 'chilo/example'
        modules = importer.get_handler_modules_from_file_paths(file_paths, handlers_base, base_path)
        assert len(modules) == 5

    def test_get_api_module(self):
        importer = CLIImporter()
        result = importer.get_api_module('api_rest.py')
        self.assertIsInstance(result, Chilo)

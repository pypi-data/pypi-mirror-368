import os
import unittest

from chilo_api.cli.scanner import CLIScanner


class CLIScannerTest(unittest.TestCase):
    handler_path = 'tests/unit/mocks/rest/handlers/valid/**/*.py'

    def setUp(self):
        self.scanner = CLIScanner(self.handler_path)

    def test_scanner_initialization_fails(self):
        with self.assertRaises(RuntimeError):
            CLIScanner(None)

    def test_file_separator(self):
        self.assertEqual(self.scanner.file_separator, os.sep)

    def test_handlers(self):
        self.assertEqual(self.scanner.handlers, self.handler_path)

    def test_handlers_base(self):
        self.assertEqual(self.scanner.handlers_base, 'tests/unit/mocks/rest/handlers/valid')

    def test_clean_path(self):
        dirty_path = '/dirty/path/'
        result = self.scanner.clean_path(dirty_path)
        self.assertEqual(result, 'dirty/path')

    def test_get_handler_file_paths(self):
        paths = self.scanner.get_handler_file_paths()
        self.assertGreater(len(paths), 10)

    def test_get_handler_file_no_directory(self):
        scanner = CLIScanner('tests/unit/mocks/rest/handlers/valid')
        paths = scanner.get_handler_file_paths()
        self.assertGreater(len(paths), 10)

    def test_get_handler_glob_pattern(self):
        handler_path = 'tests/unit/mocks/rest/handlers/valid'
        handlers_base = 'tests/unit/mocks/rest/handlers/valid/**/*.py'
        scanner = CLIScanner(handler_path)
        pattern = scanner.get_handler_glob_pattern(handlers_base)
        self.assertEqual(pattern, handlers_base)

    def test_get_generated_glob_pattern(self):
        protobuf_base = 'tests/unit/mocks/protobuf'
        expected_pattern = 'tests/unit/mocks/protobuf/**/*_pb2*.py'
        pattern = self.scanner.get_generated_glob_pattern(protobuf_base)
        self.assertEqual(pattern, expected_pattern)

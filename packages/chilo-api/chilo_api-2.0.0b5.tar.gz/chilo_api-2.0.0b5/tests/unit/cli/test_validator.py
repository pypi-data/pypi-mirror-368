import unittest

from chilo_api.cli.validator import CLIValidator


class MockInputArguments:

    def __init__(self):
        self.base = 'chilo/example'
        self.handlers = 'tests/unit/mocks/openapi/**/*.py'
        self.output = 'tests/unit/mocks'
        self.format = 'json,yml'


class MockServer:
    port = 9999999999


class CLIValidatorTest(unittest.TestCase):

    def setUp(self):
        self.validator = CLIValidator()

    def test_validate_arguments_all_pass(self):
        inputs = MockInputArguments()
        self.validator.validate_arguments(inputs)

    def test_validate_arguments_directory_fails(self):
        inputs = MockInputArguments()
        inputs.output = 'tests/fail'
        with self.assertRaises(Exception) as context:
            self.validator.validate_arguments(inputs)
        self.assertIn('is not a valid directory path', str(context.exception))

    def test_validate_server_port_fails(self):
        server = MockServer()
        with self.assertRaises(RuntimeError) as context:
            self.validator.validate_server(server)
        self.assertIn('is not between well known ports', str(context.exception))

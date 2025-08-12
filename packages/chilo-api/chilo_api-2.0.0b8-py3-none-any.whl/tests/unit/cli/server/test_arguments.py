import unittest
from chilo_api.cli.server.arguments import ServerArguments


class MockArgs:
    api = 'api_rest.py'
    host = '127.0.0.1'
    port = 3000
    reload = False
    verbose = False


class MockApi:
    api_type = 'rest'
    api = 'api_rest.py'
    host = '127.0.0.1'
    port = 3000
    reload = False
    verbose = False
    timeout = None
    handlers = 'tests/mocks/handlers'
    protobufs = 'tests/unit/mocks/grpc/protobufs'
    openapi_validate_request = False
    openapi_validate_response = False
    reflection = True
    private_key = None
    certificate = None
    max_workers = 10


class ArgumentsTest(unittest.TestCase):

    def test_route(self):
        mock_args = MockArgs()
        mock_api = MockApi()
        server_args = ServerArguments(mock_args, mock_api)  # type: ignore
        self.assertEqual(server_args.handlers, mock_api.handlers)
        self.assertEqual(server_args.protobufs, mock_api.protobufs)
        self.assertEqual(server_args.api_type, mock_api.api_type)
        self.assertIsInstance(server_args.api_config, MockApi)
        self.assertEqual(server_args.host, mock_api.host)
        self.assertEqual(server_args.port, mock_api.port)
        self.assertEqual(server_args.reload, mock_api.reload)
        self.assertEqual(server_args.verbose, mock_api.verbose)
        self.assertEqual(server_args.timeout, mock_api.timeout)
        self.assertEqual(server_args.openapi_validate_request, mock_api.openapi_validate_request)
        self.assertEqual(server_args.openapi_validate_response, mock_api.openapi_validate_response)
        self.assertEqual(server_args.reflection, mock_api.reflection)
        self.assertEqual(server_args.private_key, mock_api.private_key)
        self.assertEqual(server_args.certificate, mock_api.certificate)
        self.assertEqual(server_args.max_workers, mock_api.max_workers)

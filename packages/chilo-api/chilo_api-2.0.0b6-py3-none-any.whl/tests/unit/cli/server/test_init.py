from unittest import mock, TestCase

from chilo_api.cli.server import Server


class MockArgs:
    api = 'api_rest.py'
    host = '127.0.0.1'
    port = 3000
    reload = False
    verbose = False


class MockGRPCServer:
    def __init__(self, *args, **kwargs):
        # This constructor is intentionally left empty because it serves as a mock replacement
        pass

    def run(self):
        # This method is intentionally left empty because it serves as a mock replacement
        pass


def mock_run_simple(*args, **kwargs):
    # This function is intentionally left empty because it serves as a mock replacement
    # for 'run_simple' during testing, preventing actual server execution.
    pass


class RunServerTest(TestCase):

    @mock.patch('chilo_api.cli.server.run_simple', mock_run_simple)
    def test_run_server(self):
        args = MockArgs()
        server = Server(args)
        server.run()  # should throw an error if everything is not set up correctly
        self.assertIsInstance(server, Server)

    @mock.patch('chilo_api.cli.server.GRPCServer', MockGRPCServer)
    @mock.patch('chilo_api.cli.server.run_simple', mock_run_simple)
    def test_run_grpc_server(self):
        args = MockArgs()
        args.api = 'api_grpc.py'
        server = Server(args)
        server.run()  # should throw an error if everything is not set up correctly
        self.assertIsInstance(server, Server)

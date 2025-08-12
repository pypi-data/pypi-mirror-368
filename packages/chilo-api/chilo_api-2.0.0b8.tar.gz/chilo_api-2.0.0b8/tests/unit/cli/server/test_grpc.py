from unittest import mock, TestCase
from unittest.mock import Mock, patch, mock_open

from chilo_api.cli.server.grpc import GRPCServer
from chilo_api.core.types.server_settings import ServerSettings
from chilo_api.cli.logger import CLILogger
from chilo_api.core.router import Router


class MockArgs:
    api = 'api_grpc.py'
    host = '127.0.0.1'
    port = 3000
    handlers = 'tests/unit/mocks/grpc/handlers/valid'
    protobufs = 'tests/unit/mocks/grpc/protobufs'
    api_config = Mock(spec=Router)
    reflection = True
    private_key = None
    certificate = None
    max_workers = 10


class GRPCServerTest(TestCase):

    def setUp(self):
        self.mock_server_args = Mock(spec=ServerSettings)
        self.mock_server_args.handlers = 'test/handlers'
        self.mock_server_args.port = 50051
        self.mock_server_args.protobufs = 'test/protobufs'
        self.mock_server_args.api_config = Mock(spec=Router)
        self.mock_server_args.reflection = True
        self.mock_server_args.private_key = None
        self.mock_server_args.certificate = None
        self.mock_server_args.max_workers = 10
        self.mock_logger = Mock(spec=CLILogger)
        self.grpc_server = GRPCServer(self.mock_server_args, self.mock_logger)

    @mock.patch('chilo_api.cli.server.grpc.grpc.server')
    def test_run_server_success(self, mock_grpc_server):
        server_args = MockArgs()
        logger = mock.Mock()
        grpc_server = GRPCServer(server_args, logger)  # type: ignore
        grpc_server.run()
        mock_grpc_server.assert_called_once()
        self.assertTrue(grpc_server.__dict__['_GRPCServer__dynamic_servers'])

    def test_run_server_failure_no_handlers(self):
        server_args = MockArgs()
        server_args.handlers = 'tests/mocks/grpc/bad/handlers'
        logger = mock.Mock()
        grpc_server = GRPCServer(server_args, logger)  # type: ignore
        with self.assertRaises(RuntimeError) as context:
            grpc_server.run()
        self.assertIn('No gRPC handlers found in the specified directory', str(context.exception))

    def test_run_server_failure_no_modules(self):
        server_args = MockArgs()
        server_args.handlers = 'tests/unit/mocks/rest/handlers/valid'
        logger = mock.Mock()
        grpc_server = GRPCServer(server_args, logger)  # type: ignore
        with self.assertRaises(RuntimeError) as context:
            grpc_server.run()
        self.assertIn('No gRPC endpoint methods found in the provided modules.', str(context.exception))

    def test_run_server_failure_bad_proto_file(self):
        server_args = MockArgs()
        server_args.handlers = 'tests/unit/mocks/grpc/handlers/invalid/bad_proto'
        logger = mock.Mock()
        grpc_server = GRPCServer(server_args, logger)  # type: ignore
        with self.assertRaises(RuntimeError) as context:
            grpc_server.run()
        self.assertIn('Error generating gRPC code for', str(context.exception))

    def test_run_server_failure_bad_service_definition(self):
        server_args = MockArgs()
        server_args.handlers = 'tests/unit/mocks/grpc/handlers/invalid/bad_service'
        logger = mock.Mock()
        grpc_server = GRPCServer(server_args, logger)  # type: ignore
        with self.assertRaises(RuntimeError) as context:
            grpc_server.run()
        self.assertIn('No matching servicer class found for', str(context.exception))

    def test_run_server_failure_duplicate_method_definition(self):
        server_args = MockArgs()
        server_args.handlers = 'tests/unit/mocks/grpc/handlers/invalid/duplicate_method'
        logger = mock.Mock()
        grpc_server = GRPCServer(server_args, logger)  # type: ignore
        with self.assertRaises(RuntimeError) as context:
            grpc_server.run()
        self.assertIn('already exists', str(context.exception))

    @patch('grpc.server')
    def test_keyboard_interrupt_exception(self, mock_grpc_server):
        mock_server = Mock()
        mock_grpc_server.return_value = mock_server
        mock_server.add_insecure_port = Mock()
        mock_server.start = Mock()
        mock_server.wait_for_termination = Mock(side_effect=KeyboardInterrupt())
        mock_server.stop = Mock()
        with patch.object(self.grpc_server, '_GRPCServer__get_endpoints_from_server', return_value=[]):
            with patch.object(self.grpc_server, '_GRPCServer__generate_grpc_code_from_endpoints'):
                with patch.object(self.grpc_server, '_GRPCServer__pair_generated_code_to_endpoints'):
                    with patch.object(self.grpc_server, '_GRPCServer__assign_grpc_classes_to_endpoints'):
                        with patch.object(self.grpc_server, '_GRPCServer__assign_grpc_server_methods'):
                            with patch.object(self.grpc_server, '_GRPCServer__add_to_server'):
                                self.grpc_server.run()

        mock_server.add_insecure_port.assert_called_once_with(f'[::]:{self.mock_server_args.port}')
        mock_server.start.assert_called_once()
        mock_server.wait_for_termination.assert_called_once()

        mock_server.stop.assert_called_once_with(grace=3)
        self.mock_logger.log_message.assert_called_once_with('Server stopped by user.')

    @patch('grpc.server')
    def test_general_exception_handling(self, mock_grpc_server):
        mock_server = Mock()
        mock_grpc_server.return_value = mock_server
        test_exception = Exception("Test connection error")
        mock_server.add_insecure_port = Mock()
        mock_server.start = Mock(side_effect=test_exception)
        mock_server.stop = Mock()
        with patch.object(self.grpc_server, '_GRPCServer__get_endpoints_from_server', return_value=[]):
            with patch.object(self.grpc_server, '_GRPCServer__generate_grpc_code_from_endpoints'):
                with patch.object(self.grpc_server, '_GRPCServer__pair_generated_code_to_endpoints'):
                    with patch.object(self.grpc_server, '_GRPCServer__assign_grpc_classes_to_endpoints'):
                        with patch.object(self.grpc_server, '_GRPCServer__assign_grpc_server_methods'):
                            with patch.object(self.grpc_server, '_GRPCServer__add_to_server'):
                                self.grpc_server.run()

        mock_server.add_insecure_port.assert_called_once_with(f'[::]:{self.mock_server_args.port}')
        mock_server.start.assert_called_once()

        mock_server.stop.assert_called_once_with(grace=0)
        self.mock_logger.log_message.assert_called_once_with(f'An error occurred while running the gRPC server: {test_exception}')

    @patch('grpc.server')
    def test_add_insecure_port_exception(self, mock_grpc_server):
        mock_server = Mock()
        mock_grpc_server.return_value = mock_server

        port_exception = Exception("Port already in use")
        mock_server.add_insecure_port = Mock(side_effect=port_exception)
        mock_server.stop = Mock()

        with patch.object(self.grpc_server, '_GRPCServer__get_endpoints_from_server', return_value=[]):
            with patch.object(self.grpc_server, '_GRPCServer__generate_grpc_code_from_endpoints'):
                with patch.object(self.grpc_server, '_GRPCServer__pair_generated_code_to_endpoints'):
                    with patch.object(self.grpc_server, '_GRPCServer__assign_grpc_classes_to_endpoints'):
                        with patch.object(self.grpc_server, '_GRPCServer__assign_grpc_server_methods'):
                            with patch.object(self.grpc_server, '_GRPCServer__add_to_server'):
                                with self.assertRaises(Exception) as context:
                                    self.grpc_server.run()
                                self.assertEqual(str(context.exception), str(port_exception))

    @patch('grpc.server')
    def test_wait_for_termination_exception(self, mock_grpc_server):
        mock_server = Mock()
        mock_grpc_server.return_value = mock_server

        termination_exception = Exception("Server terminated unexpectedly")
        mock_server.add_insecure_port = Mock()
        mock_server.start = Mock()
        mock_server.wait_for_termination = Mock(side_effect=termination_exception)
        mock_server.stop = Mock()

        with patch.object(self.grpc_server, '_GRPCServer__get_endpoints_from_server', return_value=[]):
            with patch.object(self.grpc_server, '_GRPCServer__generate_grpc_code_from_endpoints'):
                with patch.object(self.grpc_server, '_GRPCServer__pair_generated_code_to_endpoints'):
                    with patch.object(self.grpc_server, '_GRPCServer__assign_grpc_classes_to_endpoints'):
                        with patch.object(self.grpc_server, '_GRPCServer__assign_grpc_server_methods'):
                            with patch.object(self.grpc_server, '_GRPCServer__add_to_server'):
                                self.grpc_server.run()

        mock_server.add_insecure_port.assert_called_once_with(f'[::]:{self.mock_server_args.port}')
        mock_server.start.assert_called_once()
        mock_server.wait_for_termination.assert_called_once()
        mock_server.stop.assert_called_once_with(grace=0)
        self.mock_logger.log_message.assert_called_once_with(f'An error occurred while running the gRPC server: {termination_exception}')

    @patch('grpc.server')
    def test_successful_server_run_no_exceptions(self, mock_grpc_server):
        mock_server = Mock()
        mock_grpc_server.return_value = mock_server
        mock_server.add_insecure_port = Mock()
        mock_server.start = Mock()
        mock_server.wait_for_termination = Mock()
        mock_server.stop = Mock()

        with patch.object(self.grpc_server, '_GRPCServer__get_endpoints_from_server', return_value=[]):
            with patch.object(self.grpc_server, '_GRPCServer__generate_grpc_code_from_endpoints'):
                with patch.object(self.grpc_server, '_GRPCServer__pair_generated_code_to_endpoints'):
                    with patch.object(self.grpc_server, '_GRPCServer__assign_grpc_classes_to_endpoints'):
                        with patch.object(self.grpc_server, '_GRPCServer__assign_grpc_server_methods'):
                            with patch.object(self.grpc_server, '_GRPCServer__add_to_server'):
                                self.grpc_server.run()

        mock_server.add_insecure_port.assert_called_once_with(f'[::]:{self.mock_server_args.port}')
        mock_server.start.assert_called_once()
        mock_server.wait_for_termination.assert_called_once()
        mock_server.stop.assert_not_called()
        self.mock_logger.log_message.assert_not_called()

    def test_exception_message_formatting(self):
        test_cases = [
            (ConnectionError("Connection refused"), "Connection refused"),
            (OSError("Address already in use"), "Address already in use"),
            (ValueError("Invalid port number"), "Invalid port number"),
            (RuntimeError("Server initialization failed"), "Server initialization failed")
        ]

        for exception, expected_message in test_cases:
            with patch('grpc.server') as mock_grpc_server:
                mock_server = Mock()
                mock_grpc_server.return_value = mock_server
                mock_server.add_insecure_port = Mock()
                mock_server.start = Mock(side_effect=exception)
                mock_server.stop = Mock()
                self.mock_logger.reset_mock()

                with patch.object(self.grpc_server, '_GRPCServer__get_endpoints_from_server', return_value=[]):
                    with patch.object(self.grpc_server, '_GRPCServer__generate_grpc_code_from_endpoints'):
                        with patch.object(self.grpc_server, '_GRPCServer__pair_generated_code_to_endpoints'):
                            with patch.object(self.grpc_server, '_GRPCServer__assign_grpc_classes_to_endpoints'):
                                with patch.object(self.grpc_server, '_GRPCServer__assign_grpc_server_methods'):
                                    with patch.object(self.grpc_server, '_GRPCServer__add_to_server'):
                                        self.grpc_server.run()

                expected_log_message = f'An error occurred while running the gRPC server: {expected_message}'
                self.mock_logger.log_message.assert_called_once_with(expected_log_message)

    @patch('builtins.open', new_callable=mock_open)
    @patch('chilo_api.cli.server.grpc.grpc.ssl_server_credentials')
    @patch('grpc.server')
    def test_add_secure_port_with_tls_credentials(self, mock_grpc_server, mock_ssl_credentials, mock_file_open):
        mock_server = Mock()
        mock_grpc_server.return_value = mock_server
        mock_credentials = Mock()
        mock_ssl_credentials.return_value = mock_credentials

        # Set up TLS credentials
        self.mock_server_args.private_key = '/path/to/key.pem'
        self.mock_server_args.certificate = '/path/to/cert.pem'

        mock_file_open.side_effect = [
            mock_open(read_data=b'private_key_data').return_value,
            mock_open(read_data=b'certificate_data').return_value
        ]

        with patch.object(self.grpc_server, '_GRPCServer__get_endpoints_from_server', return_value=[]):
            with patch.object(self.grpc_server, '_GRPCServer__generate_grpc_code_from_endpoints'):
                with patch.object(self.grpc_server, '_GRPCServer__pair_generated_code_to_endpoints'):
                    with patch.object(self.grpc_server, '_GRPCServer__assign_grpc_classes_to_endpoints'):
                        with patch.object(self.grpc_server, '_GRPCServer__assign_grpc_server_methods'):
                            with patch.object(self.grpc_server, '_GRPCServer__add_to_server'):
                                self.grpc_server.run()

        # Verify TLS setup
        mock_ssl_credentials.assert_called_once_with([(b'private_key_data', b'certificate_data')])
        mock_server.add_secure_port.assert_called_once_with(f'[::]:{self.mock_server_args.port}', mock_credentials)
        mock_server.add_insecure_port.assert_not_called()

    @patch('builtins.open', side_effect=FileNotFoundError("Private key file not found"))
    @patch('grpc.server')
    def test_add_secure_port_with_missing_private_key_file(self, mock_grpc_server, mock_file_open):
        mock_server = Mock()
        mock_grpc_server.return_value = mock_server

        # Set up TLS credentials with missing file
        self.mock_server_args.private_key = '/path/to/missing_key.pem'
        self.mock_server_args.certificate = '/path/to/cert.pem'

        with patch.object(self.grpc_server, '_GRPCServer__get_endpoints_from_server', return_value=[]):
            with patch.object(self.grpc_server, '_GRPCServer__generate_grpc_code_from_endpoints'):
                with patch.object(self.grpc_server, '_GRPCServer__pair_generated_code_to_endpoints'):
                    with patch.object(self.grpc_server, '_GRPCServer__assign_grpc_classes_to_endpoints'):
                        with patch.object(self.grpc_server, '_GRPCServer__assign_grpc_server_methods'):
                            with patch.object(self.grpc_server, '_GRPCServer__add_to_server'):
                                with self.assertRaises(FileNotFoundError) as context:
                                    self.grpc_server.run()
                                self.assertEqual(str(context.exception), "Private key file not found")

    @patch('chilo_api.cli.server.grpc.grpc.ssl_server_credentials')
    @patch('grpc.server')
    def test_add_secure_port_with_missing_certificate_file(self, mock_grpc_server, mock_ssl_credentials):
        mock_server = Mock()
        mock_grpc_server.return_value = mock_server

        # Set up TLS credentials
        self.mock_server_args.private_key = '/path/to/key.pem'
        self.mock_server_args.certificate = '/path/to/cert.pem'

        # Use context managers to patch both file operations
        with patch('builtins.open', mock_open(read_data=b'private_key_data')) as mock_file:
            # Configure the mock to succeed on first call, fail on second
            mock_file.side_effect = [
                mock_open(read_data=b'private_key_data').return_value,
                FileNotFoundError("Certificate file not found")
            ]

            with patch.object(self.grpc_server, '_GRPCServer__get_endpoints_from_server', return_value=[]):
                with patch.object(self.grpc_server, '_GRPCServer__generate_grpc_code_from_endpoints'):
                    with patch.object(self.grpc_server, '_GRPCServer__pair_generated_code_to_endpoints'):
                        with patch.object(self.grpc_server, '_GRPCServer__assign_grpc_classes_to_endpoints'):
                            with patch.object(self.grpc_server, '_GRPCServer__assign_grpc_server_methods'):
                                with patch.object(self.grpc_server, '_GRPCServer__add_to_server'):
                                    with self.assertRaises(FileNotFoundError) as context:
                                        self.grpc_server.run()
                                    self.assertEqual(str(context.exception), "Certificate file not found")

    @patch('chilo_api.cli.server.grpc.reflection.enable_server_reflection')
    @patch('grpc.server')
    def test_server_reflection_enabled_when_configured(self, mock_grpc_server, mock_enable_reflection):
        mock_server = Mock()
        mock_grpc_server.return_value = mock_server

        # Ensure reflection is enabled
        self.mock_server_args.reflection = True

        with patch.object(self.grpc_server, '_GRPCServer__get_endpoints_from_server', return_value=[]):
            with patch.object(self.grpc_server, '_GRPCServer__generate_grpc_code_from_endpoints'):
                with patch.object(self.grpc_server, '_GRPCServer__pair_generated_code_to_endpoints'):
                    with patch.object(self.grpc_server, '_GRPCServer__assign_grpc_classes_to_endpoints'):
                        with patch.object(self.grpc_server, '_GRPCServer__assign_grpc_server_methods'):
                            with patch.object(self.grpc_server, '_GRPCServer__add_to_server'):
                                with patch.object(self.grpc_server, '_GRPCServer__get_service_names_for_reflection', return_value=('test.Service', 'grpc.reflection.v1alpha.ServerReflection')):
                                    self.grpc_server.run()

        mock_enable_reflection.assert_called_once_with(('test.Service', 'grpc.reflection.v1alpha.ServerReflection'), mock_server)

    @patch('chilo_api.cli.server.grpc.reflection.enable_server_reflection')
    @patch('grpc.server')
    def test_server_reflection_disabled_when_configured(self, mock_grpc_server, mock_enable_reflection):
        mock_server = Mock()
        mock_grpc_server.return_value = mock_server

        # Disable reflection
        self.mock_server_args.reflection = False

        with patch.object(self.grpc_server, '_GRPCServer__get_endpoints_from_server', return_value=[]):
            with patch.object(self.grpc_server, '_GRPCServer__generate_grpc_code_from_endpoints'):
                with patch.object(self.grpc_server, '_GRPCServer__pair_generated_code_to_endpoints'):
                    with patch.object(self.grpc_server, '_GRPCServer__assign_grpc_classes_to_endpoints'):
                        with patch.object(self.grpc_server, '_GRPCServer__assign_grpc_server_methods'):
                            with patch.object(self.grpc_server, '_GRPCServer__add_to_server'):
                                self.grpc_server.run()

        mock_enable_reflection.assert_not_called()

    def test_tls_configuration_validation(self):
        self.mock_server_args.private_key = '/path/to/key.pem'
        self.mock_server_args.certificate = None

        with patch('grpc.server') as mock_grpc_server:
            mock_server = Mock()
            mock_grpc_server.return_value = mock_server

            with patch.object(self.grpc_server, '_GRPCServer__get_endpoints_from_server', return_value=[]):
                with patch.object(self.grpc_server, '_GRPCServer__generate_grpc_code_from_endpoints'):
                    with patch.object(self.grpc_server, '_GRPCServer__pair_generated_code_to_endpoints'):
                        with patch.object(self.grpc_server, '_GRPCServer__assign_grpc_classes_to_endpoints'):
                            with patch.object(self.grpc_server, '_GRPCServer__assign_grpc_server_methods'):
                                with patch.object(self.grpc_server, '_GRPCServer__add_to_server'):
                                    self.grpc_server.run()

            # Should fall back to insecure port
            mock_server.add_insecure_port.assert_called_once_with(f'[::]:{self.mock_server_args.port}')
            mock_server.add_secure_port.assert_not_called()

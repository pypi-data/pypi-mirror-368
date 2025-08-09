import unittest

from chilo_api.core.validator.config import ConfigValidator


class ConfigValidatorTest(unittest.TestCase):

    def test_config_validator_validates_all_passing(self):
        # Should not raise any exception
        ConfigValidator.validate(
            base_path='some/path',
            handlers='some/path',
            openapi='some/path',
            openapi_validate_request=False,
            openapi_validate_response=False,
            cache_size=128,
            cache_mode='all',
            verbose=True
        )

    def test_config_validator_validates_base_path(self):
        with self.assertRaises(RuntimeError) as context:
            ConfigValidator.validate(base_path=1)
        self.assertEqual('base_path must be a str', str(context.exception))

    def test_config_validator_validates_routing_handlers_is_required(self):
        with self.assertRaises(RuntimeError) as context:
            ConfigValidator.validate(base_path='some/path')
        self.assertEqual('handlers is required; must be glob pattern string {route: file_path}', str(context.exception))

    def test_config_validator_validates_routing_handlers_are_appropriate(self):
        with self.assertRaises(RuntimeError) as context:
            ConfigValidator.validate(base_path='some/path', handlers=1)
        self.assertEqual('handlers is required; must be glob pattern string {route: file_path}', str(context.exception))

    def test_config_validator_validates_routing_openapi_validate_request_is_appropriate(self):
        with self.assertRaises(RuntimeError) as context:
            ConfigValidator.validate(base_path='some/path', handlers='some/path', openapi_validate_request=1)
        self.assertEqual('openapi_validate_request must be a bool', str(context.exception))

    def test_config_validator_validates_routing_openapi_validate_response_is_appropriate(self):
        with self.assertRaises(RuntimeError) as context:
            ConfigValidator.validate(base_path='some/path', handlers='some/path', openapi_validate_response=1)
        self.assertEqual('openapi_validate_response must be a bool', str(context.exception))

    def test_config_validator_validates_routing_verbose_logging_is_appropriate(self):
        with self.assertRaises(RuntimeError) as context:
            ConfigValidator.validate(base_path='some/path', handlers='some/path', verbose=1)
        self.assertEqual('verbose must be a bool', str(context.exception))

    def test_config_validator_validates_routing_schema_is_appropriate(self):
        with self.assertRaises(RuntimeError) as context:
            ConfigValidator.validate(base_path='some/path', handlers='some/path', openapi=1)
        self.assertEqual('schema should either be file path string', str(context.exception))

    def test_config_validator_validates_routing_cache_size_is_appropriate(self):
        with self.assertRaises(RuntimeError) as context:
            ConfigValidator.validate(base_path='some/path', handlers='some/path', cache_size='1')
        self.assertEqual('cache_size should be an int (0 for unlimited size) or None (to disable route caching)', str(context.exception))

    def test_config_validator_validates_routing_cache_mode_is_appropriate(self):
        with self.assertRaises(RuntimeError) as context:
            ConfigValidator.validate(base_path='some/path', handlers='some/path', cache_mode='bad')
        self.assertEqual('cache_mode should be one of: all, static-only, dynamic-only', str(context.exception))

    def test_config_schema_is_required_for_openapi_validate_request(self):
        with self.assertRaises(RuntimeError) as context:
            ConfigValidator.validate(base_path='some/path', handlers='some/path', openapi_validate_request=True)
        self.assertEqual('schema is required to use openapi_validate_request', str(context.exception))

import unittest
import warnings

from chilo_api.core.validator.openapi import OpenApiValidator

warnings.filterwarnings('ignore')


class OpenApiValidatorTest(unittest.TestCase):
    valid_schema = 'tests/unit/mocks/openapi/variations/openapi.yml'
    invalid_schema = 'tests/unit/mocks/openapi/variations/openapi-for-validator-test-fail.yml'
    missing_required_body = 'tests/unit/mocks/openapi/variations/openapi-missing-required-body.yml'
    missing_required_response = 'tests/unit/mocks/openapi/variations/openapi-missing-required-response.yml'
    openapi_validate_request_schema_pass = 'tests/unit/mocks/openapi/variations/openapi-auto-validate-pass.yml'
    openapi_validate_request_schema_route_fail_route = 'tests/unit/mocks/openapi/variations/openapi-auto-validate-route-fail-route.yml'
    openapi_validate_request_schema_route_fail_method = 'tests/unit/mocks/openapi/variations/openapi-auto-validate-route-fail-route-method.yml'

    def test_valid_openapi(self):
        validator = OpenApiValidator(
            openapi=self.valid_schema,
            handlers='tests/unit/mocks/rest/handlers/valid'
        )
        # Should not raise any exception
        validator.validate_openapi()

    def test_invalid_openapi_spec_errors(self):
        validator = OpenApiValidator(
            openapi=self.invalid_schema,
            handlers='tests/unit/mocks/rest/handlers/valid'
        )

        with self.assertRaises(RuntimeError) as context:
            validator.validate_openapi()

        self.assertIn('there was a problem with your openapi schema; see above', str(context.exception))

    def test_invalid_openapi_spec_ignored(self):
        validator = OpenApiValidator(
            openapi=self.invalid_schema,
            openapi_validate_spec=False,
            handlers='tests/unit/mocks/rest/handlers/valid'
        )
        # Should not raise any exception when validation is disabled
        validator.validate_openapi()

    def test_handler_spec_passes_openapi(self):
        validator = OpenApiValidator(
            openapi=self.openapi_validate_request_schema_pass,
            handlers='tests/unit/mocks/rest/handlers/valid',
            openapi_validate_request=True
        )
        # Should not raise any exception
        validator.validate_openapi()

    def test_handler_spec_route_not_in_openapi(self):
        validator = OpenApiValidator(
            openapi=self.openapi_validate_request_schema_route_fail_route,
            handlers='tests/unit/mocks/rest/handlers/valid',
            openapi_validate_request=True
        )
        with self.assertRaises(RuntimeError) as context:
            validator.validate_openapi()
        error_message = str(context.exception)
        self.assertIn('openapi_validate_request is enabled and route', error_message)

    def test_handler_spec_route_method_not_in_openapi(self):
        validator = OpenApiValidator(
            openapi=self.openapi_validate_request_schema_route_fail_method,
            handlers='tests/unit/mocks/rest/handlers/valid',
            openapi_validate_request=True
        )

        with self.assertRaises(RuntimeError) as context:
            validator.validate_openapi()
        error_message = str(context.exception)
        self.assertIn('openapi_validate_request is enabled and method', error_message)

    def test_handler_spec_fails_missing_schema_defined_in_required_body(self):
        validator = OpenApiValidator(
            openapi=self.missing_required_body,
            handlers='tests/unit/mocks/rest/handlers/valid'
        )
        with self.assertRaises(RuntimeError) as context:
            validator.validate_openapi()
        self.assertIn('required_body schema', str(context.exception))

    def test_handler_spec_fails_missing_schema_defined_in_required_response(self):
        validator = OpenApiValidator(
            openapi=self.missing_required_response,
            handlers='tests/unit/mocks/rest/handlers/valid'
        )
        with self.assertRaises(RuntimeError) as context:
            validator.validate_openapi()
        self.assertIn('required_response schema', str(context.exception))

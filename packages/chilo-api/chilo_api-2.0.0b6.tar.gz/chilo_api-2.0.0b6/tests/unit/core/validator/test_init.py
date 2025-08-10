import json
import unittest
from wsgiref import handlers

from tests.unit.mocks.rest.common.environment_builder import EnvironmentBuilder
from tests.unit.mocks.rest.common.pydantic_class import UserRequest

from chilo_api.core.validator import Validator


class ValidatorTest(unittest.TestCase):
    schema_path = 'tests/unit/mocks/openapi/variations/openapi-for-validator-test-pass.yml'
    schema_path_bad = 'tests/unit/mocks/openapi/variations/openapi-for-validator-test-fail.yml'
    environ = EnvironmentBuilder()
    passing_body = {
        'id': 3,
        'email': 'some@email.com',
        'active': True,
        'favorites': ['anime', 'video games', 'basketball'],
        'notification_config': {
            'marketing': False,
            'transactions': True
        }
    }
    failing_body = {
        'id': 'three',
        'email': 'some@email.com',
        'active': True,
        'favorites': ['anime', 'video games', 'basketball'],
        'notification_config': {
            'marketing': False,
            'transactions': True
        }
    }

    def setUp(self):
        self.validator = Validator(openapi=self.schema_path, handlers='tests/unit/mocks/rest/handlers/valid')

    def test_empty_validation(self):
        request = self.environ.get_request()
        response = self.environ.get_response()
        requirements = {}
        self.validator.validate_request(request, response, requirements)
        self.assertFalse(response.has_errors)

    def test_required_headers_pass(self):
        request = self.environ.get_request(headers={'content-type': 'unit/test'})
        response = self.environ.get_response()
        requirements = {
            'required_headers': ['content-type']
        }
        self.validator.validate_request(request, response, requirements)
        self.assertFalse(response.has_errors)

    def test_required_headers_fails(self):
        request = self.environ.get_request()
        response = self.environ.get_response()
        requirements = {
            'required_headers': ['content-type']
        }
        self.validator.validate_request(request, response, requirements)
        self.assertTrue(response.has_errors)
        body = json.loads(next(response.get_response()).decode('utf-8'))
        self.assertDictEqual({"errors": [{"key_path": "headers", "message": "Please provide content-type in headers"}]}, body)

    def test_available_headers_pass(self):
        request = self.environ.get_request()
        response = self.environ.get_response()
        requirements = {
            'available_headers': ['content-type', 'host']
        }
        self.validator.validate_request(request, response, requirements)
        self.assertFalse(response.has_errors)

    def test_available_headers_fail(self):
        request = self.environ.get_request(headers={'content-type-fail': 'unit/test'})
        response = self.environ.get_response()
        requirements = {
            'available_headers': ['content-type', 'host']
        }
        self.validator.validate_request(request, response, requirements)
        self.assertTrue(response.has_errors)
        body = json.loads(next(response.get_response()).decode('utf-8'))
        self.assertDictEqual({"errors": [{"key_path": "headers", "message": "content-type-fail is not an available headers"}]}, body)

    def test_combined_headers_pass(self):
        request = self.environ.get_request(headers={'content-type': 'unit/test'})
        response = self.environ.get_response()
        requirements = {
            'required_headers': ['content-type'],
            'available_headers': ['host']
        }
        self.validator.validate_request(request, response, requirements)
        self.assertFalse(response.has_errors)

    def test_required_query_pass(self):
        request = self.environ.get_request(query_string={'email': 'unit@test.com'})
        response = self.environ.get_response()
        requirements = {
            'required_query': ['email']
        }
        self.validator.validate_request(request, response, requirements)
        self.assertFalse(response.has_errors)

    def test_required_query_fail(self):
        request = self.environ.get_request()
        response = self.environ.get_response()
        requirements = {
            'required_query': ['email']
        }
        self.validator.validate_request(request, response, requirements)
        body = json.loads(next(response.get_response()).decode('utf-8'))
        self.assertTrue(response.has_errors)
        self.assertDictEqual({"errors": [{"key_path": "query_params", "message": "Please provide email in query_params"}]}, body)

    def test_available_query_pass(self):
        request = self.environ.get_request()
        response = self.environ.get_response()
        requirements = {
            'available_query': ['email']
        }
        self.validator.validate_request(request, response, requirements)
        self.assertFalse(response.has_errors)

    def test_combined_available_query_pass(self):
        request = self.environ.get_request(query_string={'email': 'unit@test.com'})
        response = self.environ.get_response()
        requirements = {
            'required_query': ['email'],
            'available_query': ['first', 'name']
        }
        self.validator.validate_request(request, response, requirements)
        self.assertFalse(response.has_errors)

    def test_available_query_fails(self):
        request = self.environ.get_request(query_string={'email-fail': 'unit@test.com'})
        response = self.environ.get_response()
        requirements = {
            'available_query': ['email']
        }
        self.validator.validate_request(request, response, requirements)
        body = json.loads(next(response.get_response()).decode('utf-8'))
        self.assertTrue(response.has_errors)
        self.assertDictEqual({"errors": [{"key_path": "query_params", "message": "email-fail is not an available query_params"}]}, body)

    def test_required_body_pass(self):
        request = self.environ.get_request(json=self.passing_body)
        response = self.environ.get_response()
        requirements = {
            'required_body': 'v1-required-body-test'
        }
        self.validator.validate_request(request, response, requirements)
        self.assertFalse(response.has_errors)

    def test_required_body_fails(self):
        request = self.environ.get_request(json=self.failing_body)
        response = self.environ.get_response()
        requirements = {
            'required_body': 'v1-required-body-test'
        }
        self.validator.validate_request(request, response, requirements)
        body = json.loads(next(response.get_response()).decode('utf-8'))
        self.assertTrue(response.has_errors)
        self.assertDictEqual({"errors": [{"key_path": "id", "message": "'three' is not of type 'integer'"}]}, body)

    def test_required_body_fails_non_json(self):
        request = self.environ.get_request(data='some-thing')
        response = self.environ.get_response()
        requirements = {
            'required_body': 'v1-required-body-test'
        }
        self.validator.validate_request(request, response, requirements)
        body = json.loads(next(response.get_response()).decode('utf-8'))
        self.assertTrue(response.has_errors)
        self.assertEqual(
            {"errors": [{"key_path": "body", "message": "Expecting JSON; make ensure proper content-type headers and encoded body"}]},
            body
        )

    def test_required_body_pydantic_model_passes(self):
        request = self.environ.get_request(json=self.passing_body)
        response = self.environ.get_response()
        requirements = {
            'required_body': UserRequest
        }
        self.validator.validate_request(request, response, requirements)
        self.assertFalse(response.has_errors)

    def test_required_body_pydantic_model_fails(self):
        request = self.environ.get_request(json=self.failing_body)
        response = self.environ.get_response()
        requirements = {
            'required_body': UserRequest
        }
        self.validator.validate_request(request, response, requirements)
        body = json.loads(next(response.get_response()).decode('utf-8'))
        self.assertTrue(response.has_errors)
        self.assertEqual({"errors": [{"key_path": "id", "message": "'three' is not of type 'integer'"}]}, body)

    def test_openapi_validate_request_passes(self):
        request = self.environ.get_request(json=self.passing_body, path='/unit-test/v1/auto', headers={'x-api-key': 'some-key'})
        response = self.environ.get_response()
        self.validator.validate_request_with_openapi(request, response)
        self.assertFalse(response.has_errors)

    def test_openapi_validate_request_passes_with_all_parameters(self):
        request = self.environ.get_request(
            json=self.passing_body,
            path='/unit-test/v1/auto',
            headers={'x-api-key': 'some-key'},
            query_string={'unit_id': 'unit@test.com'},
            method='delete'
        )
        response = self.environ.get_response()
        self.validator.validate_request_with_openapi(request, response)
        self.assertFalse(response.has_errors)

    def test_openapi_validate_request_fails(self):
        request = self.environ.get_request(json=self.passing_body, path='/unit-test/v1/auto')
        response = self.environ.get_response()
        self.validator.validate_request_with_openapi(request, response)
        body = json.loads(next(response.get_response()).decode('utf-8'))
        self.assertTrue(response.has_errors)
        self.assertDictEqual({"errors": [{"key_path": "headers", "message": "Please provide x-api-key in headers"}]}, body)

    def test_route_has_security(self):
        request = self.environ.get_request(path='/unit-test/v1/auto', method='get')
        self.assertTrue(self.validator.request_has_security(request))

    def test_route_does_not_has_security(self):
        request = self.environ.get_request(path='/unit-test/v1/auto', method='post')
        self.assertFalse(self.validator.request_has_security(request))

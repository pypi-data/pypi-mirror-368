import json
import unittest

from tests.unit.mocks.rest.common.environment_builder import EnvironmentBuilder
from tests.unit.mocks.rest.common import middleware as mw

from chilo_api import Chilo


class RouterTest(unittest.TestCase):
    builder = EnvironmentBuilder()

    def __get_chilo_settings(self, **kwargs):
        return {
            'base_path': kwargs.get('base_path', '/'),
            'handlers':  kwargs.get('handlers', 'tests/unit/mocks/rest/handlers/valid'),
            'before_all': kwargs.get('before_all'),
            'after_all': kwargs.get('after_all'),
            'when_auth_required': kwargs.get('when_auth_required'),
            'timeout': kwargs.get('timeout'),
            'on_timeout': kwargs.get('on_timeout'),
            'on_error': kwargs.get('on_error'),
            'openapi': kwargs.get('openapi'),
            'openapi_validate_request': kwargs.get('openapi_validate_request'),
            'openapi_validate_response': kwargs.get('openapi_validate_response'),
            'verbose': kwargs.get('verbose'),
            'LOG_LEVEL': kwargs.get('LOG_LEVEL', 'NOTSET')
        }

    def __get_chilo_response_body(self, chilo_settings=None, **kwargs):
        settings = chilo_settings if chilo_settings is not None else self.__get_chilo_settings()
        chilo = Chilo(**settings)
        environ = self.builder.get_environ(**kwargs)
        response = chilo.route(environ, self.builder.mock_start_response)
        try:
            return json.loads(next(response).decode('utf-8'))  # type: ignore[return-value]
        except (StopIteration, json.JSONDecodeError):
            return {}

    def test_host_default(self):
        chilo = Chilo(base_path='/', handlers='tests/unit/mocks/rest/handlers/valid')
        self.assertEqual('127.0.0.1', chilo.host)

    def test_port_default(self):
        chilo = Chilo(base_path='/', handlers='tests/unit/mocks/rest/handlers/valid')
        self.assertEqual(3000, chilo.port)

    def test_reload_default(self):
        chilo = Chilo(base_path='/', handlers='tests/unit/mocks/rest/handlers/valid')
        self.assertFalse(chilo.reload)

    def test_verbose_default(self):
        chilo = Chilo(base_path='/', handlers='tests/unit/mocks/rest/handlers/valid')
        self.assertFalse(chilo.verbose)

    def test_timeout_default(self):
        chilo = Chilo(base_path='/', handlers='tests/unit/mocks/rest/handlers/valid')
        self.assertIsNone(chilo.timeout)

    def test_openapi_validate_request_default(self):
        chilo = Chilo(base_path='/', handlers='tests/unit/mocks/rest/handlers/valid')
        self.assertFalse(chilo.openapi_validate_request)

    def test_openapi_validate_response_default(self):
        chilo = Chilo(base_path='/', handlers='tests/unit/mocks/rest/handlers/valid')
        self.assertFalse(chilo.openapi_validate_response)

    def test_output_error_default(self):
        chilo = Chilo(base_path='/', handlers='tests/unit/mocks/rest/handlers/valid')
        self.assertFalse(chilo.output_error)

    def test_on_error_default(self):
        chilo = Chilo(base_path='/', handlers='tests/unit/mocks/rest/handlers/valid')
        self.assertIsNone(chilo.on_error)

    def test_on_timeout_default(self):
        chilo = Chilo(base_path='/', handlers='tests/unit/mocks/rest/handlers/valid')
        self.assertIsNone(chilo.on_timeout)

    def test_before_all_default(self):
        chilo = Chilo(base_path='/', handlers='tests/unit/mocks/rest/handlers/valid')
        self.assertIsNone(chilo.before_all)

    def test_after_all_default(self):
        chilo = Chilo(base_path='/', handlers='tests/unit/mocks/rest/handlers/valid')
        self.assertIsNone(chilo.after_all)

    def test_when_auth_required_default(self):
        chilo = Chilo(base_path='/', handlers='tests/unit/mocks/rest/handlers/valid')
        self.assertIsNone(chilo.when_auth_required)

    def test_cors_default(self):
        chilo = Chilo(base_path='/', handlers='tests/unit/mocks/rest/handlers/valid')
        self.assertFalse(chilo.cors)

    def test_route_passes(self):
        body = self.__get_chilo_response_body(path='/basic', method='patch')
        self.assertDictEqual({'router_directory_basic': 'PATCH'}, body)

    def test_route_fails_not_found(self):
        body = self.__get_chilo_response_body(path='/not-found', method='patch')
        self.assertDictEqual({'errors': [{'key_path': 'unknown', 'message': 'route not found'}]}, body)

    def test_route_fails_method_not_allowed(self):
        body = self.__get_chilo_response_body(path='/optional-params', method='patch')
        self.assertDictEqual({'errors': [{'key_path': 'unknown', 'message': 'method not allowed'}]}, body)

    def test_route_fails_handled_exception(self):
        body = self.__get_chilo_response_body(path='/raise-exception', method='post')
        self.assertDictEqual({'errors': [{'key_path': 'crazy_error', 'message': 'I am a teapot'}]}, body)

    def test_route_fails_unhandled_exception(self):
        body = self.__get_chilo_response_body(path='/unhandled-exception', method='post')
        self.assertDictEqual({'errors': [{'key_path': 'unknown', 'message': 'internal service error'}]}, body)

    def test_route_fails_timeout(self):
        chilo_settings = self.__get_chilo_settings(timeout=1)
        body = self.__get_chilo_response_body(chilo_settings=chilo_settings, path='/timeout', method='post')
        self.assertDictEqual({'errors': [{'key_path': 'unknown', 'message': 'request timeout'}]}, body)

    def test_router_calls_before_all(self):
        chilo_settings = self.__get_chilo_settings(before_all=mw.before_all)
        self.__get_chilo_response_body(chilo_settings=chilo_settings, path='/basic', method='patch')
        self.assertTrue(mw.before_all.called)  # type: ignore[unreachable]

    def test_router_calls_after_all(self):
        chilo_settings = self.__get_chilo_settings(after_all=mw.after_all)
        self.__get_chilo_response_body(chilo_settings=chilo_settings, path='/basic', method='patch')
        self.assertTrue(mw.after_all.called)  # type: ignore[unreachable]

    def test_router_calls_when_auth_required(self):
        chilo_settings = self.__get_chilo_settings(when_auth_required=mw.when_auth_required)
        self.__get_chilo_response_body(chilo_settings=chilo_settings, path='/basic', method='post')
        self.assertTrue(mw.when_auth_required.called)  # type: ignore[unreachable]

    def test_router_calls_on_error(self):
        chilo_settings = self.__get_chilo_settings(on_error=mw.on_error)
        self.__get_chilo_response_body(chilo_settings=chilo_settings, path='/raise-exception', method='post')
        self.assertTrue(mw.on_error.called)  # type: ignore[unreachable]

    def test_router_calls_on_error_and_handles_bad_method(self):
        chilo_settings = self.__get_chilo_settings(on_error=mw.bad_on_error)
        self.__get_chilo_response_body(chilo_settings=chilo_settings, path='/raise-exception', method='post')
        self.assertTrue(mw.bad_on_error.called)  # type: ignore[unreachable]

    def test_router_calls_on_timeout(self):
        chilo_settings = self.__get_chilo_settings(on_timeout=mw.on_timeout, timeout=1)
        self.__get_chilo_response_body(chilo_settings=chilo_settings, path='/timeout', method='post')
        self.assertTrue(mw.on_timeout.called)  # type: ignore[unreachable]

    def test_router_logs_verbose(self):
        chilo_settings = self.__get_chilo_settings(verbose=True)
        self.__get_chilo_response_body(chilo_settings=chilo_settings, path='/basic', method='post')
        self.assertTrue(True)

    def test_router_openapi_validate_requests_request_pass(self):
        json = {
            'test_id': 'uuid',
            'object_key': {
                'key': 'value'
            },
            'array_number': [1, 2, 3],
            'array_objects': [{'key': 1}],
            'fail_id': 'fail-uuid'
        }
        settings = self.__get_chilo_settings(
            base_path='/unit-test/v1',
            openapi='tests/unit/mocks/openapi/variations/openapi.yml',
            openapi_validate_request=True
        )
        body = self.__get_chilo_response_body(
            chilo_settings=settings,
            headers={'x-api-key': 'some-key'},
            path='/unit-test/v1/auto',
            method='post',
            json=json
        )
        self.assertDictEqual({'router_directory_auto': json}, body)

    def test_router_openapi_validate_requests_request_fails(self):
        expected = {'errors': [{'key_path': 'fail_id', 'message': "33 is not of type 'string'"}]}
        json = {
            'test_id': 'uuid',
            'object_key': {
                'key': 'value'
            },
            'array_number': [1, 2, 3],
            'array_objects': [{'key': 1}],
            'fail_id': 33,
        }
        settings = self.__get_chilo_settings(
            base_path='/unit-test/v1',
            openapi='tests/unit/mocks/openapi/variations/openapi.yml',
            openapi_validate_request=True
        )
        body = self.__get_chilo_response_body(
            chilo_settings=settings,
            headers={'x-api-key': 'some-key'},
            path='/unit-test/v1/auto',
            method='post',
            json=json
        )
        self.assertDictEqual(expected, body)

    def test_router_validate_response_pass(self):
        expected = {'page_number': 1, 'data': {'id': '2'}}
        settings = self.__get_chilo_settings(
            base_path='/unit-test/v1',
            openapi='tests/unit/mocks/openapi/variations/openapi.yml',
        )
        body = self.__get_chilo_response_body(
            chilo_settings=settings,
            headers={'x-api-key': 'some-key'},
            path='/unit-test/v1/auto',
            method='put'
        )
        self.assertDictEqual(expected, body)

    def test_router_validate_response_fails(self):
        expected = {
            'errors': [
                {'key_path': 'root', 'message': "'data' is a required property"},
                {'key_path': 'root', 'message': "Additional properties are not allowed ('bad-data' was unexpected)"},
                {'key_path': 'response', 'message': 'There was a problem with the APIs response; does not match defined schema'}
            ]
        }
        settings = self.__get_chilo_settings(
            base_path='/unit-test/v1',
            openapi='tests/unit/mocks/openapi/variations/openapi.yml'
        )
        body = self.__get_chilo_response_body(
            chilo_settings=settings,
            headers={'x-api-key': 'some-key'},
            path='/unit-test/v1/auto',
            method='get'
        )
        self.assertDictEqual(expected, body)

    def test_router_openapi_validate_response_pass(self):
        expected = {'page_number': 1, 'data': {'id': '2'}}
        settings = self.__get_chilo_settings(
            base_path='/unit-test/v1',
            openapi='tests/unit/mocks/openapi/variations/openapi.yml',
            openapi_validate_request=True,
            openapi_validate_response=True
        )
        body = self.__get_chilo_response_body(
            chilo_settings=settings,
            headers={'x-api-key': 'some-key'},
            path='/unit-test/v1/auto',
            method='put'
        )
        self.assertDictEqual(expected, body)

    def test_router_openapi_validate_response_pass_only(self):
        expected = {'page_number': 1, 'data': {'id': '2'}}
        settings = self.__get_chilo_settings(
            base_path='/unit-test/v1',
            openapi='tests/unit/mocks/openapi/variations/openapi.yml',
            openapi_validate_response=True
        )
        body = self.__get_chilo_response_body(
            chilo_settings=settings,
            headers={'x-api-key': 'some-key'},
            path='/unit-test/v1/auto',
            method='put'
        )
        self.assertDictEqual(expected, body)

    def test_router_openapi_validate_response_fails(self):
        expected = {
            'errors': [
                {'key_path': 'root', 'message': "'data' is a required property"},
                {'key_path': 'root', 'message': "Additional properties are not allowed ('bad-data' was unexpected)"},
                {'key_path': 'response', 'message': 'There was a problem with the APIs response; does not match defined schema'}
            ]
        }
        settings = self.__get_chilo_settings(
            base_path='/unit-test/v1',
            openapi='tests/unit/mocks/openapi/variations/openapi.yml',
            openapi_validate_request=True,
            openapi_validate_response=True
        )
        body = self.__get_chilo_response_body(
            chilo_settings=settings,
            headers={'x-api-key': 'some-key'},
            path='/unit-test/v1/auto',
            method='get'
        )
        self.assertDictEqual(expected, body)

    def test_router_openapi_validate_response_fails_only(self):
        expected = {
            'errors': [
                {'key_path': 'root', 'message': "'data' is a required property"},
                {'key_path': 'root', 'message': "Additional properties are not allowed ('bad-data' was unexpected)"},
                {'key_path': 'response', 'message': 'There was a problem with the APIs response; does not match defined schema'}
            ]
        }
        settings = self.__get_chilo_settings(
            base_path='/unit-test/v1',
            openapi='tests/unit/mocks/openapi/variations/openapi.yml',
            openapi_validate_response=True
        )
        body = self.__get_chilo_response_body(
            chilo_settings=settings,
            headers={'x-api-key': 'some-key'},
            path='/unit-test/v1/auto',
            method='get'
        )
        self.assertDictEqual(expected, body)

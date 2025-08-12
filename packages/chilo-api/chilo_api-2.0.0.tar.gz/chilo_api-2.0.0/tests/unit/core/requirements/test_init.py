import unittest
import json

from tests.unit.mocks.rest.common.environment_builder import EnvironmentBuilder
from tests.unit.mocks.rest.handlers.valid import full_handler as full
from tests.unit.mocks.rest.handlers.stream import stream, full_handler as stream_full

from chilo_api.core.exception import ApiTimeOutException


class RequirementsTest(unittest.TestCase):
    environ = EnvironmentBuilder()

    def __get_request_response(self, timeout=None):
        request = self.environ.get_request(timeout)
        response = self.environ.get_response()
        return request, response

    def test_requirements_decorator_has_attribute(self):
        self.assertTrue(hasattr(full.get, 'requirements'))

    def test_requirements_runs_before(self):
        request, response = self.__get_request_response()
        full.post(request, response)
        self.assertTrue(full.before_call.has_been_called)  # type: ignore

    def test_requirements_runs_after(self):
        request, response = self.__get_request_response()
        full.post(request, response)
        self.assertTrue(full.after_call.has_been_called)  # type: ignore

    def test_requirements_runs_in_correct_order(self):
        request, response = self.__get_request_response()
        full.post(request, response)
        self.assertEqual('before', full.call_order[0])
        self.assertEqual('after', full.call_order[1])

    def test_requirements_passes_after_request_class(self):
        request, response = self.__get_request_response()
        full.post(request, response)
        body = next(response.get_response()).decode('utf-8')
        self.assertDictEqual({'requirements_basic': True}, json.loads(body))

    def test_requirements_global_timeout_raises_exception(self):
        request, response = self.__get_request_response(timeout=1)
        with self.assertRaises(ApiTimeOutException):
            full.get(request, response)

    def test_requirements_local_timeout_raises_exception(self):
        request, response = self.__get_request_response()
        with self.assertRaises(ApiTimeOutException):
            full.patch(request, response)

    def test_requirements_local_overwrites_global_timeout_setting(self):
        request, response = self.__get_request_response(timeout=10)
        with self.assertRaises(ApiTimeOutException):
            full.patch(request, response)

    def test_requirements_fail_before(self):
        request, response = self.__get_request_response(timeout=10)
        response = stream_full.delete(request, response)
        self.assertEqual(response.code, 400)
        self.assertEqual(response.raw, {'errors': [{'key_path': 'failed before', 'message': 'failed'}]})

    def test_stream_response_success(self):
        request, response = self.__get_request_response()
        generator = stream.success(request, response)
        self.assertEqual(next(generator).raw, {'message': 'This is a stream response'})

    def test_stream_response_fail(self):
        request, response = self.__get_request_response()
        generator = stream.fail(request, response)
        with self.assertRaises(StopIteration) as context:
            next(generator)
        self.assertEqual(context.exception.args[0].raw, {'errors': [{'key_path': 'failed before', 'message': 'failed'}]})

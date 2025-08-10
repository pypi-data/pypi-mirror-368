import base64
import gzip
import json
import unittest

from tests.unit.mocks.rest.common.environment_builder import EnvironmentBuilder


class ResponseTest(unittest.TestCase):
    environ = EnvironmentBuilder()

    def setUp(self):
        self.response = self.environ.get_response()

    def test_defaults(self):
        self.response.body = {'unit-test': True}
        self.assertFalse(self.response.has_errors)
        self.assertFalse(self.response.compress)
        self.assertIsNone(self.response.cors)
        self.assertEqual('application/json', self.response.mimetype)
        self.assertEqual(200, self.response.code)

    def test_cors_is_star_on_boolean(self):
        self.response.cors = True
        self.assertEqual('*', self.response.headers['Access-Control-Allow-Origin'])

    def test_cors_custom_on_string(self):
        self.response.cors = 'https://foo.example'
        self.assertEqual('https://foo.example', self.response.headers['Access-Control-Allow-Origin'])

    def test_compress(self):
        self.response.body = {'unit-test': True}
        self.response.compress = True
        body = next(self.response.get_response())
        decoded = json.loads(gzip.decompress(base64.b64decode(body)))
        self.assertEqual(self.response.headers['Content-Encoding'], 'gzip')
        self.assertDictEqual(decoded, {'unit-test': True})

    def test_assigned_code(self):
        self.response.code = 201
        self.assertEqual(201, self.response.code)

    def test_empty_body_default_code(self):
        self.assertEqual(204, self.response.code)

    def test_error_body_default_code(self):
        self.response.set_error('some-error-key', 'some-error-value')
        self.assertEqual(400, self.response.code)

    def test_set_error(self):
        expected = {'errors': [{'key_path': 'some-error-key', 'message': 'some-error-value'}]}
        self.response.set_error('some-error-key', 'some-error-value')
        body = next(self.response.get_response()).decode('utf-8')
        self.assertDictEqual(json.loads(body), expected)

    def test_has_error(self):
        self.response.set_error('some-error-key', 'some-error-value')
        self.assertTrue(self.response.has_errors)

    def test_default_mimetype_with_default_is_json(self):
        self.assertEqual('application/json', self.response.mimetype)

    def test_default_content_type_set_will_stick(self):
        self.response.mimetype = 'application/xml'
        self.assertEqual('application/xml', self.response.mimetype)

    def test_default_mimetype_follows_headers(self):
        self.response.headers = ('Content-Type', 'text/html; charset=UTF-8')
        self.assertEqual('text/html', self.response.mimetype)

    def test_raw(self):
        self.response.body = {'raw': True}
        self.assertIsNotNone(self.response.raw)
        self.assertIsInstance(self.response.raw, dict)
        self.assertDictEqual({'raw': True}, self.response.raw)  # type: ignore[unreachable]

    def test_no_json_body(self):
        expected = 'works!'
        self.response.body = expected
        self.assertEqual(expected, self.response.body)

    def test_to_str(self):
        expected = {'headers': {}, 'mimetype': 'application/json', 'cors': None, 'compress': False, 'code': 204, 'body': None}
        self.assertEqual(str(expected), str(self.response))

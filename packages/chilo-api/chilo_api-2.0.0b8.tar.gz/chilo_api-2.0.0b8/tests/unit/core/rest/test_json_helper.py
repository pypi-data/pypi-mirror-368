import json
import unittest

from chilo_api.core.rest.json_helper import JsonHelper


class JsonHelperTest(unittest.TestCase):

    def test_decode_pass(self):
        json_obj = {'unit': 'test'}
        json_string = json.dumps(json_obj)
        result = JsonHelper.decode(json_string)
        self.assertDictEqual(json_obj, result)

    def test_decode_fails_no_error(self):
        json_string = 'some-string'
        result = JsonHelper.decode(json_string)
        self.assertEqual(json_string, result)

    def test_decode_fails_raise_error(self):
        json_string = 'some-string'
        with self.assertRaises(Exception) as context:
            JsonHelper.decode(json_string, raise_error=True)
        self.assertIn('JSON is malformed', str(context.exception))

    def test_encode_pass(self):
        json_obj = {'unit': 'test'}
        result = JsonHelper.encode(json_obj)
        self.assertEqual('{"unit":"test"}', result)

    def test_encode_fails_no_error(self):
        json_string = 'some-string'
        result = JsonHelper.encode(json_string)
        self.assertEqual(f'"{json_string}"', result)

    def test_encode_fails_raise_error(self):
        class BadJSON:
            pass
        json_obj = BadJSON()
        with self.assertRaises(Exception) as context:
            JsonHelper.encode(json_obj, raise_error=True)
        self.assertIn('Encoding objects of type BadJSON', str(context.exception))

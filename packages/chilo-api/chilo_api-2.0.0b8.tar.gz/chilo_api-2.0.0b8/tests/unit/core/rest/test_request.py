
import base64
from io import BytesIO
import json
import unittest

from tests.unit.mocks.rest.common.environment_builder import EnvironmentBuilder


class RequestTest(unittest.TestCase):
    environ = EnvironmentBuilder()

    def test_wsgi(self):
        request = self.environ.get_request()
        self.assertIsInstance(request.wsgi, self.environ.mock_request_class)
    
    def test_api_type(self):
        request = self.environ.get_request()
        self.assertEqual('rest', request.api_type)

    def test_authorization(self):
        auth = {'Authorization': 'Bearer 123456789'}
        request = self.environ.get_request(headers=auth)
        self.assertEqual(auth['Authorization'].split('Bearer ')[1], request.authorization.token)

    def test_cookies(self):
        cookie = {'Cookie': 'unit=test'}
        request = self.environ.get_request(headers=cookie)
        self.assertDictEqual({'unit': 'test'}, request.cookies)

    def test_protocol(self):
        request = self.environ.get_request()
        self.assertEqual('http', request.protocol)

    def test_content_type(self):
        request = self.environ.get_request(json={'unit': 'test'})
        self.assertEqual('application/json', request.content_type)

    def test_mimetype(self):
        request = self.environ.get_request(json={'unit': 'test'})
        self.assertEqual('application/json', request.mimetype)

    def test_host_url(self):
        request = self.environ.get_request()
        self.assertEqual('http://localhost/', request.host_url)

    def test_domain(self):
        request = self.environ.get_request()
        self.assertEqual('localhost', request.domain)

    def test_method(self):
        request = self.environ.get_request(method='get')
        self.assertEqual('get', request.method)

    def test_path(self):
        request = self.environ.get_request(path='/basic')
        self.assertEqual('/basic', request.path)

    def test_route(self):
        request = self.environ.get_request(path='/basic/1')
        request.route = '/basic/{id}'
        self.assertEqual('/basic/{id}', request.route)
        request.route = 'basic/{id}'
        self.assertEqual('/basic/{id}', request.route)

    def test_headers(self):
        headers = {'host': 'localhost', 'x-unit-key': 'test'}
        request = self.environ.get_request(headers=headers)
        self.assertDictEqual(headers, request.headers)

    def test_body(self):
        json = {'unit': 'test'}
        request = self.environ.get_request(json=json)
        self.assertDictEqual(json, request.body)

    def test_json(self):
        json = {'unit': 'test'}
        request = self.environ.get_request(json=json)
        self.assertDictEqual(json, request.json)

    def test_json_bad(self):
        bad_json = '{"missing-quote : "bad"}'
        request = self.environ.get_request(data=bad_json, mimetype='application/json')
        self.assertEqual(bad_json, request.body)

    def test_form(self):
        data = {'unit': 'test'}
        request = self.environ.get_request(data=data, method='POST')
        self.assertDictEqual(data, request.form)

    def test_xml(self):
        expected = {
            'root': {
                '@xmlns': 'http://defaultns.com/',
                '@xmlns:a': 'http://a.com/',
                '@xmlns:b': 'http://b.com/',
                'x': '1',
                'a:y': '2',
                'b:z': '3'
            }
        }
        data = '<root xmlns="http://defaultns.com/" xmlns:a="http://a.com/" xmlns:b="http://b.com/"><x>1</x><a:y>2</a:y><b:z>3</b:z></root>'
        request = self.environ.get_request(data=data, content_type='application/xml')
        self.assertDictEqual(expected, request.xml)

    def test_files(self):
        expceted = 'file contents'
        data = {
            'name': 'test',
            'file': (BytesIO(expceted.encode('utf8')), 'test.txt')
        }
        request = self.environ.get_request(data=data, method='POST')
        self.assertEqual(expceted, request.files['file'].read().decode())

    def test_graphql(self):
        expected = {
            'query': 'query GreetingQuery ($arg1: String) { hello (name: $arg1) { value } }',
            'operationName': 'GreetingQuery',
            'variables': {'arg1': 'Timothy'}
        }
        request = self.environ.get_request(data=base64.b64encode(json.dumps(expected).encode()), content_type='application/graphql')
        self.assertDictEqual(expected, request.graphql)

    def test_raw(self):
        data = 'unit-test'
        request = self.environ.get_request(data=data, method='POST')
        self.assertEqual(data, request.raw.decode())

    def test_query_params(self):
        params = {'unit': 'test'}
        request = self.environ.get_request(query_string=params)
        self.assertDictEqual(params, request.query_params)

    def test_path_params(self):
        path = '/basic/{id}'
        request = self.environ.get_request(path=path)
        request.path_params = ('id', 1)
        self.assertDictEqual({'id': 1}, request.path_params)

    def test_context(self):
        context = {'unit': 'test'}
        request = self.environ.get_request()
        request.context = context
        self.assertDictEqual(context, request.context)

    def test_timeout(self):
        timeout = 30
        request = self.environ.get_request(timeout=timeout)
        self.assertEqual(timeout, request.timeout)

    def test_clear_path_params(self):
        path = '/basic/{id}'
        request = self.environ.get_request(path=path)
        request.path_params = ('id', 1)
        self.assertDictEqual({'id': 1}, request.path_params)
        request.clear_path_params()
        self.assertDictEqual({}, request.path_params)

    def test_to_str(self):
        expected = {'method': 'get', 'headers': {'host': 'localhost'}, 'query': {}, 'path': {},  'body': b'', 'context': {}}
        request = self.environ.get_request()
        self.assertEqual(str(expected), str(request))

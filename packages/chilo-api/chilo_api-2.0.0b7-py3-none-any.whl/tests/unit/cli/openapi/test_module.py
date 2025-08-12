import importlib.util
import unittest

from chilo_api.cli.openapi.module import OpenAPIHandlerModule


class OpenAPIHandlerModuleTest(unittest.TestCase):

    def __setup_module(self, **kwargs):
        file_path = kwargs.get('file_path', 'tests/unit/mocks/rest/handlers/valid/basic.py')
        import_path = kwargs.get('import_path', 'tests.unit.mocks.rest.handlers.valid.basic')
        method = kwargs.get('method', 'post')
        spec = importlib.util.spec_from_file_location(import_path, file_path)
        if spec is None:
            raise ImportError(f"Cannot load spec for {import_path} from {file_path}")
        handler_module = importlib.util.module_from_spec(spec)
        if spec.loader is None:
            raise ImportError(f"Cannot load module loader for {import_path} from {file_path}")
        spec.loader.exec_module(handler_module)
        return OpenAPIHandlerModule(
            handler_base='tests/unit/mocks/',
            file_path=file_path,
            module=handler_module,
            method=method,
            base='chilo/example'
        )

    def setUp(self):
        self.module = self.__setup_module()

    def test_file_path(self):
        self.assertEqual(self.module.file_path, 'tests/unit/mocks/rest/handlers/valid/basic.py')

    def test_module(self):
        self.assertEqual(len(dir(self.module.module)), 15)

    def test_method(self):
        self.assertEqual(self.module.method, 'post')

    def test_operation_id(self):
        self.assertEqual(self.module.operation_id, 'PostChiloExampleRestHandlersValidBasicChiloGenerated')

    def test_route_path(self):
        self.assertEqual(self.module.route_path, '/chilo/example/rest/handlers/valid/basic')

    def test_deprecated(self):
        self.assertFalse(self.module.deprecated)

    def test_summary(self):
        self.assertIsNone(self.module.summary)

    def test_tags(self):
        self.assertListEqual(['chilo-example'], self.module.tags)

    def test_requires_auth(self):
        self.assertTrue(self.module.requires_auth)

    def test_required_headers(self):
        self.assertListEqual([], self.module.required_headers)

    def test_available_headers(self):
        self.assertListEqual([], self.module.available_headers)

    def test_required_query(self):
        self.assertListEqual([], self.module.required_query)

    def test_available_query(self):
        self.assertListEqual([], self.module.available_query)

    def test_required_path_params_empty(self):
        self.assertListEqual([], self.module.required_path_params)

    def test_required_path_params(self):
        self.assertEqual(self.module.request_body_schema_name, 'post-chilo-example-rest-handlers-valid-basic-request-body')

    def test_response_body_schema_name(self):
        self.assertEqual(self.module.response_body_schema_name, 'post-chilo-example-rest-handlers-valid-basic-response-body')

    def test_request_body_schema_is_none(self):
        module = self.__setup_module()
        assert module.request_body_schema is None

    def test_dynamic_route_path(self):
        module = self.__setup_module(
            method='get',
            file_path='tests/unit/mocks/rest/handlers/valid/user/_user_id/item/_item_id.py',
            import_path='tests.unit.mocks.rest.handlers.valid.user._user_id.item._item_id'
        )
        self.assertEqual(module.route_path, '/chilo/example/user/{user_id}/item/{item_id}')

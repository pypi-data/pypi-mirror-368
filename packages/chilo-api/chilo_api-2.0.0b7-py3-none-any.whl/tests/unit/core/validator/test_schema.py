import unittest
from typing import Any, Dict, Union

from pydantic import BaseModel
from collections.abc import Mapping

from chilo_api.core.validator import Schema
from tests.unit.mocks.rest.common.pydantic_class import Request


class SchemaTest(unittest.TestCase):
    maxDiff = None
    schema_path = 'tests/unit/mocks/openapi/variations/openapi.yml'
    schema_path_with_base_path = 'tests/unit/mocks/openapi/variations/openapi-with-base-path.yml'

    schema_dict = {
        'type': 'object',
        'required': ['id', 'body'],
        'additionalProperties': False,
        'properties': {
            'id': {'type': 'string'},
            'body': {'type': 'object'},
            'dict': {'type': 'boolean'}
        }
    }

    expected_dict_from_path = {
        'type': 'object',
        'required': ['id', 'body'],
        'additionalProperties': False,
        'properties': {
            'id': {'type': 'string'},
            'body': {'type': 'object'},
            'file': {'type': 'boolean'}
        }
    }

    expected_dict_from_dict = {
        'type': 'object',
        'required': ['id', 'body'],
        'additionalProperties': False,
        'properties': {
            'id': {'type': 'string'},
            'body': {'type': 'object'},
            'dict': {'type': 'boolean'}
        }
    }

    expected_combined_dict = {
        'type': 'object',
        'properties': {
            'test_id': {'type': 'string'},
            'object_key': {
                'type': 'object',
                'properties': {
                    'string_key': {'type': 'string'}
                }
            },
            'array_number': {
                'type': 'array',
                'items': {'type': 'number'}
            },
            'array_objects': {
                'type': 'array',
                'items': {
                    'type': 'object',
                    'properties': {
                        'array_string_key': {'type': 'string'},
                        'array_number_key': {'type': 'number'}
                    }
                }
            },
            'fail_id': {'type': 'string'}
        },
        'required': ['test_id', 'object_key', 'array_number', 'array_objects'],
        'additionalProperties': False
    }

    expected_route_spec = {
        'tags': ['unit-test'],
        'operationId': 'GetSchema',
        'deprecated': False,
        'parameters': [
            {
                'in': 'query',
                'name': 'test_id',
                'required': False,
                'schema': {'type': 'string'}
            },
            {
                'in': 'query',
                'name': 'unit_id',
                'required': True,
                'schema': {'type': 'string'}
            }
        ],
        'responses': {
            '200': {
                'description': 'valid',
                'content': {
                    'application/json': {
                        'schema': {
                            'type': 'object',
                            'properties': {
                                'page_number': {'type': 'number'},
                                'data': {
                                    'type': 'object',
                                    'required': ['id'],
                                    'properties': {
                                        'id': {'type': 'string'}
                                    }
                                }
                            },
                            'required': ['page_number', 'data']
                        }
                    }
                }
            }
        }
    }

    def _normalize_spec_to_dict(self, spec: Union[Dict[str, Any], BaseModel, Mapping, Any]) -> Dict[str, Any]:
        '''
        Helper method to normalize different spec formats to a dictionary.
        Handles BaseModel, Mapping, and other types consistently.
        '''
        if isinstance(spec, type) and issubclass(spec, BaseModel):
            return spec.schema()
        if isinstance(spec, Mapping) and not isinstance(spec, dict):
            return dict(spec)
        if not isinstance(spec, dict):
            self.fail(f"spec is not a dict or convertible to dict: {type(spec)}")
        return spec

    def test_get_openapi_spec(self):
        schema_factory = Schema(openapi=self.schema_path)
        spec = schema_factory.get_openapi_spec()
        self.assertIsInstance(spec, dict)

    def test_get_body_spec_from_file(self):
        schema = Schema(openapi=self.schema_path)
        spec = schema.get_body_spec('v1-schema-factory-test')

        normalized_spec = self._normalize_spec_to_dict(spec)
        self.assertDictEqual(self.expected_dict_from_path, normalized_spec)

    def test_get_combined_body_spec_from_file(self):
        schema = Schema(openapi=self.schema_path)
        spec = schema.get_body_spec('v1-test-request')

        normalized_spec = self._normalize_spec_to_dict(spec)
        self.assertDictEqual(self.expected_combined_dict, normalized_spec)

    def test_get_body_spec_from_pydantic_model(self):
        schema = Schema(openapi=self.schema_path)
        spec = schema.get_body_spec(Request)  # type: ignore
        normalized_spec = self._normalize_spec_to_dict(spec)

        # Verify it's either a BaseModel subclass or a dict
        if isinstance(spec, type):
            self.assertTrue(issubclass(spec, BaseModel))
        else:
            self.assertIsInstance(normalized_spec, dict)

    def test_get_spec_from_route(self):
        schema = Schema(openapi=self.schema_path)
        spec = schema.get_route_spec('/unit-test/v1/schema', 'get')
        self.assertDictEqual(self.expected_route_spec, spec)

    def test_get_spec_from_route_with_base_path(self):
        schema = Schema(openapi=self.schema_path_with_base_path)
        spec = schema.get_route_spec('/unit-test/v1/schema', 'get')
        self.assertDictEqual(self.expected_route_spec, spec)

    def test_get_body_spec_from_dict(self):
        schema = Schema(openapi=self.schema_path)
        spec = schema.get_body_spec(self.schema_dict)

        normalized_spec = self._normalize_spec_to_dict(spec)
        self.assertDictEqual(self.expected_dict_from_dict, normalized_spec)

    def test_get_body_spec_invalid_input(self):
        schema = Schema(openapi=self.schema_path)

        with self.assertRaises((ValueError, TypeError, KeyError)):
            schema.get_body_spec('nonexistent-schema')

    def test_get_route_spec_invalid_route(self):
        schema = Schema(openapi=self.schema_path)

        with self.assertRaises((ValueError, KeyError)):
            schema.get_route_spec('/nonexistent/route', 'get')

    def test_get_route_spec_invalid_method(self):
        schema = Schema(openapi=self.schema_path)

        with self.assertRaises((ValueError, KeyError)):
            schema.get_route_spec('/unit-test/v1/schema', 'invalid_method')

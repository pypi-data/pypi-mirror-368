import copy
import json
import inspect
from typing import Dict, Any, Optional, Union

import jsonref
from pydantic import BaseModel
import yaml


class Schema:
    '''A class to handle OpenAPI schema loading and manipulation.
    This class is responsible for loading the OpenAPI schema from a file, resolving references, and providing methods to access the schema components.
    Attributes
    ----------
    openapi: Optional[str]
        The path to the OpenAPI schema file.
    config: Dict[str, Any]
        Configuration settings for the schema, such as whether to allow additional properties.
    spec: Optional[Dict[str, Any]]
        The loaded OpenAPI schema specification.
    paths: Union[Dict[str, Any], str]
        The paths defined in the OpenAPI schema, or an empty string if not available.
    Methods
    ----------
    load_schema_file():
        Loads the OpenAPI schema from the specified file.
    get_openapi_spec() -> Optional[Dict[str, Any]]:
        Returns the loaded OpenAPI schema specification.
    get_body_spec(required_body: Optional[Union[BaseModel, Dict[str, Any], str]] = None) -> Union[BaseModel, Dict[str, Any]]:
        Returns the body specification for the given required body, which can be a Pydantic model, a dictionary, or a string reference.
    get_route_spec(route: str, method: str) -> Dict[str, Any]:
        Returns the route specification for the given route and method. 
    '''

    def __init__(self, **kwargs: Any) -> None:
        self.__openapi: Optional[str] = kwargs.get('openapi')
        self.__config: Dict[str, Any] = kwargs.get('schema_config', {})
        self.__spec: Optional[Dict[str, Any]] = None

    @property
    def spec(self) -> Optional[Dict[str, Any]]:
        return self.__spec

    @property
    def paths(self) -> Union[Dict[str, Any], str]:
        self.__get_full_spec()
        return self.spec['paths'] if self.spec and self.spec.get('paths') else ''

    def load_schema_file(self) -> None:
        self.__get_full_spec()

    def get_openapi_spec(self) -> Optional[Dict[str, Any]]:
        return self.__get_full_spec()

    def get_body_spec(self, required_body: Optional[Union[BaseModel, Dict[str, Any], str]] = None) -> Union[BaseModel, Dict[str, Any]]:
        body_spec: Dict[str, Any] = {}
        if required_body and inspect.isclass(required_body) and issubclass(required_body, BaseModel):
            return required_body.model_json_schema()
        if required_body and isinstance(required_body, dict):
            body_spec = required_body
        elif required_body and isinstance(required_body, str):
            body_spec = self.__get_component_spec(required_body)
        body_spec['additionalProperties'] = self.__config.get('allow_additional_properties', False)
        return body_spec

    def get_route_spec(self, route: str, method: str) -> Dict[str, Any]:
        return self.__get_route_spec(route, method)

    def __get_full_spec(self) -> Optional[Dict[str, Any]]:
        if not self.spec and self.__openapi:
            unresolved_spec = self.__get_spec_from_file()
            resolved_spec = jsonref.loads(json.dumps(unresolved_spec), jsonschema=True, merge_props=True)
            self.__spec = self.__combine_all_of_spec(resolved_spec)
        return self.spec

    def __get_spec_from_file(self) -> Dict[str, Any]:
        if not self.__openapi:
            raise RuntimeError('OpenAPI file path is not set.')  # pragma: no cover
        with open(self.__openapi, encoding='utf-8') as schema_file:
            return yaml.load(schema_file, Loader=yaml.FullLoader)

    def __combine_all_of_spec(self, spec: Dict[str, Any]) -> Dict[str, Any]:
        combined = copy.deepcopy(spec)
        return self.__walk_spec(spec, combined)

    def __walk_spec(self, spec: Dict[str, Any], combined_spec: Dict[str, Any]) -> Dict[str, Any]:
        for spec_key in spec:
            if spec_key == 'allOf':
                self.__combine_all_of(spec, spec_key, combined_spec)
            elif isinstance(spec[spec_key], dict):
                self.__walk_spec(spec[spec_key], combined_spec[spec_key])
            elif isinstance(spec[spec_key], list):
                self.__iter_spec_list(spec, spec_key, combined_spec)
        return combined_spec

    def __combine_all_of(self, spec: Dict[str, Any], spec_key: str, combined_spec: Dict[str, Any]) -> None:
        combined: Dict[str, Any] = {
            'type': 'object',
            'properties': {},
            'required': []
        }
        for all_of in spec[spec_key]:
            if isinstance(all_of, dict) and all_of.get('properties'):
                combined['properties'].update(all_of['properties'])
            if isinstance(all_of, dict) and all_of.get('required'):
                combined['required'] += all_of['required']
        if combined['properties']:
            del combined_spec['allOf']
            combined_spec.update(combined)

    def __iter_spec_list(self, spec: Dict[str, Any], spec_key: str, combined_spec: Dict[str, Any]) -> None:
        for index, item in enumerate(spec[spec_key]):
            if isinstance(item, dict):
                self.__walk_spec(item, combined_spec[spec_key][index])

    def __get_component_spec(self, required_body: str) -> Dict[str, Any]:
        spec = self.__get_full_spec()
        if not spec or 'components' not in spec or not spec['components'] or 'schemas' not in spec['components'] or not spec['components']['schemas']:
            raise RuntimeError("OpenAPI spec, components, or schemas are missing or None.")  # pragma: no cover
        return spec['components']['schemas'][required_body]

    def __get_route_spec(self, route: str, method: str) -> Dict[str, Any]:
        spec = self.__get_full_spec()
        if not spec or 'paths' not in spec or spec['paths'] is None:
            raise ValueError('OpenAPI spec or paths are missing or None.')
        if spec.get('basePath'):
            route = route.replace(spec['basePath'], '')
        if route not in spec['paths']:
            raise ValueError(f'Route \"{route}\" not found in OpenAPI paths.')
        if method not in spec['paths'][route]:
            raise ValueError(f'Method \"{method}\" not found for route \"{route}\" in OpenAPI paths.')
        return spec['paths'][route][method]

from collections import defaultdict
from typing import Any, Dict, List, Optional, Union, Type

from jsonschema import Draft7Validator
from pydantic import BaseModel, ValidationError

from chilo_api.core.validator.openapi import OpenApiValidator
from chilo_api.core.validator.schema import Schema
from chilo_api.core.rest.request import RestRequest as Request
from chilo_api.core.rest.response import RestResponse as Response


class Validator:
    '''
    A class to validate API requests and responses against OpenAPI specifications.
    This class provides methods to validate request bodies, headers, query parameters, and responses against the OpenAPI schema.
    Attributes
    ----------
    schema: Schema
        An instance of the Schema class to handle OpenAPI schema loading and manipulation.
    openapi_validator: OpenApiValidator
        An instance of the OpenApiValidator class to validate OpenAPI specifications.
    pairings: Dict[str, str]
        A dictionary mapping requirement types to their corresponding request attributes.
    Methods
    ----------
    auto_load():
        Loads the OpenAPI schema and validates it against the defined routes and methods.
    request_has_security(request: Request) -> bool:
        Checks if the request has security requirements defined in the OpenAPI schema.
    validate_request_with_openapi(request: Request, response: Response, *_: Any) -> None:
        Validates the request against the OpenAPI schema, checking required fields and body specifications.
    validate_request(request: Request, response: Response, requirements: Dict[str, Any]) -> None:
        Validates the request against the provided requirements, checking required and available fields in headers, query parameters, and body.
    validate_response_with_openapi(request: Request, response: Response, *_: Any) -> None:
        Validates the response against the OpenAPI schema, checking required response specifications.
    validate_response(request: Request, response: Response, requirements: Dict[str, Any]) -> None:
        Validates the response against the provided requirements, checking the response body against the OpenAPI schema.
    check_required_fields(response: Response, required: List[str], sent: Any, list_name: str = '') -> None:
        Checks if the required fields are present in the sent data and sets errors in the response if any fields are missing.
    check_available_fields(response: Response, available: List[str], sent: Any, list_name: str = '') -> None:
        Checks if the available fields are present in the sent data and sets errors in the response if any fields are not allowed.
    combine_available_with_required(requirements: Dict[str, Any], required: str) -> List[str]:
        Combines the available fields with the required fields for validation purposes.
    check_required_body(response: Response, schema: Optional[Union[Dict[str, Any], Type[BaseModel]]], request_body: Any) -> bool:
        Checks if the request body matches the required schema and sets errors in the response if it does not.
    combine_parameters(parameters: List[Dict[str, Any]]) -> Dict[str, List[str]]:
        Combines parameters from the OpenAPI schema into a dictionary of required and available fields for headers and query parameters.
    format_schema_error_key(schema_error: Any) -> str:
        Formats the schema error key for better readability in error messages.
    is_json_serializable(response: Response, request_body: Any) -> bool:
        Checks if the request body is JSON serializable and sets an error in the response if it is not.
    '''

    def __init__(self, **kwargs: Any) -> None:
        self.__schema: Schema = Schema(**kwargs)
        self.__openapi_validator: OpenApiValidator = OpenApiValidator(**kwargs)
        self.__pairings: Dict[str, str] = {
            'required_headers': 'headers',
            'available_headers': 'headers',
            'required_query': 'query_params',
            'available_query': 'query_params',
            'required_body': 'body'
        }

    def auto_load(self) -> None:
        self.__schema.load_schema_file()
        self.__openapi_validator.validate_openapi()

    def request_has_security(self, request: Request) -> bool:
        route_spec: Dict[str, Any] = self.__schema.get_route_spec(request.route, request.method)
        if route_spec.get('security'):
            return True
        return False

    def validate_request_with_openapi(self, request: Request, response: Response, *_: Any) -> None:
        route_spec: Dict[str, Any] = self.__schema.get_route_spec(request.route, request.method)
        requirements: Dict[str, Any] = Validator.combine_parameters(route_spec.get('parameters', []))
        if route_spec.get('requestBody'):
            requirements['required_body'] = route_spec['requestBody']['content'][request.content_type]['schema']
        self.validate_request(request, response, requirements)

    def validate_request(self, request: Request, response: Response, requirements: Dict[str, Any]) -> None:
        if not requirements:
            return
        for required, source in self.__pairings.items():
            if requirements.get(required) and required == 'required_body':
                body_spec = self.__schema.get_body_spec(requirements[required])
                if isinstance(body_spec, BaseModel):
                    body_spec_type: Union[Dict[str, Any], Type[BaseModel], None] = type(body_spec)  # pragma: no cover
                else:
                    body_spec_type = body_spec
                Validator.check_required_body(response, body_spec_type, getattr(request, source))
            elif requirements.get(required) and 'required' in required:
                Validator.check_required_fields(response, requirements[required], getattr(request, source), source)
            elif requirements.get(required) and 'available' in required:
                full_list: List[str] = Validator.combine_available_with_required(requirements, required)
                Validator.check_available_fields(response, full_list, getattr(request, source), source)
        if response.has_errors:
            response.code = 400

    def validate_response_with_openapi(self, request: Request, response: Response, *_: Any) -> None:
        requirements: Dict[str, Any] = {}
        route_spec: Dict[str, Any] = self.__schema.get_route_spec(request.route, request.method)
        if route_spec.get('responses', {}).get(f'{response.code}', {}).get('content', {}).get(response.mimetype, {}).get('schema'):
            requirements['required_response'] = route_spec['responses'][f'{response.code}']['content'][response.mimetype]['schema']
            self.validate_response(request, response, requirements)

    def validate_response(self, _: Request, response: Response, requirements: Dict[str, Any]) -> None:
        if not requirements:
            return  # pragma: no cover
        body_spec = self.__schema.get_body_spec(requirements.get('required_response'))
        if isinstance(body_spec, BaseModel):
            body_spec_type: Union[Dict[str, Any], Type[BaseModel], None] = type(body_spec)  # pragma: no cover
        else:
            body_spec_type = body_spec
        Validator.check_required_body(response, body_spec_type, response.raw)
        if response.has_errors:
            response.set_error('response', 'There was a problem with the APIs response; does not match defined schema')
            response.code = 500

    @staticmethod
    def check_required_fields(response: Response, required: List[str], sent: Any, list_name: str = '') -> None:
        sent_keys: List[str] = []
        if isinstance(sent, dict) and len(sent.keys()) > 0:
            sent_keys = [key.lower() for key in sent.keys()]
        missing_fields: List[str] = [value for value in required if value.lower() not in sent_keys]
        if len(required) > 0 and len(missing_fields) > 0:
            for field in missing_fields:
                response.set_error(list_name, f'Please provide {field} in {list_name}')

    @staticmethod
    def check_available_fields(response: Response, available: List[str], sent: Any, list_name: str = '') -> None:
        sent_keys: List[str] = []
        if isinstance(sent, dict) and len(sent.keys()) > 0:
            sent_keys = [key.lower() for key in sent.keys()]
        unavailable_fields: List[str] = [value for value in sent_keys if value.lower() not in available]
        if len(available) > 0 and len(unavailable_fields) > 0:
            for field in unavailable_fields:
                response.set_error(list_name, f'{field} is not an available {list_name}')

    @staticmethod
    def combine_available_with_required(requirements: Dict[str, Any], required: str) -> List[str]:
        avail_list: List[str] = requirements[required]
        if required == 'available_query' and requirements.get('required_query'):
            avail_list += requirements['required_query']
        elif required == 'available_headers' and requirements.get('required_headers'):
            avail_list += requirements['required_headers']
        return avail_list

    @staticmethod
    def check_required_body(response: Response, schema: Optional[Union[Dict[str, Any], Type[BaseModel]]], request_body: Any) -> bool:
        if not Validator.is_json_serializable(response, request_body):
            return False
        if schema and isinstance(schema, dict):
            schema_validator: Draft7Validator = Draft7Validator(schema)
            for schema_error in sorted(schema_validator.iter_errors(request_body), key=str):
                error_key: str = Validator.format_schema_error_key(schema_error)
                response.set_error(key_path=error_key, message=schema_error.message)
        elif schema and isinstance(schema, type) and issubclass(schema, BaseModel):  # pragma: no cover
            try:
                schema(**request_body)
            except ValidationError as error:
                for err in error.errors():
                    response.set_error(key_path='.'.join(str(loc) for loc in err['loc']), message=err['msg'])
        return True

    @staticmethod
    def combine_parameters(parameters: List[Dict[str, Any]]) -> Dict[str, List[str]]:
        requirements: defaultdict[str, List[str]] = defaultdict(lambda: [])
        for param in parameters:
            if param.get('in') == 'query' and param.get('required'):
                requirements['required_query'].append(param['name'])
            elif param.get('in') == 'query':
                requirements['available_query'].append(param['name'])
            elif param.get('in') == 'header' and param.get('required'):
                requirements['required_headers'].append(param['name'])
            elif param.get('in') == 'header':
                requirements['available_headers'].append(param['name'])
        return dict(requirements)

    @staticmethod
    def format_schema_error_key(schema_error: Any) -> str:
        error_path: str = '.'.join(str(path) for path in schema_error.path)
        return error_path if error_path else 'root'

    @staticmethod
    def is_json_serializable(response: Response, request_body: Any) -> bool:
        if not isinstance(request_body, (dict, list, tuple)):
            response.set_error('body', 'Expecting JSON; make ensure proper content-type headers and encoded body')
            return False
        return True

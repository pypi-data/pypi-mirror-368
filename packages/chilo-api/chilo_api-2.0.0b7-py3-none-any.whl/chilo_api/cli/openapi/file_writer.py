import json
from typing import Any, Dict, List
import yaml


class OpenAPIFileWriter:
    '''
    A class to write OpenAPI documentation to files.
    This class provides methods to write OpenAPI documentation in JSON and YAML formats.
    Methods
    ----------
    write_openapi(doc, file_location, formats):
        Writes the OpenAPI documentation to files in the specified formats (JSON, YAML).
    '''

    def write_openapi(self, doc: Dict[str, Any], file_location: str, formats: List[str]) -> None:
        for write_format in formats:
            if write_format == 'json':
                self.__write_json(doc, file_location)
            if write_format == 'yml':
                self.__write_yml(doc, file_location)

    def __write_json(self, doc: Dict[str, Any], file_location: str) -> None:
        with open(f'{file_location}/openapi.json', 'w', encoding='utf-8') as openapi_json:
            openapi_json.write(json.dumps(doc, indent=4))

    def __write_yml(self, doc: Dict[str, Any], file_location: str) -> None:
        with open(f'{file_location}/openapi.yml', 'w', encoding='utf-8') as openapi_yml:
            yaml.dump(doc, openapi_yml, indent=4, default_flow_style=False, sort_keys=False)

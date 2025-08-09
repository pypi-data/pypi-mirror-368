import base64
import gzip
from io import BytesIO
from typing import Dict, Any, Union, Tuple, List, Optional

from chilo_api.core.rest.json_helper import JsonHelper
from chilo_api.core.interfaces.response import ResponseInterface


class RestResponse(ResponseInterface):
    '''
    A class to represent an API response

    Attributes
    ----------
    headers: dict
        The headers of the response (case sensitive)
    mimetype: str
        The mimetype (content type without charset etc.)
    cors: str, boolean
        determines if cors is enabled; can set `True` to open cors, or set a comma delimented string for only certain domains
    compress: boolean
        determines if response will be compressed (defaults is `False`)
    code: int (1xx - 5xx)
        status code to be returned to requester
    has_errors: bool
        determines if body contains error object
    body: str
        the return body of the response in json string
    raw: dict, list tuple
        the return body of the request in its original format
    server: any
        special return format for use by the server worker

    Methods
    ----------
    set_error(key_path, message):
        composes error using consistent format
    '''

    def __init__(self, **kwargs: Any) -> None:
        super().__init__()
        self.__wsgi = kwargs['wsgi']
        self.__environ = kwargs['environ']
        self.__server_response = kwargs['server_response']
        self.__cors: Optional[Union[bool, str]] = kwargs.get('cors')
        self.__compress: bool = False
        self.__mimetype: str = 'application/json'
        self.__headers: Dict[str, str] = {}

    @property
    def headers(self) -> Dict[str, str]:
        if isinstance(self.cors, bool) and self.cors:
            self.headers = ('Access-Control-Allow-Origin', '*')
        elif isinstance(self.cors, str) and 'Access-Control-Allow-Origin' not in self.__headers:
            self.headers = ('Access-Control-Allow-Origin', self.cors)
        return self.__headers

    @headers.setter
    def headers(self, header: Tuple[str, str]) -> None:
        key, value = header
        self.__headers[key] = value

    @property
    def mimetype(self) -> str:
        if 'Content-Type' in self.headers:
            self.__mimetype = self.headers['Content-Type'].split(';')[0]  # pylint: disable=invalid-sequence-index
        return self.__mimetype

    @mimetype.setter
    def mimetype(self, mimetype: str) -> None:
        self.__mimetype = mimetype

    @property
    def cors(self) -> Optional[Union[bool, str]]:
        return self.__cors

    @cors.setter
    def cors(self, access: Union[bool, str]) -> None:
        self.__cors = access

    @property
    def compress(self) -> bool:
        return self.__compress

    @compress.setter
    def compress(self, value: bool) -> None:
        self.__compress = value

    @property
    def code(self) -> int:
        if self._body is None and self._code == 200:
            self._code = 204
        elif isinstance(self._body, dict) and self._code == 200 and self.has_errors:
            self._code = 400
        return self._code

    @code.setter
    def code(self, code: int) -> None:
        self._code = code

    @property
    def has_errors(self) -> bool:
        return 'errors' in self._body if isinstance(self._body, dict) else False

    @property
    def body(self) -> Optional[Union[str, bytes]]:
        if self.compress:
            encoded_body = JsonHelper.encode(self._body, raise_error=True)
            return self.__compress_body(str(encoded_body))
        if isinstance(self._body, (dict, list, tuple)):
            return JsonHelper.encode(self._body, raise_error=True)
        return self._body

    @body.setter
    def body(self, body: Union[Dict[str, Any], List[Any], Tuple[Any, ...], str, None]) -> None:
        self._body = body

    @property
    def raw(self) -> Optional[Union[Dict[str, Any], List[Any], Tuple[Any, ...], str]]:
        return self._body

    def get_response(self) -> Any:
        response = self.__wsgi(self.body, headers=self.headers, mimetype=self.mimetype, status=self.code)
        return response(self.__environ, self.__server_response)

    def set_error(self, key_path: str, message: str) -> None:
        error: Dict[str, str] = {'key_path': key_path, 'message': message}
        if isinstance(self._body, dict) and 'errors' in self._body:
            self._body['errors'].append(error)
        else:
            self._body = {'errors': [error]}

    def __compress_body(self, body: str) -> str:
        self.headers = ('Content-Encoding', 'gzip')
        bytes_io = BytesIO()
        with gzip.GzipFile(fileobj=bytes_io, mode='w') as file:
            file.write(body.encode('utf-8'))
        return base64.b64encode(bytes_io.getvalue()).decode('ascii')

    def __str__(self) -> str:
        return str({
            'headers': self.headers,
            'mimetype': self.mimetype,
            'cors': self.cors,
            'compress': self.compress,
            'code': self.code,
            'body': self.raw
        })

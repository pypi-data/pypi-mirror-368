import base64
from typing import Any
import urllib.parse

import xmltodict

from chilo_api.core import logger
from chilo_api.core.rest.json_helper import JsonHelper
from chilo_api.core.interfaces.request import RequestInterface


class RestRequest(RequestInterface):
    '''
    A class to represent a api request

    Attributes
    ----------
    api_type: str
        The type of API, such as 'rest' or 'grpc'
    wsgi: Request
        An instance of the werkzeug Request (https://werkzeug.palletsprojects.com/en/3.0.x/wrappers/)
    authorization: dict
        The Authorization header parsed into a dictionary. None if the header is not present
    cookies: dict
        A dict with the contents of all cookies transmitted with the request.
    protocol: str
        The URL protocol the request used, such as https or wss.
    content_type: str
        The Content-Type entity-header field indicates the media type of the entity-body sent to the recipient.
    mimetype: str
        The mimetype (content type without charset etc.)
    host_url: str
        The request URL scheme and host only.
    domain: str
        The request domain only.
    method: str
        The http request method
    path: str
        The path of the request after the domain, inlcuding base_path and embedded path param values
    route: str
        The route of the request after the domain, not including base_path and using path param variables (not values)
    headers: dict
        The headers of the request, all lowercase
    body: any
        The body of the request, parsed automatically by the mimetype header
    json: dict, list
        The body of the request parsed as json; will raise error if json malformed
    form: dict, list
        The body of the request parsed as a form
    xml: dict, list
        The body of the request parsed as xml
    files: dict
        A dict containing all uploaded files. Each key in files is the name from the <input type="file" name="">. Each value is a Werkzeug FileStorage object.
    graphql: dict
        The body of the request parsed as graphql
    raw: Any
        The body of the request exactly as it was sent, no parsing
    query_params: dict, None
        The query string params sent as a dict
    path_params: dict, None
        The path params sent; keys are varables definied in your endpoint's required_path kwarg
    context: Any
        Optional context used by you to pass along data from middleware to the endpoint
    timeout: int
        The timeout of the request as set by the global definition within Chilo definition
    Methods
    ----------
    clear_path_params():
        Clears the path params so that they can be set again
    __str__():
        Returns a string representation of the request object, useful for debugging and logging
    '''
    DEFAULT_MIMETYPE = 'raw'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.__timeout = kwargs['timeout']
        self.__route = ''
        self.__path_params = {}
        self.__parsers = {
            'application/json': 'json',
            'application/graphql': 'graphql',
            'application/x-www-form-urlencoded': 'form',
            'multipart/form-data': 'raw',
            'application/xml': 'xml',
            'text/xml': 'xml',
            'raw': 'raw'
        }

    @property
    def api_type(self) -> str:
        return 'rest'

    @property
    def wsgi(self) -> Any:
        return self._wsgi

    @property
    def text(self) -> str:
        return self._wsgi.get_data(as_text=True)

    @property
    def authorization(self) -> Any:
        return self._wsgi.authorization

    @property
    def cookies(self) -> dict:
        return dict(self._wsgi.cookies)

    @property
    def protocol(self) -> str:
        return self._wsgi.scheme

    @property
    def content_type(self) -> str:
        return self._wsgi.content_type

    @property
    def mimetype(self) -> str:
        return self._wsgi.mimetype if self._wsgi.mimetype is not None else self.DEFAULT_MIMETYPE

    @property
    def host_url(self) -> str:
        return self._wsgi.host_url

    @property
    def domain(self) -> str:
        return urllib.parse.urlparse(self._wsgi.host_url).netloc

    @property
    def method(self) -> str:
        return self._wsgi.method.lower()

    @property
    def path(self) -> str:
        return self._wsgi.path

    @property
    def route(self) -> str:
        route = self.__route if self.__route else self.path
        if route and route[0] != '/':
            return f'/{route}'
        return route

    @route.setter
    def route(self, route: str):
        self.__route = route

    @property
    def headers(self) -> dict:
        return {key.lower(): value for key, value in dict(self._wsgi.headers).items()}

    @property
    def body(self) -> Any:
        try:
            parser = self.__parsers.get(self.mimetype, 'raw')
            return getattr(self, parser)
        except Exception as error:  # pragma: no cover
            logger.log(level='ERROR', log=error)
            return self.text

    @property
    def json(self) -> dict:
        return JsonHelper.decode(self.text)

    @property
    def form(self) -> dict:
        return dict(self._wsgi.form)

    @property
    def xml(self) -> dict:
        return xmltodict.parse(self.text)

    @property
    def files(self) -> dict:
        return dict(self._wsgi.files)

    @property
    def graphql(self) -> dict:
        try:
            graphql_body = base64.b64decode(self.text).decode('utf-8')
        except Exception as error:  # pragma: no cover
            logger.log(level='ERROR', log=error)
            graphql_body = self.text
        return JsonHelper.decode(graphql_body)

    @property
    def raw(self) -> Any:
        return self._wsgi.get_data()

    @property
    def query_params(self) -> dict:
        return dict(self._wsgi.args)

    @property
    def path_params(self) -> dict:
        return self.__path_params

    @path_params.setter
    def path_params(self, path_params: tuple):
        key, value = path_params
        self.__path_params[key] = value

    @property
    def context(self) -> Any:
        return self._context

    @context.setter
    def context(self, context: Any):
        self._context = context

    @property
    def timeout(self) -> int:
        return self.__timeout

    def clear_path_params(self):
        self.__path_params = {}

    def __str__(self) -> str:
        return str({
            'method': self.method,
            'headers': self.headers,
            'query': self.query_params,
            'path': self.path_params,
            'body': self.body,
            'context': self.context
        })

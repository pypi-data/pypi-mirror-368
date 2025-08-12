from typing import Any, Dict
from types import ModuleType

from chilo_api.core.resolver.cache import ResolverCache
from chilo_api.core.rest.endpoint import Endpoint
from chilo_api.core.exception import ApiException
from chilo_api.core.resolver.scanner import ResolverScanner
from chilo_api.core.rest.request import RestRequest
from chilo_api.core.grpc.request import GRPCRequest


class Resolver:
    '''
    A class to resolve API endpoints based on the request path.
    This class is responsible for scanning the file system for handler files, determining the correct import paths,
    and resolving the endpoints based on the request path.
    Attributes
    ----------
    cacher: ResolverCache
        An instance of ResolverCache to handle caching of resolved endpoints.
    scanner: ResolverScanner
        An instance of ResolverScanner to handle scanning and resolving endpoints.
    cache_misses: int
        The number of times an endpoint was not found in the cache and had to be resolved from the file system.
    Methods
    ----------
    auto_load():
        Automatically loads the handler files into the resolver.
    reset():
        Resets the state of the resolver, clearing dynamic parts and import paths.
    get_endpoint(request: Request) -> Endpoint:
        Retrieves the endpoint for the given request path, either from the cache or by scanning the file system.
    '''
    __cache_misses: int = 0

    def __init__(self, **kwargs: Any) -> None:
        self.__cacher: ResolverCache = ResolverCache(**kwargs)
        self.__scanner: ResolverScanner = ResolverScanner(**kwargs)

    @property
    def cache_misses(self) -> int:
        return self.__cache_misses

    def auto_load(self) -> None:
        self.__scanner.load_importer_files()

    def reset(self) -> None:
        self.__scanner.reset()

    def get_endpoint(self, request: Any) -> Endpoint:
        endpoint_module: ModuleType = self.__get_endpoint_module(request)
        if not hasattr(endpoint_module, request.method) and request.method not in {'options', 'head'}:
            raise ApiException(code=403, message='method not allowed')
        endpoint: Endpoint = Endpoint(endpoint_module, request.method)
        self.__assign_normalized_route(request, endpoint)
        self.__check_dynamic_route_and_apply_params(request, endpoint)
        self.__cacher.put(request.path, endpoint_module, self.__scanner.has_dynamic_route, self.__scanner.dynamic_parts)
        self.reset()
        return endpoint

    def __get_endpoint_module(self, request: Any) -> ModuleType:
        cached: Dict[str, Any] = self.__cacher.get(request.path)
        endpoint = cached.get('endpoint')
        self.__scanner.has_dynamic_route = cached.get('is_dynamic_route', self.__scanner.has_dynamic_route)
        self.__scanner.dynamic_parts = cached.get('dynamic_parts', self.__scanner.dynamic_parts)
        if endpoint is None:
            self.__cache_misses += 1
            endpoint = self.__scanner.get_endpoint_module(request)
        if not isinstance(endpoint, ModuleType):
            raise ApiException(code=500, message='Endpoint module is not a valid python module')  # pragma: no cover
        return endpoint

    def __assign_normalized_route(self, request: Any, endpoint: Endpoint) -> None:
        base_path_parts: list[str] = self.__scanner.base_path.split('/')
        dirty_route_parts: list[str] = endpoint.required_route.split('/') if endpoint.has_required_route else request.path.split('/')
        route_parts: list[str] = [part for part in dirty_route_parts if part]
        combined_route: list[str] = base_path_parts + route_parts
        final_route: list[str] = list(dict.fromkeys(combined_route))
        request.route = '/'.join(final_route)

    def __check_dynamic_route_and_apply_params(self, request: Any, endpoint: Endpoint) -> None:
        if not self.__scanner.has_dynamic_route:
            return
        if not endpoint.has_required_route:
            self.__raise_404_error(request.path, 'no route found; endpoint does have required_route configured')
        clean_request_path: list[str] = [rp for rp in request.path.split('/') if rp and rp not in self.__scanner.base_path.split('/')]
        clean_endpoint_route: list[str] = [er for er in endpoint.required_route.split('/') if er and er not in self.__scanner.base_path.split('/')]
        self.__check_dynamic_route(request, clean_request_path, clean_endpoint_route)
        self.__apply_dynamic_route_params(request, clean_endpoint_route)

    def __check_dynamic_route(self, request: Any, clean_request_path: list[str], clean_endpoint_route: list[str]) -> None:
        for index, _ in enumerate(clean_request_path):
            if clean_request_path[index] != clean_endpoint_route[index] and index not in list(self.__scanner.dynamic_parts.keys()):
                self.__raise_404_error(request.path, 'no route found; requested dynamic route does not match endpoint route definition')

    def __apply_dynamic_route_params(self, request: Any, required_route_parts: list[str]) -> None:
        for part in self.__scanner.dynamic_parts.keys():
            variable_name: str = required_route_parts[part]
            if not variable_name.startswith('{') or not variable_name.endswith('}'):
                self.__raise_404_error(request.path, 'no route found; endpoint does not have proper variables in required_route')
            dynamic_name: str = variable_name.strip('{').strip('}')
            request.path_params = dynamic_name, self.__scanner.dynamic_parts[part]

    def __raise_404_error(self, request_path: str, message: str) -> None:
        raise ApiException(code=404, key_path=request_path, message=message)

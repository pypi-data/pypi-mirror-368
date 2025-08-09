from collections import OrderedDict
from typing import Any, Dict, Optional


class ResolverCache:
    '''
    A class to handle caching of routes and endpoints in the resolver.
    This class provides methods to get and put cached items, with a size limit and mode of operation.
    Attributes
    ----------
    cache: OrderedDict[str, Dict[str, Any]]
        An ordered dictionary to store cached items, where keys are method paths and values are dictionaries containing
        the endpoint, whether it is a dynamic route, and any dynamic parts.
    size: Optional[int]
        The maximum size of the cache. If None, the cache has no size limit. If 0, the cache is disabled.
    mode: str
        The mode of the cache, which can be 'all', 'static-only', or 'dynamic-only'.
        - 'all': Cache all routes.
        - 'static-only': Cache only static routes.
        - 'dynamic-only': Cache only dynamic routes.
    Methods
    ----------
    get(method_path: str) -> Dict[str, Any]:
        Retrieves the cached item for the given method path. If not found, returns an empty dictionary.
    put(route_path: str, endpoint: Any, is_dynamic_route: bool = False, dynamic_parts: Optional[Dict[int, str]] = None) -> None:
        Caches the given route path and endpoint. If the cache size limit is reached, the oldest item is removed.
    '''
    CACHE_ALL: str = 'all'
    CACHE_STATIC: str = 'static-only'
    CACHE_DYNAMIC: str = 'dynamic-only'

    def __init__(self, **kwargs: Any) -> None:
        self.__cache: OrderedDict[str, Dict[str, Any]] = OrderedDict()
        self.__size: Optional[int] = kwargs.get('cache_size', 128)
        self.__mode: str = kwargs.get('cache_mode', self.CACHE_ALL)

    def get(self, method_path: str) -> Dict[str, Any]:
        if method_path not in self.__cache:
            return {}
        self.__cache.move_to_end(method_path)
        return self.__cache[method_path]

    def put(self, route_path: str, endpoint: Any, is_dynamic_route: bool = False, dynamic_parts: Optional[Dict[int, str]] = None) -> None:
        if self.__size is None:
            return
        if is_dynamic_route and self.__mode == self.CACHE_STATIC:
            return
        if not is_dynamic_route and self.__mode == self.CACHE_DYNAMIC:
            return
        self.__cache[route_path] = {'endpoint': endpoint, 'is_dynamic_route': is_dynamic_route, 'dynamic_parts': dynamic_parts}
        self.__cache.move_to_end(route_path)
        if self.__size != 0 and len(self.__cache) > self.__size:
            self.__cache.popitem(last=False)

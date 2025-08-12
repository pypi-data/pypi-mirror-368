from functools import wraps
from typing import Any, Callable, Optional
from typing_extensions import Unpack, List, Union, Dict

from chilo_api.core import logger
from chilo_api.core.types.logger_settings import LoggerSettings


def log(**settings: Unpack[LoggerSettings]) -> Callable[..., Any]:
    '''
    A decorator to make logging simplier and DRY'er; will capture all args, kwargs and ouput of decorated function/method

    level: str, enum(DEBUG, INFO, WARN, ERROR)
        The log level to log (default is INFO)
    condition: callable, optional
        A callable function which will determine if log should happen; callable must return truth-y/false-y value
    '''
    def decorator_func(func: Callable[..., Any]) -> Callable[..., Any]:
        captured: Dict[str, Union[Dict[str, Union[List[Any], Dict[str, Any]]], Any]] = {'arguments': {}, 'result': None}

        @wraps(func)
        def run_func(*args: Any, **kwargs: Any) -> Any:
            captured['arguments']['args'] = list(args)
            captured['arguments']['kwargs'] = kwargs
            captured['result'] = func(*args, **kwargs)

            condition: Optional[Callable[..., Any]] = settings.get('condition')
            if condition and callable(condition):
                if condition(*args, **kwargs):
                    logger.log(level=settings.get('level', 'INFO'), log=captured)
            else:
                logger.log(level=settings.get('level', 'INFO'), log=captured)
            return captured['result']

        return run_func  # type: ignore

    return decorator_func

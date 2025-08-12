import traceback
from typing import Any, Dict

from icecream import ic


class CommonLogger:

    def __init__(self, **kwargs: Any) -> None:
        self.__log_level: str = kwargs.get('level', 'INFO')
        self.log_levels: Dict[str, int] = {'DEBUG': 1, 'INFO': 2, 'WARN': 3, 'ERROR': 4, 'CRITICAL': 5, 'NOTSET': 99}
        self.__validate_configs()

    def log(self, *args: Any, **kwargs: Any) -> None:
        log: Dict[str, Any] = {'level': kwargs.get('level', 'INFO'), 'log': kwargs.get('log', args)}
        if self.__should_log(log['level']):
            self.__log(**log)

    def __validate_configs(self) -> None:
        if self.__log_level not in self.log_levels.keys():
            raise RuntimeError(f'level argument must be {",".join(self.log_levels.keys())}; recieved: {self.__log_level}')

    def __should_log(self, level: str) -> bool:
        current_log_level: int = self.log_levels[level]
        log_level_setting: int = self.log_levels[self.__log_level]
        return current_log_level >= log_level_setting

    def __get_traceback(self) -> str:
        trace: str = traceback.format_exc()
        if str(trace) != 'NoneType: None\n':
            return trace
        return ''

    def __log(self, **kwargs: Any) -> None:
        trace: str = self.__get_traceback()
        prefix: str = f"{trace}\n{kwargs['level']} | "
        log: Any = kwargs['log']
        ic.configureOutput(prefix=prefix)
        ic(log)

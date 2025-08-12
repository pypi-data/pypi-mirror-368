from typing import Any

from chilo_api.core.logger.common import CommonLogger


def log(**kwargs: Any) -> None:
    '''
    Log function to log your desired input/ouput

    Parameters
    ----------
    level: str, enum(DEBUG, INFO, WARN, ERROR)
        The log level to log (default is INFO)
    log: any
        The thing to log
    '''
    try:
        logger: CommonLogger = CommonLogger(**kwargs)
        logger.log(**kwargs)
    except Exception as exception:
        raise RuntimeError(exception) from exception

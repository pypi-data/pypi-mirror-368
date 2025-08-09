import unittest

from chilo_api import log, logger


def some_log_condition(*args, **_):
    if args[0] == 1:
        return True
    return False


@log()
def mock_func_simple(arg1, arg2, **kwargs):
    return {'args': [arg1, arg2], 'kwargs': kwargs}


@log(level='INFO')
def mock_func_level(arg1, arg2, **kwargs):
    return {'args': [arg1, arg2], 'kwargs': kwargs}


@log(level='INFO', condition=some_log_condition)
def mock_func_condition(arg1, arg2, **kwargs):
    return {'args': [arg1, arg2], 'kwargs': kwargs}


class LoggerTest(unittest.TestCase):

    def test_logger_logs_simple_local_json(self):
        logger.log(LOG_FORMAT='JSON', level='ERROR', log={'error': 'test-simple'})

    def test_logger_logs_simple_local_inline(self):
        logger.log(LOG_FORMAT='INLINE', level='INFO', log={'error': 'test-simple'})

    def test_logger_logs_simple_non_local(self):
        logger.log(level='ERROR', log={'error': 'test-simple'})

    def test_logger_logs_simple_local(self):
        logger.log(level='ERROR', log={'error': 'test-simple-local'})

    def test_logger_logs_error_json(self):
        try:
            raise RuntimeError('error-object')
        except RuntimeError as error:
            logger.log(LOG_FORMAT='JSON', level='ERROR', log=error)

    def test_logger_logs_error_inline(self):
        try:
            raise RuntimeError('error-object')
        except RuntimeError as error:
            logger.log(level='ERROR', log=error)

    def test_logger_logs_error_as_object(self):
        try:
            raise RuntimeError('error-string') # type: ignore
        except RuntimeError as error:
            logger.log(level='ERROR', log={'error': error, 'request': 'request'})

    def test_logger_logs_ignore_info(self):
        logger.log(level='INFO', log={'INFO': 'ignore'})

    def test_logger_logs_see_info(self):
        logger.log(level='INFO', log={'INFO': 'see'})

    def test_log_decorator(self):
        result = mock_func_simple(1, 2, test=True)
        self.assertDictEqual({'args': [1, 2], 'kwargs': {'test': True}}, result)

    def test_log_decorator_with_level(self):
        result = mock_func_level(1, 2, test=True)
        self.assertDictEqual({'args': [1, 2], 'kwargs': {'test': True}}, result)

    def test_log_decorator_with_condition_logs(self):
        result = mock_func_condition(1, 2, test=True)
        self.assertDictEqual({'args': [1, 2], 'kwargs': {'test': True}}, result)

    def test_log_decorator_with_condition_does_not_log(self):
        result = mock_func_condition(3, 2, test=True)
        self.assertDictEqual({'args': [3, 2], 'kwargs': {'test': True}}, result)

    def test_logger_LOG_LEVEL(self):
        try:
            logger.log(level='BAD', log={'error': 'test-simple'})
        except Exception as error:
            self.assertIn('level argument must be', str(error))

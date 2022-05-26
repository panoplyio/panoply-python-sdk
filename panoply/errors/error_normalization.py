from enum import Enum
from functools import wraps

import panoply.datasource
from .exceptions import DataSourceException

ERROR_CODES_REGISTRY = {
    400: 'Bad request',
    401: 'Unauthorized',
    403: 'Permissions error',
    404: 'Resource is not found',
    408: 'Timeout',
    422: 'Parsing error',
    429: 'Rate limit',
    500: 'Internal exception',
    501: 'Unclassified error',
    506: 'SDK error in processing an error'
}

EXCEPTIONS_REGISTRY = {}


class Phase(Enum):
    COLLECT = 'collect'
    CONFIG = 'config'


def set_internal_code(code: int) -> callable:
    """ A decorator is used on exception classes to register mapping
        of error and internal code from ERROR_CODES_REGISTRY.
        Parameters
        ----------
        code : int
           Error code from ERROR_CODES_REGISTRY.
    """
    def decorator(exception_cls: type) -> type:
        if not issubclass(exception_cls, BaseException):
            raise RuntimeError('Unable to set error code for non-Exception class')

        EXCEPTIONS_REGISTRY[exception_cls] = code

        return exception_cls

    return decorator


def wrap_errors(phase: Phase) -> callable:
    """ A decorator is used to normalize raised exceptions.
       Parameters
       ----------
       phase : Phase
           Equals to CONFIG / COLLECT.
    """
    def _wrap_errors(func: callable) -> callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> list:
            try:
                return func(*args, **kwargs)
            except DataSourceException as e:
                # In case of nested error wrapper we should keep the original
                # error but with the phase value of the last error wrapper
                e.phase = phase.value
                raise e
            except Exception as e:
                # source object can be:
                # 1. a first param in dynamic params methods (e.g. definition(source, options))
                # 2. an attribute of the DataSource class (e.g. definition(self, params) -> source = self.source)
                source_config = args[0]
                if isinstance(source_config, panoply.datasource.DataSource):
                    source_config = getattr(source_config, 'source', None)

                code = EXCEPTIONS_REGISTRY.get(type(e))

                if code is None:
                    code = 501

                if code not in ERROR_CODES_REGISTRY:
                    code = 506

                details = {
                    'message': str(e),
                    'code': code,
                    'exception_cls': f'{e.__class__.__module__}.{e.__class__.__name__}',
                    'phase': phase.value,
                    'source_type': source_config['type'],
                    'source_id': source_config['id'],
                    'database_id': source_config['database']
                }

                normalized = DataSourceException(**details)

                raise normalized
        return wrapper
    return _wrap_errors

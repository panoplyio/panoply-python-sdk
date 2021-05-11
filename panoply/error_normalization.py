from panoply import DataSource, PanoplyException
from datetime import datetime


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


class NormalizedException(PanoplyException):
    def __init__(self, message, code, exception_cls,
                 phase, source_type, source_id, database_id,
                 retryable=True):
        super().__init__(message, retryable)
        self.message = message
        self.code = code
        self.phase = phase
        self.source_type = source_type
        self.source_id = source_id
        self.database_id = database_id
        self.exception_cls = exception_cls
        self.created_at = datetime.utcnow()


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


def handle_errors(phase: str) -> callable:
    """ A decorator is used to normalize raised exceptions.
       Parameters
       ----------
       phase : str
           Equals to config / collect.
    """
    def _handle_errors(func: callable) -> callable:
        def wrapper(*args, **kwargs) -> list:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                # source object can be:
                # 1. a first param in dynamic params methods (e.g. definition(source, options))
                # 2. an attribute of the DataSource class (e.g. definition(self, params) -> source = self.source)
                source_config = args[0]
                if isinstance(source_config, DataSource):
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
                    'phase': phase,
                    'source_type': source_config['type'],
                    'source_id': source_config['id'],
                    'database_id': source_config['database'],
                    'retryable': getattr(e, 'retryable', True)
                }

                print(details)
                normalized = NormalizedException(**details)

                raise normalized
        return wrapper
    return _handle_errors

from datetime import datetime


class PanoplyException(Exception):
    def __init__(self, args=None, retryable=True):
        super(PanoplyException, self).__init__(args)
        self.retryable = retryable


class IncorrectParamError(Exception):
    def __init__(self, msg: str = "Incorrect input parametr"):
        super().__init__(msg)


class DataSourceException(Exception):
    def __init__(self, message, code, exception_cls,
                 phase, source_type, source_id, database_id):
        super().__init__(message)
        self.message = message
        self.code = code
        self.phase = phase
        self.source_type = source_type
        self.source_id = source_id
        self.database_id = database_id
        self.exception_cls = exception_cls
        self.created_at = datetime.utcnow()


class TokenValidationException(PanoplyException):
    def __init__(self, original_error, args=None, retryable=True):
        super().__init__(args, retryable)
        self.original_error = original_error


class WrongTypeOrValueError(Exception):
    def __init__(self, message: str):
        super().__init__(message)

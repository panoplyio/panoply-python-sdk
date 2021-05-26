from datetime import datetime


class PanoplyException(Exception):
    def __init__(self, args=None, retryable=True):
        super(PanoplyException, self).__init__(args)
        self.retryable = retryable


class IncorrectParamError(Exception):
    def __init__(self, msg: str = "Incorrect input parametr"):
        super().__init__(msg)


class DataSourceException(PanoplyException):
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

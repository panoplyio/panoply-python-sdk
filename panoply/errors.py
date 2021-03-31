class PanoplyException(Exception):
    def __init__(self, args=None, retryable=True):
        super(PanoplyException, self).__init__(args)
        self.retryable = retryable


class IncorrectParamError(Exception):
    def __init__(self, msg: str = "Incorrect input parametr"):
        super().__init__(msg)

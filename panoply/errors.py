class PanoplyException(Exception):
    def __init__(self, args=None, retryable=True):
        super(PanoplyException, self).__init__(args)
        self.retryable = retryable

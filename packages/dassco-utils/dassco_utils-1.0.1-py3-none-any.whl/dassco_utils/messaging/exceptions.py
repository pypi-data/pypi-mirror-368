class TransientError(Exception):
    """
    Exception raised when a temporary error occurs. The message will be requeued.
    The default number of retries is 3.
    """
    def __init__(self, max_retries = 3):
        super().__init__()
        self.max_retries = max_retries

class FatalError(Exception):
    """
    Exception raised when a fatal error occurs. The message will be dropped.
    """
    pass
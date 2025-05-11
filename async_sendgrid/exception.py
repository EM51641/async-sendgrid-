class SessionClosedException(Exception):
    """
    Exception raised when the session is closed unexpectedly.
    """

    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)

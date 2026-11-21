class AppError(Exception):
    """Base class for all errors we raise on purpose."""

    user_message = "Error happened in server side."

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message

class AppError(Exception):
    """Base class for all errors we raise on purpose."""

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


class InvalidAreaError(AppError):
    pass


class NotFoundError(AppError):
    pass

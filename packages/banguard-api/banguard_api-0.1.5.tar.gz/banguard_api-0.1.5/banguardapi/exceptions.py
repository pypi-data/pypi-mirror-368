class APIError(Exception):
    """Base class for API-related errors."""

    def __init__(self, message="An API error occurred."):
        self.message = message
        super().__init__(self.message)

class AuthenticationError(APIError):
    def __init__(self, message="Authentication failed."):
        super().__init__(message)

class PermissionDeniedError(APIError):
    def __init__(self, message="Insufficient permissions."):
        super().__init__(message)

class NotFoundError(APIError):
    def __init__(self, message="Resource not found."):
        super().__init__(message)

class BanNotFoundError(NotFoundError):
    def __init__(self, message="Ban not found."):
        super().__init__(message)

class PlayerNotFoundError(NotFoundError):
    def __init__(self, message="Player not found."):
        super().__init__(message)

class ServerNotFoundError(NotFoundError):
    def __init__(self, message="Server not found."):
        super().__init__(message)

class BadRequestError(APIError):
    def __init__(self, message="Bad request sent to the API."):
        super().__init__(message)

class ServerError(APIError):
    def __init__(self, message="An error occurred on the server."):
        super().__init__(message)

class RateLimitError(APIError):
    def __init__(self, message="Rate limit exceeded."):
        super().__init__(message)

class InvalidResponseError(APIError):
    def __init__(self, message="Invalid or malformed response from server."):
        super().__init__(message)

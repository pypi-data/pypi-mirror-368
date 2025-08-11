"""HTTP status codes."""

from bear_utils.constants._meta import IntValue as Value, RichIntEnum


class HTTPStatusCode(RichIntEnum):
    """An enumeration of common HTTP status codes."""

    SERVER_ERROR = Value(500, "Internal Server Error")
    SERVER_OK = Value(200, "OK")
    PAGE_NOT_FOUND = Value(404, "Not Found")
    BAD_REQUEST = Value(400, "Bad Request")
    UNPROCESSABLE_CONTENT = Value(422, "Unprocessable Content")
    UNAUTHORIZED = Value(401, "Unauthorized")
    FORBIDDEN = Value(403, "Forbidden")
    CONFLICT = Value(409, "Conflict")
    METHOD_NOT_ALLOWED = Value(405, "Method Not Allowed")


SERVER_ERROR = HTTPStatusCode.SERVER_ERROR
"""Internal Server Error"""
SERVER_OK = HTTPStatusCode.SERVER_OK
"""OK"""
PAGE_NOT_FOUND = HTTPStatusCode.PAGE_NOT_FOUND
"""Not Found"""
BAD_REQUEST = HTTPStatusCode.BAD_REQUEST
"""Bad Request"""
UNPROCESSABLE_CONTENT = HTTPStatusCode.UNPROCESSABLE_CONTENT
"""Unprocessable Content"""
UNAUTHORIZED = HTTPStatusCode.UNAUTHORIZED
"""Unauthorized"""
FORBIDDEN = HTTPStatusCode.FORBIDDEN
"""Forbidden"""
CONFLICT = HTTPStatusCode.CONFLICT
"""Conflict"""
METHOD_NOT_ALLOWED = HTTPStatusCode.METHOD_NOT_ALLOWED
"""Method Not Allowed"""

import enum


class ErrorCode(enum.IntEnum):
    # General error codes (1001-1999)
    GENERAL_1001_UNEXPECTED_ERROR = 1001
    GENERAL_1002_REQUEST_VALIDATION_FAILED = 1002
    GENERAL_1003_RESOURCE_NOT_FOUND = 1003

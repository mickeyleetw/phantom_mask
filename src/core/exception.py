from starlette import status

from core.error_code import ErrorCode
from core.fastapi import FastAPIError


class BaseException_(FastAPIError):

    def __init__(
        self,
        code=ErrorCode.GENERAL_1001_UNEXPECTED_ERROR,
        http_status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        message='unexpected error'
    ):
        self.code = code
        self.http_status = http_status
        self.message = message
        super().__init__(self.message)

    def __repr__(self):
        return f'BaseException:CODE={self.code},MESSAGE={self.message}'


class ResourceNotFoundException(BaseException_):

    def __init__(self, subject: str):
        super().__init__(
            code=ErrorCode.GENERAL_1003_RESOURCE_NOT_FOUND,
            http_status=status.HTTP_404_NOT_FOUND,
            message=f'{subject} not found'
        )
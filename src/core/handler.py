from typing import Union

from fastapi import FastAPI, Request
from fastapi.exceptions import HTTPException as FastAPIHTTPException
from fastapi.exceptions import RequestValidationError
from starlette import status
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.responses import JSONResponse

from core.error_code import ErrorCode
from core.exception import BaseException_


def add_exception_handlers(app: FastAPI) -> None:

    @app.exception_handler(BaseException_)
    async def base_exception_handler(_: Request, exception: BaseException_):
        return JSONResponse(
            status_code=exception.http_status,
            content={
                'message': exception.message,
                'code': exception.code
            },
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(_: Request, exception: RequestValidationError):
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                'message': str(exception),
                'code': ErrorCode.GENERAL_1002_REQUEST_VALIDATION_FAILED
            }
        )

    @app.exception_handler(FastAPIHTTPException)
    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(_: Request, exception: Union[FastAPIHTTPException, StarletteHTTPException]):
        return JSONResponse(
            status_code=exception.status_code,
            content={
                'message': exception.detail,
                'code': ErrorCode.GENERAL_1004_HTTP_SERVICE_ERROR
            }
        )

    @app.exception_handler(NotImplementedError)
    async def not_implemented_exception_handler(_: Request, exception: NotImplementedError):
        return JSONResponse(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            content={
                'message': 'not implemented',
                'code': ErrorCode.GENERAL_1011_NOT_IMPLEMENTED
            }
        )

    @app.exception_handler(Exception)
    async def default_exception_handler(_: Request, exception: Exception):
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                'message': 'internal error',
                'code': ErrorCode.GENERAL_1001_UNEXPECTED_ERROR
            }
        )

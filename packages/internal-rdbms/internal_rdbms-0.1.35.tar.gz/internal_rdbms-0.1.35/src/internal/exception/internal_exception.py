from fastapi import status
from .base_exception import InternalBaseException


class BadGatewayException(InternalBaseException):
    code = "error_bad_gateway"
    message = "請求失敗"

    def __init__(self, message: str = None, **kwargs):
        _message = message or self.message
        super().__init__(status.HTTP_502_BAD_GATEWAY, self.code, _message, **kwargs)


class GatewayTimeoutException(InternalBaseException):
    code = "error_gateway_timeout"
    message = "請求逾時"

    def __init__(self, message: str = None, **kwargs):
        _message = message or self.message
        super().__init__(status.HTTP_504_GATEWAY_TIMEOUT, self.code, _message, **kwargs)


class DatabaseInitializeFailureException(InternalBaseException):
    code = "error_database_initialize"
    message = "資料庫初始化失敗"

    def __init__(self, message: str = None, **kwargs):
        _message = message or self.message
        super().__init__(status.HTTP_500_INTERNAL_SERVER_ERROR, self.code, _message, **kwargs)


class DatabaseConnectFailureException(InternalBaseException):
    code = "error_database_connect"
    message = "資料庫連線失敗"

    def __init__(self, message: str = None, **kwargs):
        _message = message or self.message
        super().__init__(status.HTTP_500_INTERNAL_SERVER_ERROR, self.code, _message, **kwargs)


class NoChangeException(InternalBaseException):
    code = "error_no_change"
    message = "資料未異動"

    def __init__(self, message: str = None, **kwargs):
        _message = message or self.message
        super().__init__(status.HTTP_200_OK, self.code, _message, **kwargs)


class CustomerValidationException(InternalBaseException):
    code = "error_validation"
    message = "無效參數或格式不符"

    def __init__(self, message: str = None, **kwargs):
        _message = message or self.message
        super().__init__(status.HTTP_422_UNPROCESSABLE_ENTITY, self.code, _message, **kwargs)

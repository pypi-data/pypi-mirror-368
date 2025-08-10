from fastapi import HTTPException


class InternalBaseException(HTTPException):
    def __init__(self, status_code: int = None, code: str = "ok", message: str = "success", **kwargs):
        detail = {
            "code": code,
            "message": message,
            "data": kwargs,
        }
        super().__init__(status_code=status_code, detail=detail)

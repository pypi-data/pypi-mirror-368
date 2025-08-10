from typing import Optional, Union

from pydantic import BaseModel


class PaginationResponse(BaseModel):
    page_data: Optional[list] = None
    page_no: int
    page_size: int
    total_num: int


class BaseResponse(BaseModel):
    code: int
    message: Optional[str] = None
    data: Optional[Union[dict, list]] = None

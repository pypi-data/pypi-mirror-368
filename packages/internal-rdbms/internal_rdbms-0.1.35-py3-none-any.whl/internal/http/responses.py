import json
import httpx

from fastapi import status
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

from ..model.base_model import InternalBaseModel


async def async_response(data=None, message=None, code=None, page_no=None, total_num=None, page_size=None,
                         status_code=status.HTTP_200_OK):
    def _serialize(data):
        if isinstance(data, InternalBaseModel):
            data = json.loads(json.dumps(jsonable_encoder(data.to_dict()), ensure_ascii=False))
        return data

    if isinstance(data, httpx.Response):
        return JSONResponse(status_code=data.status_code, content=data.json())

    ret = {}
    if isinstance(data, list):
        data = [_serialize(d) for d in data]
    else:
        data = _serialize(data)

    data = jsonable_encoder(data)

    ret['code'] = code or "ok"

    ret['message'] = message or "success"

    if page_no and total_num and page_size:
        ret['data'] = {
            'page_no': page_no,
            'page_size': page_size,
            'total_num': total_num,
            'page_data': data
        }
    else:
        ret['data'] = data

    return JSONResponse(status_code=status_code, content=ret)

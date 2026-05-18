from typing import Any

from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

def success_response(message: str = "success", data: Any |  None = None):
   content = {
       "code": 200,
       "message": message,
       "data": data
   }
   return JSONResponse(content=jsonable_encoder(content))
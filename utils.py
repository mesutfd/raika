from starlette.responses import JSONResponse
from typing_extensions import List, Dict, Optional, TypedDict, Union


# I personally always create this function to make rest standard outputs
def api_response(
        result: Union[List[Dict], Dict, None],
        message: str = "Operation successful",
        success: bool = True) -> JSONResponse:
    if result is None:
        return JSONResponse({
            "success": False,
            "message": "Item not found",
            "status_code": 404,
            "data": None,
        })

    return JSONResponse({
        "success": success,
        "message": message,
        "status_code": 200,
        "data": result,
    })

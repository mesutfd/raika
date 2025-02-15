# I have used my older code snippets(DRY), and IDE Code completion
# I have never written a unit or integration test before, so I have skipped that part, wish to learn it
# File is abnormally long, so naming conventions may be a little bit nonsense
# Databases, Brokers and other external services are all on LOCALHOST, I dont really know how you gonna use the service
# If you had any questions, feel free to contact me by email or phone call

import datetime
import jwt
from fastapi import Depends, FastAPI, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from starlette.responses import JSONResponse
from typing_extensions import List, Dict, Optional, TypedDict, Union
from utils import api_response

# routers import
from app.jwt_auth import router as jwt_router
from app.alchemist import router as alchemist_router
from app.mongo_profiles import router as mongo_profiles_router
from app.background_tasks import router as background_tasks_router
from app.concurrency_management import router as concurrency_management_router
from app.celery_tasks import router as celery_tasks_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# include routers
app.include_router(jwt_router, prefix="/auth")
app.include_router(alchemist_router, prefix="/alchemist")
app.include_router(mongo_profiles_router, prefix="/mongo-profiles")
app.include_router(background_tasks_router, prefix="/background-tasks")
app.include_router(celery_tasks_router, prefix="/celery-tasks")
app.include_router(concurrency_management_router, prefix="/concurrency-management")



# def custom_openapi():
#     if app.openapi_schema:
#         return app.openapi_schema
#     openapi_schema = get_openapi(
#         title="FastAPI application",
#         version="1.0.0",
#         description="JWT Authentication and Authorization",
#         routes=app.routes,
#     )
#     openapi_schema["components"]["securitySchemes"] = {
#         "BearerAuth": {
#             "type": "http",
#             "scheme": "bearer",
#             "bearerFormat": "JWT"
#         }
#     }
#     openapi_schema["security"] = [{"BearerAuth": []}]
#     app.openapi_schema = openapi_schema
#     return app.openapi_schema
#
#
# app.openapi = custom_openapi


# PART 1

# to make code more readable, I have made this Item object
class Item(TypedDict):
    id: int
    name: str
    description: Optional[str]


items: List[Item] = []


# I personally always create this function to make rest standard outputs


# get list of items (pagination is skipped...)
@app.get("/items", tags=["Part 1"])
async def get_items_list():
    return api_response(result=items)


@app.get("/items/{id}", tags=["Part 1"])
async def get_item_details(id: int):
    item = next((item for item in items if item["id"] == id), None)
    return api_response(result=item)


@app.post("/items", tags=["Part 1"])
async def create_item(name: str, description: Optional[str] = Form("")):
    new_item = Item(
        id=(items[-1]["id"] + 1) if len(items) > 0 else 1,  # creating guid is skipped, created incremental id instead
        name=name,
        description=description
    )
    items.append(new_item)
    return api_response(result=new_item)


# PART 2


# PART 3

# PART 4

# PART 5

# PART 6

# PART 7

import os

from motor.motor_asyncio import AsyncIOMotorClient as MongoClient
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv

from utils import api_response

load_dotenv()

RUNNING_IN_DOCKER = os.path.exists('/.dockerenv')

MONGO_DB_URI = os.getenv("MONGO_DB_URI") if os.getenv("MONGO_DB_URI") else ("mongodb://mongodb:27017/" if RUNNING_IN_DOCKER else "mongodb://localhost:27017/")
router = APIRouter()

# at this point, naming conventions are a little bit different
mongo_client = MongoClient(MONGO_DB_URI)
mongo_db = mongo_client.Raika
raika_col = mongo_db.users
users_col = mongo_db["users"]


class ProfileDto(BaseModel):
    username: str
    full_name: str
    age: int


@router.post("/profiles", tags=["Part 4"])
async def create_profile(profile: ProfileDto):
    res = await raika_col.insert_one(profile.model_dump())
    return api_response({"_id": str(res.inserted_id), "username": profile.username, "full_name": profile.full_name})


@router.get("/profiles/{username}", tags=["Part 4"])
async def get_profile_details_mongo(username: str):
    res = await users_col.find_one({"username": username})
    if not res:
        raise HTTPException(status_code=404, detail="User not found")
    res["_id"] = str(res['_id'])
    return api_response(res)


@router.get("/profiles", tags=["Part 4"])
async def get_profiles_list_mongo():
    res = users_col.find({})
    profiles = []

    async for doc in res:
        doc["_id"] = str(doc["_id"])
        profiles.append(doc)

    return api_response(profiles)

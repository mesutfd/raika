from fastapi.security import OAuth2PasswordBearer
import datetime
import jwt
from fastapi import Depends, FastAPI, Form, HTTPException, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from starlette.responses import JSONResponse
from typing_extensions import List, Dict, Optional, TypedDict, Union


ALGORITHM = "HS256"
SECRET_KEY = "MY_secure_SECRET_P@ssw0rd_KeY"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


router = APIRouter()

class Credentials(BaseModel):
    username: str
    password: str


users_list: list[Credentials] = []

# creating 10 mamads (no offence, it is my younger brother`s name and my default, default value...)
# default username and passwords are: mamad1 - mamad10 and P@ssw0rd1 - P@ssw0rd10
for i in range(1, 11):
    users_list.append(Credentials(username=f"mamad{i}", password=f"P@ssw0rd{i}"))


def generate_token(username: str) -> str:
    # utc dates are a habit with origin of working with postgres db :D
    payload = {
        "sub": username,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(seconds=1800)
    }
    return jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM
    )


@router.post("/login", tags=["Part 2"])
async def login(username: str = Form(...), password: str = Form(...)) -> JSONResponse:
    user = next(
        (user for user in users_list if user.username == username and user.password == password),
        None
    )
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    token = generate_token(username)
    return JSONResponse({"access_token": token, "token_type": "bearer"})


def decode_token(token: str):
    try:
        payload = jwt.decode(token, algorithms=[ALGORITHM], key=SECRET_KEY)
        username: str = payload.get("sub")

        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")

        user = next((user for user in users_list if user.username == username), None)

        if user is None:
            raise HTTPException(status_code=401, detail="User not found")

        return user

    except Exception as e:
        # log e as exception
        raise HTTPException(status_code=401, detail="Invalid token")


@router.get("/get/me", tags=["Part 2"])
async def get_me(token: str = Depends(oauth2_scheme)):
    data = decode_token(token)
    return data.username

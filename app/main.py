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

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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
from fastapi.security import OAuth2PasswordBearer

ALGORITHM = "HS256"
SECRET_KEY = "MY_secure_SECRET_P@ssw0rd_KeY"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


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


@app.post("/login", tags=["Part 2"])
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


@app.get("/get/me", tags=["Part 2"])
async def get_me(token: str = Depends(oauth2_scheme)):
    data = decode_token(token)
    return data.username


# PART 3
from sqlalchemy import create_engine, Column, Integer, String, text
from sqlalchemy.orm import Session, sessionmaker, declarative_base

# in tasks description there was no reference to create .env file, so all the constants and configurations are hard-coded
DEFAULT_DB_URL = "postgresql+psycopg2://admin:P%40ssw0rd@localhost:5432/postgres"
RAIKA_DB_URL = "postgresql+psycopg2://admin:P%40ssw0rd@localhost:5432/raika"


def is_db_exists(engine, database_name):
    with engine.connect() as conn:
        query = text(
            f"SELECT 1 FROM pg_database WHERE datname='{database_name}'"
        )
        result = conn.execute(query)
        return result.scalar() is not None


def create_db(engine, database_name):
    with engine.connect() as conn:
        conn.execution_options(isolation_level="AUTOCOMMIT")
        conn.execute(text(f"CREATE DATABASE {database_name}"))


default_engine = create_engine(DEFAULT_DB_URL)

# handle creating database if not exists...
if not is_db_exists(default_engine, "raika"):
    create_db(default_engine, "raika")

engine = create_engine(RAIKA_DB_URL)

db_session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# I personally always create a Data Transfer Object due to have full control on I/O data
class CreateBookDto(BaseModel):
    name: str
    author_name: str


class Book(Base):
    __tablename__ = 'book'  # singular table name is a habit

    id = Column(Integer, autoincrement=True, primary_key=True, index=True)  # pk is default nullable false
    name = Column(String, nullable=False)
    author_name = Column(String, nullable=True)


Base.metadata.create_all(bind=engine)


def get_db():
    db = db_session()
    try:
        yield db
    finally:
        db.close()


@app.post("/books", response_model=CreateBookDto, tags=["Part 3"])
async def create_book(book: CreateBookDto, db: Session = Depends(get_db)):
    db_book = Book(name=book.name, author_name=book.author_name)

    db.add(db_book)
    db.commit()
    db.refresh(db_book)

    return db_book


@app.get("/books", tags=["Part 3"])
async def get_books(db: Session = Depends(get_db)) -> JSONResponse:
    books = db.query(Book).all()
    return api_response([{"id": book.id, "name": book.name, "author_name": book.author_name} for book in books])


@app.get("/books/{id}", tags=["Part 3"])
async def get_book_details(id: int, db: Session = Depends(get_db)):
    book = db.query(Book).where(Book.id == id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return api_response(result={"id": book.id, "name": book.name, "author_name": book.author_name})


# PART 4
from motor.motor_asyncio import AsyncIOMotorClient as MongoClient

MONGO_DB_URI = "mongodb://192.168.25.95:27017"

# at this point, naming conventions are a little bit different
mongo_client = MongoClient(MONGO_DB_URI)
mongo_db = mongo_client.Raika
raika_col = mongo_db.users
users_col = mongo_db["users"]


class ProfileDto(BaseModel):
    username: str
    full_name: str
    age: int


@app.post("/profiles", tags=["Part 4"])
async def create_profile(profile: ProfileDto):
    res = await raika_col.insert_one(profile.model_dump())
    return api_response({"_id": str(res.inserted_id), "username": profile.username, "full_name": profile.full_name})


@app.get("/profiles/{username}", tags=["Part 4"])
async def get_profile_details_mongo(username: str):
    res = await users_col.find_one({"username": username})
    if not res:
        raise HTTPException(status_code=404, detail="User not found")
    res["_id"] = str(res['_id'])
    return api_response(res)


@app.get("/profiles", tags=["Part 4"])
async def get_profiles_list_mongo():
    res = users_col.find({})
    profiles = []

    async for doc in res:
        doc["_id"] = str(doc["_id"])
        profiles.append(doc)

    return api_response(profiles)


# PART 5
from fastapi import BackgroundTasks
import time
from threading import Event


class EmailDto(BaseModel):
    email: str


email_sent_event = Event()


def send_notification(email: str):
    time.sleep(11)
    email_sent_event.set()
    print(f"Imaginary Email sent to: {email}")


@app.post("/notify", tags=["Part 5"])
async def notify(
        email_request: EmailDto,
        background_tasks: BackgroundTasks
):
    background_tasks.add_task(send_notification, email_request.email)
    return {"message": "Processing sending email"}


@app.get("/email/is-sent", tags=["Part 5"])
async def get_profiles_list_mongo():
    return email_sent_event.is_set()


# PART 6
import httpx
import asyncio

IMAGINARY_API_X = "https://jsonplaceholder.typicode.com/posts/1"
IMAGINARY_API_Y = "https://jsonplaceholder.typicode.com/comments/1"


async def retrieve_data(client: httpx.AsyncClient, url: str):
    res = await client.get(url)
    res.raise_for_status()
    return res.json()


@app.get("/combine-data", tags=["Part 6"])
async def combine_data():
    async with httpx.AsyncClient() as client:
        res_x, res_y = await asyncio.gather(
            retrieve_data(client, IMAGINARY_API_X),
            retrieve_data(client, IMAGINARY_API_Y)
        )
    return {"X_RESULTS": res_x, "Y_RESULTS": res_y}


# PART 7
# I didnt have redis on my local machine, so I have used rabbitMQ instead, wish it is OK...
import time
import hashlib
import secrets
from celery import Celery
from fastapi import FastAPI
from pydantic import BaseModel, Field, EmailStr

CELERY_BROKER_URL = "pyamqp://guest:123456@localhost//"
celery = Celery("tasks", broker=CELERY_BROKER_URL)


@celery.task
def heavy_compute(num1: int, num2: int):
    time.sleep(5)
    return num1 + num2


class TaskRequest(BaseModel):
    num1: int
    num2: int


@app.post("/tasks", tags=["PART 7"])
def create_task(task: TaskRequest):
    task_result = heavy_compute.apply_async(args=[task.num1, task.num2])
    return {"task_id": task_result.id}


def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    hashed = hashlib.sha256((password + salt).encode()).hexdigest()
    return f"{salt}${hashed}"


class CeleryUser(BaseModel):
    username: str = Field(..., min_length=3, max_length=255)
    email: EmailStr
    password: str = Field(..., min_length=8)


users = []


@app.post("/register", tags=["PART 7"])
def register_user(user: CeleryUser):  # celery user means User in celery-related task
    hashed_passwd = hash_password(user.password)
    users.append({
        "username": user.username,
        "email": user.email,
        "password": hashed_passwd
    })
    return {"message": "User added successfully"}

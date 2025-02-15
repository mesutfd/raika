# I didn't have redis on my local machine, so I have used rabbitMQ instead, wish it is OK...
import os
import time
import hashlib
import secrets
from celery import Celery
from pydantic import BaseModel, Field, EmailStr
from fastapi import APIRouter
from dotenv import load_dotenv

load_dotenv()
router = APIRouter()

RUNNING_IN_DOCKER = os.path.exists('/.dockerenv')

CELERY_BROKER_URL = os.getenv("RABBITMQ_URL") if RUNNING_IN_DOCKER else ("pyamqp://guest:123456@localhost//")

celery = Celery("tasks", broker=CELERY_BROKER_URL)


@celery.task
def heavy_compute(num1: int, num2: int):
    time.sleep(5)
    return num1 + num2


class TaskRequest(BaseModel):
    num1: int
    num2: int


@router.post("/tasks", tags=["PART 7"])
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


@router.post("/register", tags=["PART 7"])
def register_user(user: CeleryUser):  # celery user means User in celery-related task
    hashed_passwd = hash_password(user.password)
    users.append({
        "username": user.username,
        "email": user.email,
        "password": hashed_passwd
    })
    return {"message": "User added successfully"}

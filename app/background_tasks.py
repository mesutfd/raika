from fastapi import BackgroundTasks, APIRouter
import time
from threading import Event

from pydantic import BaseModel

router = APIRouter()


class EmailDto(BaseModel):
    email: str


email_sent_event = Event()


def send_notification(email: str):
    time.sleep(11)
    email_sent_event.set()
    print(f"Imaginary Email sent to: {email}")


@router.post("/notify", tags=["Part 5"])
async def notify(
        email_request: EmailDto,
        background_tasks: BackgroundTasks
):
    background_tasks.add_task(send_notification, email_request.email)
    return {"message": "Processing sending email"}


@router.get("/email/is-sent", tags=["Part 5"])
async def get_profiles_list_mongo():
    return email_sent_event.is_set()

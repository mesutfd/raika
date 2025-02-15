import os

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, text
from sqlalchemy.orm import Session, sessionmaker, declarative_base
from starlette.responses import JSONResponse
from dotenv import load_dotenv

from utils import api_response

load_dotenv()
# in tasks description there was no reference to create .env file, so all the constants and configurations are hard-coded

RUNNING_IN_DOCKER = os.path.exists('/.dockerenv')

DEFAULT_DB_URL = os.getenv("DEFAULT_DB_URL") if os.getenv("DEFAULT_DB_URL") else (
    "postgresql+psycopg2://admin:P%40ssw0rd@postgres:5432/postgres" if RUNNING_IN_DOCKER else
    "postgresql+psycopg2://admin:P%40ssw0rd@localhost:5432/postgres"
)

DATABASE_URL = os.getenv("DATABASE_URL") if os.getenv("DATABASE_URL") else (
    "postgresql+psycopg2://admin:P%40ssw0rd@postgres:5432/raika" if RUNNING_IN_DOCKER else
    "postgresql+psycopg2://admin:P%40ssw0rd@localhost:5432/raika"
)
router = APIRouter()


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

engine = create_engine(DATABASE_URL)

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


@router.post("/books", response_model=CreateBookDto, tags=["Part 3"])
async def create_book(book: CreateBookDto, db: Session = Depends(get_db)):
    db_book = Book(name=book.name, author_name=book.author_name)

    db.add(db_book)
    db.commit()
    db.refresh(db_book)

    return db_book


@router.get("/books", tags=["Part 3"])
async def get_books(db: Session = Depends(get_db)) -> JSONResponse:
    books = db.query(Book).all()
    return api_response([{"id": book.id, "name": book.name, "author_name": book.author_name} for book in books])


@router.get("/books/{id}", tags=["Part 3"])
async def get_book_details(id: int, db: Session = Depends(get_db)):
    book = db.query(Book).where(Book.id == id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return api_response(result={"id": book.id, "name": book.name, "author_name": book.author_name})

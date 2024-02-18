import json
import os
from typing import Literal, Optional
from uuid import uuid4
from fastapi import FastAPI, HTTPException
import random
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from mangum import Mangum
import shutil

class Book(BaseModel):
    name: str
    genre: Literal["fiction", "non-fiction"]
    price: float
    book_id: Optional[str] = uuid4().hex


BOOKS_FILE = "books.json"
BOOKS = []

TMP_BOOKS_FILE = "/tmp/"+BOOKS_FILE
shutil.copy(BOOKS_FILE, TMP_BOOKS_FILE)



app = FastAPI()
handler = Mangum(app)


@app.get("/")
async def root():
    return {"message": "Welcome to my bookstore app!"}


@app.get("/random-book")
async def random_book():
    if os.path.exists(TMP_BOOKS_FILE):
        with open(TMP_BOOKS_FILE, "r") as f:
            BOOKS = json.load(f)
    return random.choice(BOOKS)


@app.get("/list-books")
async def list_books():
    if os.path.exists(TMP_BOOKS_FILE):
        with open(TMP_BOOKS_FILE, "r") as f:
            BOOKS = json.load(f)
    return {"books": BOOKS}


@app.get("/book_by_index/{index}")
async def book_by_index(index: int):
    if os.path.exists(TMP_BOOKS_FILE):
        with open(TMP_BOOKS_FILE, "r") as f:
            BOOKS = json.load(f)
    if index < len(BOOKS):
        return BOOKS[index]
    else:
        raise HTTPException(404, f"Book index {index} out of range ({len(BOOKS)}).")


@app.post("/add-book")
async def add_book(book: Book):
    if os.path.exists(TMP_BOOKS_FILE):
        with open(TMP_BOOKS_FILE, "r") as f:
            BOOKS = json.load(f)
    book.book_id = uuid4().hex
    json_book = jsonable_encoder(book)
    BOOKS.append(json_book)

    with open(TMP_BOOKS_FILE, "w") as f:
        json.dump(BOOKS, f)

    return {"book_id": book.book_id}


@app.get("/get-book")
async def get_book(book_id: str):
    if os.path.exists(TMP_BOOKS_FILE):
        with open(TMP_BOOKS_FILE, "r") as f:
            BOOKS = json.load(f)

    for book in BOOKS:
        b = Book.model_validate(book)
        if b.book_id == book_id:
            return book

    raise HTTPException(404, f"Book ID {book_id} not found in database.")

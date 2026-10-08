from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI
from psycopg.rows import dict_row
from pydantic import BaseModel, Field, field_validator

import db

_schema_ready = False


@asynccontextmanager
async def lifespan(_app):
    global _schema_ready
    if not _schema_ready:
        connection = db.connect()
        connection.close()
        _schema_ready = True
    yield


app = FastAPI(lifespan=lifespan)


def get_connection():
    connection = db.connect()
    connection.row_factory = dict_row
    try:
        yield connection
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


class TarefaCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str = Field(default="", max_length=2000)

    @field_validator("title")
    @classmethod
    def title_not_whitespace(cls, value):
        if value.strip() == "":
            raise ValueError("title must not be blank")
        return value


def serialize(row):
    return {
        "id": row["id"],
        "title": row["title"],
        "description": row["description"],
        "status": row["status"],
        "created_at": row["created_at"].isoformat(),
        "updated_at": row["updated_at"].isoformat(),
    }


@app.post("/tarefas", status_code=201)
def criar_tarefa(body: TarefaCreate, connection=Depends(get_connection)):
    cursor = connection.execute(
        """
        INSERT INTO tarefas (title, description)
        VALUES (%s, %s)
        RETURNING id, title, description, status, created_at, updated_at
        """,
        (body.title, body.description),
    )
    row = cursor.fetchone()
    cursor.close()
    return serialize(row)

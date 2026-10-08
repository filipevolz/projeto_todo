from contextlib import asynccontextmanager
from typing import Literal

from fastapi import Depends, FastAPI, HTTPException
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


def reject_blank_title(value):
    if value.strip() == "":
        raise ValueError("title must not be blank")
    return value


class TarefaCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str = Field(default="", max_length=2000)

    @field_validator("title")
    @classmethod
    def title_not_whitespace(cls, value):
        return reject_blank_title(value)


class StatusBody(BaseModel):
    status: Literal["pendente", "concluido"]


class TarefaReplace(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str = Field(max_length=2000)

    @field_validator("title")
    @classmethod
    def title_not_whitespace(cls, value):
        return reject_blank_title(value)


def not_found(task_id):
    raise HTTPException(
        status_code=404, detail=f"O ID {task_id} não foi encontrado"
    )


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


@app.get("/tarefas")
def listar_tarefas(connection=Depends(get_connection)):
    cursor = connection.execute(
        """
        SELECT id, title, description, status, created_at, updated_at
        FROM tarefas
        ORDER BY id ASC
        """
    )
    rows = cursor.fetchall()
    cursor.close()
    return [serialize(row) for row in rows]


@app.get("/tarefas/{task_id}")
def obter_tarefa(task_id: int, connection=Depends(get_connection)):
    cursor = connection.execute(
        """
        SELECT id, title, description, status, created_at, updated_at
        FROM tarefas
        WHERE id = %s
        """,
        (task_id,),
    )
    row = cursor.fetchone()
    cursor.close()
    if row is None:
        not_found(task_id)
    return serialize(row)


@app.put("/tarefas/{task_id}")
def atualizar_tarefa(
    task_id: int, body: TarefaReplace, connection=Depends(get_connection)
):
    cursor = connection.execute(
        """
        UPDATE tarefas
        SET title = %s,
            description = %s,
            updated_at = clock_timestamp()
        WHERE id = %s
        RETURNING id, title, description, status, created_at, updated_at
        """,
        (body.title, body.description, task_id),
    )
    row = cursor.fetchone()
    cursor.close()
    if row is None:
        not_found(task_id)
    return serialize(row)


@app.patch("/tarefas/{task_id}/status")
def alterar_status(
    task_id: int, body: StatusBody, connection=Depends(get_connection)
):
    cursor = connection.execute(
        """
        UPDATE tarefas
        SET status = %s,
            updated_at = clock_timestamp()
        WHERE id = %s
        RETURNING id, title, description, status, created_at, updated_at
        """,
        (body.status, task_id),
    )
    row = cursor.fetchone()
    cursor.close()
    if row is None:
        not_found(task_id)
    return serialize(row)

import os

import psycopg

CREATE_TAREFAS = """
CREATE TABLE IF NOT EXISTS tarefas (
    id serial PRIMARY KEY,
    title text NOT NULL,
    description text NOT NULL DEFAULT '',
    status text NOT NULL DEFAULT 'pendente'
        CHECK (status IN ('pendente', 'concluido')),
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now()
)
"""


def connect():
    connection = psycopg.connect(os.environ["DATABASE_URL"])
    connection.execute(CREATE_TAREFAS)
    connection.commit()
    return connection

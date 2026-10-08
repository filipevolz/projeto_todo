import os
import re
import subprocess
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from psycopg.rows import dict_row

ROOT = Path(__file__).resolve().parents[1]
ISO_WITH_OFFSET = re.compile(
    r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?[+-]\d{2}:\d{2}$"
)


def load_env():
    env_path = ROOT / ".env"
    for raw in env_path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        if key.startswith("export "):
            key = key[len("export ") :].strip()
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
            value = value[1:-1]
        os.environ.setdefault(key, value)


load_env()

import db  # noqa: E402
import main  # noqa: E402
from main import app, get_connection  # noqa: E402


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        connection = db.connect()
        try:
            connection.row_factory = dict_row
            connection.execute("DELETE FROM tarefas").close()

            def override():
                yield connection

            app.dependency_overrides[get_connection] = override
            yield test_client
        finally:
            app.dependency_overrides.clear()
            connection.rollback()
            connection.close()


def test_post_returns_201_pending_with_iso_timestamps(client):
    response = client.post(
        "/tarefas",
        json={"title": "Comprar leite", "description": "integral"},
    )
    assert response.status_code == 201
    body = response.json()
    assert set(body) == {
        "id",
        "title",
        "description",
        "status",
        "created_at",
        "updated_at",
    }
    assert isinstance(body["id"], int)
    assert body["title"] == "Comprar leite"
    assert body["description"] == "integral"
    assert body["status"] == "pendente"
    assert ISO_WITH_OFFSET.match(body["created_at"])
    assert ISO_WITH_OFFSET.match(body["updated_at"])


def test_post_omitted_description_is_empty_string(client):
    response = client.post("/tarefas", json={"title": "Sem descricao"})
    assert response.status_code == 201
    assert response.json()["description"] == ""


def test_post_duplicate_title_inserts_new_id(client):
    first = client.post(
        "/tarefas", json={"title": "Repetida", "description": "uma"}
    )
    second = client.post(
        "/tarefas", json={"title": "Repetida", "description": "outra"}
    )
    assert first.status_code == 201
    assert second.status_code == 201
    assert first.json()["title"] == "Repetida"
    assert second.json()["title"] == "Repetida"
    assert first.json()["id"] != second.json()["id"]


def test_post_missing_title_returns_422(client):
    response = client.post("/tarefas", json={"description": "sem titulo"})
    assert response.status_code == 422


def test_post_empty_title_returns_422(client):
    response = client.post("/tarefas", json={"title": ""})
    assert response.status_code == 422


def test_post_whitespace_title_returns_422(client):
    response = client.post("/tarefas", json={"title": "   "})
    assert response.status_code == 422


def test_post_title_longer_than_200_returns_422(client):
    response = client.post("/tarefas", json={"title": "a" * 201, "description": ""})
    assert response.status_code == 422


def test_post_description_longer_than_2000_returns_422(client):
    response = client.post(
        "/tarefas",
        json={"title": "limite", "description": "d" * 2001},
    )
    assert response.status_code == 422


def test_get_tarefas_empty_returns_empty_array(client):
    response = client.get("/tarefas")
    assert response.status_code == 200
    assert response.json() == []


def test_get_tarefas_returns_every_row_ordered_by_id(client):
    first = client.post(
        "/tarefas", json={"title": "primeira", "description": "a"}
    )
    second = client.post(
        "/tarefas", json={"title": "segunda", "description": "b"}
    )
    assert first.status_code == 201
    assert second.status_code == 201
    response = client.get("/tarefas")
    assert response.status_code == 200
    body = response.json()
    assert [row["id"] for row in body] == [first.json()["id"], second.json()["id"]]
    assert body[0]["id"] < body[1]["id"]
    assert [row["id"] for row in body] == sorted(row["id"] for row in body)
    assert body[0]["title"] == "primeira"
    assert body[1]["title"] == "segunda"
    assert body[0]["description"] == "a"
    assert body[1]["description"] == "b"


def test_second_client_sees_task_from_the_database(client):
    created = client.post(
        "/tarefas", json={"title": "persistida", "description": "no banco"}
    )
    assert created.status_code == 201
    task = created.json()
    with TestClient(app) as other:
        listed = other.get("/tarefas")
    assert listed.status_code == 200
    match = next(row for row in listed.json() if row["id"] == task["id"])
    assert match["title"] == "persistida"
    assert match["description"] == "no banco"
    assert match["status"] == "pendente"
    assert match["id"] == task["id"]
    assert not hasattr(main, "lista_de_tarefas")
    assert not any(isinstance(value, list) for value in vars(main).values())


def test_import_does_not_read_stdin_or_print_menu():
    result = subprocess.run(
        [sys.executable, "-c", "import main"],
        cwd=str(ROOT),
        env=os.environ.copy(),
        capture_output=True,
        text=True,
        timeout=15,
        input="",
    )
    output = result.stdout + result.stderr
    assert result.returncode == 0
    assert "1 - CRIAR TAREFA" not in output
    assert "2 - LISTAR TAREFA" not in output
    assert "3 - BUSCAR TAREFA" not in output
    assert "4 - ATUALIZAR TAREFA" not in output
    assert "5 - ALTERAR STATUS" not in output
    assert "6 - DELETAR TAREFA" not in output
    assert "7 - SAIR" not in output
    assert "Escolha uma opção" not in output

# To-Do List API

API HTTP para criar, listar, buscar, atualizar, mudar o status e apagar tarefas no Postgres.

## Como executar

1. Instale as dependências:

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. Exporte `DATABASE_URL` com a connection string do banco. O arquivo `.env.example` tem o placeholder da variável. Se a variável não estiver no ambiente, `python migrate.py` lê o arquivo `.env`.

3. Aplique as migrations:

   ```bash
   python migrate.py
   ```

4. Suba o servidor:

   ```bash
   uvicorn main:app
   ```

## Rotas

- `POST /tasks`
- `GET /tasks`
- `GET /tasks/{id}`
- `PUT /tasks/{id}`
- `PATCH /tasks/{id}/status`
- `DELETE /tasks/{id}`

O status de uma tarefa é `pending` ou `completed`.

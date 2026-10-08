# To-Do List API

API HTTP para criar, listar, buscar, atualizar, mudar o status e apagar tarefas no Postgres.

## Como executar

1. Instale as dependências:

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. Exporte `DATABASE_URL` com a connection string do banco. O arquivo `.env.example` tem o placeholder da variável.

3. Suba o servidor:

   ```bash
   uvicorn main:app
   ```

## Rotas

- `POST /tarefas`
- `GET /tarefas`
- `GET /tarefas/{id}`
- `PUT /tarefas/{id}`
- `PATCH /tarefas/{id}/status`
- `DELETE /tarefas/{id}`

O status de uma tarefa é `pendente` ou `concluido`.

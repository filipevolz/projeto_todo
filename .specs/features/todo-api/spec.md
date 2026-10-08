# Todo API Specification

## Problem Statement

O CRUD em `main.py` guarda tarefas numa lista em memória e só existe como menu de terminal. O processo acaba e os dados somem. A API HTTP precisa gravar as mesmas tarefas no Postgres do Neon e responder com status e erros previsíveis.

## Goals

- [ ] Um cliente HTTP cria, lista, busca, atualiza, muda o status e apaga tarefas persistidas no Neon.
- [ ] Status só aceita `pendente` e `concluido`. Entrada inválida responde 422. ID ausente responde 404 com a mensagem já usada no CLI.
- [ ] O menu interativo do terminal deixa de existir.

## Out of Scope

| Feature | Reason |
| --- | --- |
| Autenticação e rate limit | API local de prática, sem usuários. |
| Paginação, filtros e ordenação customizada | A lista inteira, ordenada por `id`, cabe no escopo. |
| Soft delete, TTL e arquivamento | Delete é físico. |
| Frontend | Só a API. |
| Lock otimista | Uma escrita por vez; a última escrita ganha. |
| Manter o menu do CLI | A interface passa a ser só HTTP. |

---

## Assumptions & Open Questions

| Assumption / decision | Chosen default | Rationale | Confirmed? |
| --- | --- | --- | --- |
| Superfície | Só FastAPI. O loop do CLI sai de `main.py`. | O usuário escolheu API HTTP no lugar do menu. | y |
| Status | Somente `pendente` e `concluido`. Qualquer outro valor responde 422. Transição nos dois sentidos. | O usuário rejeitou texto livre. O README já cita esses dois valores. | y |
| JSON | Campos `id`, `title`, `description`, `status`, `created_at`, `updated_at`. | São os campos do dicionário atual em `main.py`. | y |
| Timestamps | `timestamptz` no banco, ISO 8601 com offset UTC na resposta. | O formato `%Y-%m-%d %H:%M:%S` do CLI não carrega fuso. | y |
| Título | Obrigatório, 1 a 200 caracteres. Só espaços conta como vazio. | Limite concreto para o 422. | y |
| Descrição | Opcional no POST, 0 a 2000 caracteres, default string vazia. No PUT, `title` e `description` são obrigatórios. | O CLI pede descrição, mas não a valida. O PUT substitui os dois campos. | y |
| Títulos duplicados | Permitidos. Cada POST insere uma linha nova. | O CLI não deduplica. | y |
| Lista | `GET /tarefas` devolve todas as linhas, `id` crescente. Vazio devolve `[]`. | Sem paginação neste escopo. | y |
| ID ausente | 404 e `detail` igual a `O ID {id} não foi encontrado`. | É o texto que o CLI já devolve. | y |
| Delete existente | 200 e `message` igual a `A tarefa {title} foi removida com sucesso!`. A linha some. | É o texto de sucesso do CLI. | y |
| ID não inteiro | 422. | O path `{id}` é inteiro. | y |
| Banco fora | 503 e `detail` igual a `Banco de dados indisponível`, sem stack trace no corpo. | Falha do Neon precisa de um status próprio, distinto de 404 e 422. | y |
| Segredo | `DATABASE_URL` só no `.env`. O git ignora `.env`. `.env.example` leva placeholder. | A connection string com senha não entra no repositório. | y |
| Conexão | Host pooler, `sslmode=require`, driver `psycopg`. Tabela criada na subida se não existir. | É a URL pooled que o usuário passou. | y |
| Concorrência | Última escrita ganha. Sem versão de linha. | Um usuário local. | y |
| Idempotência | POST não é idempotente. DELETE repetido no mesmo id responde 404. | Cada POST é uma tarefa nova. O segundo delete não acha a linha. | y |

**Open questions:** none - all resolved or logged above.

---

## User Stories

### P1: Criar tarefa ⭐ MVP

**User Story**: As a client, I want to create a task over HTTP so that it stays in Neon after the process stops.

**Why P1**: Sem o POST persistido não existe todo list.

**Acceptance Criteria**:

1. WHEN a client sends POST /tarefas with a title of 1 to 200 characters and a description of 0 to 2000 characters THEN the system SHALL respond 201 with id, title, description, status pendente, and created_at and updated_at as ISO 8601 timestamps.
2. WHEN a client sends POST /tarefas without description THEN the system SHALL store description as an empty string and respond 201.
3. WHEN a client sends POST /tarefas with a title that already exists THEN the system SHALL insert a new row with a new id and respond 201.
4. IF title is missing, empty, or only whitespace THEN the system SHALL respond 422.
5. IF title length is greater than 200 characters THEN the system SHALL respond 422.
6. IF description length is greater than 2000 characters THEN the system SHALL respond 422.

**Independent Test**: POST uma tarefa e ler a mesma linha de volta no Postgres.

---

### P1: Listar tarefas ⭐ MVP

**User Story**: As a client, I want the full task list so that I can see everything stored.

**Why P1**: O CLI já lista todas as tarefas. A API precisa do mesmo.

**Acceptance Criteria**:

1. WHEN a client sends GET /tarefas and no rows exist THEN the system SHALL respond 200 with an empty JSON array.
2. WHEN a client sends GET /tarefas and rows exist THEN the system SHALL respond 200 with every row ordered by id ascending.
3. WHEN a task was created by a previous request THEN a new client SHALL read that same task from the database on GET /tarefas.

**Independent Test**: Lista vazia devolve `[]`. Duas criações aparecem em ordem de id. Um segundo cliente vê a linha.

---

### P1: Buscar tarefa ⭐ MVP

**User Story**: As a client, I want one task by id so that I can open it or learn it is gone.

**Why P1**: O CLI já busca por id.

**Acceptance Criteria**:

1. WHEN a client sends GET /tarefas/{id} and the id exists THEN the system SHALL respond 200 with that task.
2. IF the id does not exist THEN the system SHALL respond 404 with detail equal to `O ID {id} não foi encontrado`.
3. IF the id path segment is not an integer THEN the system SHALL respond 422.

**Independent Test**: GET de um id criado devolve a tarefa. GET de um id ausente devolve 404 com o texto exato. GET `/tarefas/abc` devolve 422.

---

### P1: Atualizar tarefa ⭐ MVP

**User Story**: As a client, I want to replace title and description so that the task text stays current.

**Why P1**: O CLI já atualiza título e descrição sem mexer no status.

**Acceptance Criteria**:

1. WHEN a client sends PUT /tarefas/{id} with a valid title and description and the id exists THEN the system SHALL respond 200 with the new title and description, the same status, and an updated_at later than the stored updated_at.
2. IF the id does not exist on PUT /tarefas/{id} THEN the system SHALL respond 404 with detail equal to `O ID {id} não foi encontrado`.
3. IF a PUT /tarefas/{id} omits title or description, or either field breaks the create bounds, THEN the system SHALL respond 422 and leave the stored row unchanged.

**Independent Test**: PUT muda título e descrição, conserva o status e avança `updated_at`. PUT inválido não altera a linha.

---

### P1: Alterar status ⭐ MVP

**User Story**: As a client, I want to set status to pendente or concluido so that invalid states never get stored.

**Why P1**: O usuário limitou o status a esses dois valores.

**Acceptance Criteria**:

1. WHEN a client sends PATCH /tarefas/{id}/status with status pendente or concluido and the id exists THEN the system SHALL respond 200 with that status and an updated_at later than the stored updated_at.
2. WHEN the stored status is pendente and the client sends concluido THEN the system SHALL persist concluido.
3. WHEN the stored status is concluido and the client sends pendente THEN the system SHALL persist pendente.
4. IF status is any value other than pendente or concluido THEN the system SHALL respond 422 and leave the stored row unchanged.
5. IF the id does not exist on PATCH /tarefas/{id}/status THEN the system SHALL respond 404 with detail equal to `O ID {id} não foi encontrado`.

**Independent Test**: `pendente` vai para `concluido` e volta. `fazendo` responde 422 e o status anterior continua.

---

### P1: Apagar tarefa ⭐ MVP

**User Story**: As a client, I want to delete a task so that it no longer appears in the list.

**Why P1**: O CLI já remove a tarefa e confirma com uma frase.

**Acceptance Criteria**:

1. WHEN a client sends DELETE /tarefas/{id} and the id exists THEN the system SHALL respond 200 with message equal to `A tarefa {title} foi removida com sucesso!` and a following GET /tarefas/{id} SHALL respond 404.
2. IF the id does not exist on DELETE /tarefas/{id} THEN the system SHALL respond 404 with detail equal to `O ID {id} não foi encontrado`.

**Independent Test**: DELETE devolve a frase com o título e o GET seguinte é 404. DELETE de novo no mesmo id é 404.

---

### P1: Persistência e falha do banco ⭐ MVP

**User Story**: As a client, I want a clear failure when Neon is down so that I do not see a stack trace.

**Why P1**: A lista deixa de viver no processo. A falha do banco precisa de contrato.

**Acceptance Criteria**:

1. The system SHALL read and write tasks only through DATABASE_URL and SHALL NOT keep the task list in a process-memory collection.
2. The system SHALL create the tarefas table on startup when it is missing, with status constrained to pendente and concluido.
3. IF the database is unreachable THEN the system SHALL respond 503 with detail equal to `Banco de dados indisponível` and SHALL NOT include a stack trace in the response body.

**Independent Test**: Com o banco acessível, a tarefa sobrevive a um novo cliente. Com a conexão forçada a falhar, a resposta é 503 com o texto exato e sem `Traceback`.

---

### P2: Operador sobe a API

**User Story**: As an operator, I want the repo to keep the Neon password out of git and the README to show how to run the API.

**Why P2**: Sem isso a connection string vaza ou ninguém sobe o servidor. Não bloqueia o CRUD.

**Acceptance Criteria**:

1. The repository SHALL ignore `.env` and the committed `.env.example` SHALL contain a DATABASE_URL placeholder without a password.
2. The README SHALL document DATABASE_URL, the uvicorn command, and the six routes POST /tarefas, GET /tarefas, GET /tarefas/{id}, PUT /tarefas/{id}, PATCH /tarefas/{id}/status, and DELETE /tarefas/{id}.
3. The system SHALL NOT start an interactive terminal menu when the process starts.

**Independent Test**: `.env` está no `.gitignore`, `.env.example` não tem senha, e importar o app não pede `input()`.

---

## Edge Cases

- IF the task list is empty THEN GET /tarefas SHALL respond 200 with `[]`.
- IF title is only spaces THEN POST /tarefas SHALL respond 422.
- IF DELETE is repeated for an id that was already removed THEN the system SHALL respond 404.
- IF PUT or PATCH names an id that does not exist THEN the system SHALL respond 404 and insert nothing.

---

## Requirement Traceability

| Requirement ID | Story | Phase | Status |
| --- | --- | --- | --- |
| TODO-01 | P1: Criar tarefa | Tasks | Done |
| TODO-02 | P1: Criar tarefa | Tasks | Done |
| TODO-03 | P1: Criar tarefa | Tasks | Done |
| TODO-04 | P1: Criar tarefa | Tasks | Done |
| TODO-05 | P1: Criar tarefa | Tasks | Done |
| TODO-06 | P1: Criar tarefa | Tasks | Done |
| TODO-07 | P1: Listar tarefas | Tasks | In Tasks |
| TODO-08 | P1: Listar tarefas | Tasks | In Tasks |
| TODO-09 | P1: Listar tarefas | Tasks | In Tasks |
| TODO-10 | P1: Buscar tarefa | Tasks | In Tasks |
| TODO-11 | P1: Buscar tarefa | Tasks | In Tasks |
| TODO-12 | P1: Buscar tarefa | Tasks | In Tasks |
| TODO-13 | P1: Atualizar tarefa | Tasks | In Tasks |
| TODO-14 | P1: Atualizar tarefa | Tasks | In Tasks |
| TODO-15 | P1: Atualizar tarefa | Tasks | In Tasks |
| TODO-16 | P1: Alterar status | Tasks | In Tasks |
| TODO-17 | P1: Alterar status | Tasks | In Tasks |
| TODO-18 | P1: Alterar status | Tasks | In Tasks |
| TODO-19 | P1: Alterar status | Tasks | In Tasks |
| TODO-20 | P1: Alterar status | Tasks | In Tasks |
| TODO-21 | P1: Apagar tarefa | Tasks | In Tasks |
| TODO-22 | P1: Apagar tarefa | Tasks | In Tasks |
| TODO-23 | P1: Persistência e falha do banco | Tasks | In Tasks |
| TODO-24 | P1: Persistência e falha do banco | Tasks | Done |
| TODO-25 | P1: Persistência e falha do banco | Tasks | In Tasks |
| TODO-26 | P2: Operador sobe a API | Tasks | Done |
| TODO-27 | P2: Operador sobe a API | Tasks | In Tasks |
| TODO-28 | P2: Operador sobe a API | Tasks | Done |

**Coverage:** 28 total, 28 mapped to tasks, 0 unmapped.

---

## Success Criteria

- [ ] Os seis endpoints respondem os status 201, 200, 404, 422 e 503 definidos acima.
- [ ] Nenhuma senha de banco aparece em arquivo versionado.
- [ ] `python3 -m pytest -q` passa com rollback, sem deixar linhas novas no Neon.

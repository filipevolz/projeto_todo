# Todo API Tasks

## Execution Protocol (MANDATORY -- do not skip)

Implement these tasks with the `tlc-spec-driven` skill: **activate it by name and follow its Execute flow and Critical Rules.** Do not search for skill files by filesystem path. The skill is the source of truth for the full flow (per-task cycle, sub-agent delegation, adequacy review, Verifier, discrimination sensor).

**If the skill cannot be activated, STOP and tell the user - do not proceed without it.**

---

**Design**: skipped. Medium scope; the contract is `.specs/features/todo-api/spec.md`.
**Status**: Draft

---

## Test Coverage Matrix

> Generated from codebase, project guidelines, and spec - confirm before Execute. Guidelines found: none - strong defaults applied. No `AGENTS.md`, `CONTRIBUTING.md`, `pytest.ini`, `pyproject.toml`, `tox.ini`, Makefile, or CI workflow exists. No test files exist. The approved plan already chose pytest + httpx against Neon, one transaction per test, rollback at the end. `python3 -m pytest -q` is the project command.

| Code Layer | Required Test Type | Coverage Expectation | Location Pattern | Run Command |
| --- | --- | --- | --- | --- |
| Route | integration | All six routes: happy path, every listed edge case, and 404, 422, and 503 | `tests/test_tarefas.py` | `python3 -m pytest -q` |
| Schema / connection | none | Build gate only. Startup DDL is proved when the first POST returns 201. | `db.py` | build gate only |
| Config | none | Build gate only | `requirements.txt`, `.gitignore`, `.env.example` | build gate only |
| Docs | none | Build gate only | `README.md` | build gate only |

## Gate Check Commands

> Generated from codebase - confirm before Execute. No linter or formatter is configured, so the build gate compiles the Python modules.

| Gate Level | When to Use | Command |
| --- | --- | --- |
| Quick | Not used. This feature has no unit-test layer. | — |
| Full | After every task that adds or changes a route | `python3 -m pytest -q` |
| Build | After config, schema, docs, and at the end of a phase | `python3 -m compileall -q main.py db.py` |

---

## Execution Plan

Phases run in order. Tasks inside a phase run in order. Twelve tasks pack into three batches (Phase 1, Phase 2, Phase 3) because a batch holds about seven tasks and never splits a phase.

### Phase 1: Foundation

```
T1 → T4
T2
T3
```

### Phase 2: Routes

```
T5 → T6 → T7 → T8 → T9 → T10 → T11
```

### Phase 3: Docs

```
T12
```

---

## Task Breakdown

### Phase 1: Foundation

### T1: Declare runtime dependencies

**What**: Add `requirements.txt` with fastapi, uvicorn, psycopg[binary], pytest, and httpx.
**Where**: `requirements.txt`
**Depends on**: None
**Reuses**: none
**Requirement**: TODO-23

**Tools**:

- MCP: NONE
- Skill: NONE

**Done when**:

- [x] `requirements.txt` lists fastapi, uvicorn, psycopg[binary], pytest, and httpx
- [x] Gate check passes: `python3 -m compileall -q main.py db.py` once `db.py` exists (T4). Until then, `python3 -m compileall -q main.py` passes.

**Tests**: none
**Gate**: build

**Commit**: `build(api): declare fastapi and psycopg dependencies`

---

### T2: Ignore the Neon credential file

**What**: Add `.env` to `.gitignore` so the connection string is never committed.
**Where**: `.gitignore`
**Depends on**: None
**Reuses**: `.gitignore`
**Requirement**: TODO-26

**Tools**:

- MCP: NONE
- Skill: NONE

**Done when**:

- [x] `.gitignore` contains `.env`
- [x] `git check-ignore -q .env` exits 0
- [x] Gate check passes: `python3 -m compileall -q main.py`

**Tests**: none
**Gate**: build

**Commit**: `chore(git): ignore the database credential file`

---

### T3: Add a credential placeholder

**What**: Add `.env.example` with `DATABASE_URL=` and a placeholder host, no password.
**Where**: `.env.example`
**Depends on**: None
**Reuses**: none
**Requirement**: TODO-26

**Tools**:

- MCP: NONE
- Skill: NONE

**Done when**:

- [x] `.env.example` contains the key `DATABASE_URL`
- [x] The file contains no `@` userinfo and no live password
- [x] Gate check passes: `python3 -m compileall -q main.py`

**Tests**: none
**Gate**: build

**Commit**: `chore(env): add a database url placeholder`

---

### T4: Open Neon and create the tarefas table

**What**: Add `db.py` that reads `DATABASE_URL`, connects with psycopg using the pooled URL, and creates `tarefas` on startup when the table is missing.
**Where**: `db.py`
**Depends on**: T1
**Reuses**: field names in `main.py` (`id`, `title`, `description`, `status`, `created_at`, `updated_at`)
**Requirement**: TODO-23, TODO-24

**Tools**:

- MCP: NONE
- Skill: NONE

**Done when**:

- [x] `db.py` reads `DATABASE_URL` and does not embed a connection string
- [x] Startup SQL creates `tarefas` with `status` constrained to `pendente` and `concluido`, and timestamptz defaults for both timestamps
- [x] Gate check passes: `python3 -m compileall -q main.py db.py`

**Tests**: none
**Gate**: build

**Commit**: `feat(db): connect to neon and create tarefas`

---

### Phase 2: Routes

### T5: Create a task

**What**: Replace the terminal menu in `main.py` with a FastAPI app and `POST /tarefas`. Co-locate the first integration tests in `tests/test_tarefas.py` (transaction rolled back).
**Where**: `main.py`
**Depends on**: T4
**Reuses**: `criar_tarefa` behavior in `main.py` (status starts as `pendente`)
**Requirement**: TODO-01, TODO-02, TODO-03, TODO-04, TODO-05, TODO-06, TODO-28

**Tools**:

- MCP: NONE
- Skill: NONE

**Done when**:

- [ ] `POST /tarefas` returns 201 with `pendente` and ISO 8601 timestamps
- [ ] Omitted description is stored as `""`. A duplicate title inserts a new id
- [ ] Missing, empty, or whitespace title returns 422. Title over 200 or description over 2000 returns 422
- [ ] Importing the app does not read from stdin and does not print the numbered menu
- [ ] Each test rolls back its transaction
- [ ] Gate check passes: `python3 -m pytest -q`
- [ ] Test count: 9 tests pass (no silent deletions)

**Tests**: integration
**Gate**: full

**Commit**: `feat(api): create a task over http`

---

### T6: List tasks

**What**: Add `GET /tarefas` and its integration tests, including a second client that reads the row from Neon.
**Where**: `main.py`
**Depends on**: T5
**Reuses**: `POST /tarefas` from T5
**Requirement**: TODO-07, TODO-08, TODO-09, TODO-23

**Tools**:

- MCP: NONE
- Skill: NONE

**Done when**:

- [ ] `GET /tarefas` with no rows returns 200 and `[]`
- [ ] Rows come back ordered by `id` ascending
- [ ] A second client sees a task created by the first request
- [ ] The module does not keep a process-memory task list
- [ ] Gate check passes: `python3 -m pytest -q`
- [ ] Test count: 12 tests pass (no silent deletions)

**Tests**: integration
**Gate**: full

**Commit**: `feat(api): list tasks from neon`

---

### T7: Get one task

**What**: Add `GET /tarefas/{id}` and its integration tests.
**Where**: `main.py`
**Depends on**: T6
**Reuses**: the 404 sentence already returned by `obter_tarefa_por_id` in the old CLI
**Requirement**: TODO-10, TODO-11, TODO-12

**Tools**:

- MCP: NONE
- Skill: NONE

**Done when**:

- [ ] An existing id returns 200 and that task
- [ ] A missing id returns 404 with detail `O ID {id} não foi encontrado`
- [ ] `GET /tarefas/abc` returns 422
- [ ] Gate check passes: `python3 -m pytest -q`
- [ ] Test count: 15 tests pass (no silent deletions)

**Tests**: integration
**Gate**: full

**Commit**: `feat(api): fetch one task by id`

---

### T8: Replace title and description

**What**: Add `PUT /tarefas/{id}` and its integration tests.
**Where**: `main.py`
**Depends on**: T7
**Reuses**: `atualizar_tarefa` behavior (title and description change, status stays)
**Requirement**: TODO-13, TODO-14, TODO-15

**Tools**:

- MCP: NONE
- Skill: NONE

**Done when**:

- [ ] A valid PUT returns 200, keeps `status`, and sets `updated_at` later than the stored value
- [ ] A missing id returns 404 with detail `O ID {id} não foi encontrado`
- [ ] Omitting title or description, or breaking the create bounds, returns 422 and leaves the row unchanged
- [ ] Gate check passes: `python3 -m pytest -q`
- [ ] Test count: 20 tests pass (no silent deletions)

**Tests**: integration
**Gate**: full

**Commit**: `feat(api): replace task title and description`

---

### T9: Change status

**What**: Add `PATCH /tarefas/{id}/status` and its integration tests.
**Where**: `main.py`
**Depends on**: T8
**Reuses**: `alterar_status_tarefa`, restricted to `pendente` and `concluido`
**Requirement**: TODO-16, TODO-17, TODO-18, TODO-19, TODO-20

**Tools**:

- MCP: NONE
- Skill: NONE

**Done when**:

- [ ] `pendente` can become `concluido` and `concluido` can become `pendente`, each with 200 and a later `updated_at`
- [ ] Any other status returns 422 and leaves the row unchanged
- [ ] A missing id returns 404 with detail `O ID {id} não foi encontrado`
- [ ] Gate check passes: `python3 -m pytest -q`
- [ ] Test count: 24 tests pass (no silent deletions)

**Tests**: integration
**Gate**: full

**Commit**: `feat(api): change task status`

---

### T10: Delete a task

**What**: Add `DELETE /tarefas/{id}` and its integration tests.
**Where**: `main.py`
**Depends on**: T9
**Reuses**: the success sentence from `deletar_tarefa`
**Requirement**: TODO-21, TODO-22

**Tools**:

- MCP: NONE
- Skill: NONE

**Done when**:

- [ ] Deleting an existing id returns 200 with message `A tarefa {title} foi removida com sucesso!` and a following GET returns 404
- [ ] Deleting a missing id returns 404 with detail `O ID {id} não foi encontrado`
- [ ] Gate check passes: `python3 -m pytest -q`
- [ ] Test count: 26 tests pass (no silent deletions)

**Tests**: integration
**Gate**: full

**Commit**: `feat(api): delete a task`

---

### T11: Map a dead database to 503

**What**: When the database connection fails, respond 503 from the API and cover it with an integration test.
**Where**: `main.py`
**Depends on**: T10
**Reuses**: `db.py` connection helper from T4
**Requirement**: TODO-25

**Tools**:

- MCP: NONE
- Skill: NONE

**Done when**:

- [ ] A failed connection returns 503 with detail `Banco de dados indisponível`
- [ ] The response body does not contain `Traceback`
- [ ] Gate check passes: `python3 -m pytest -q`
- [ ] Test count: 27 tests pass (no silent deletions)

**Tests**: integration
**Gate**: full

**Commit**: `feat(api): return 503 when the database is down`

---

### Phase 3: Docs

### T12: Document how to run the API

**What**: Replace the CLI instructions in the README with `DATABASE_URL`, the uvicorn command, and the six routes.
**Where**: `README.md`
**Depends on**: T11
**Reuses**: route list from the spec
**Requirement**: TODO-27

**Tools**:

- MCP: NONE
- Skill: NONE

**Done when**:

- [ ] README names `DATABASE_URL`, the uvicorn command, and POST /tarefas, GET /tarefas, GET /tarefas/{id}, PUT /tarefas/{id}, PATCH /tarefas/{id}/status, DELETE /tarefas/{id}
- [ ] README no longer tells the operator to drive the numbered terminal menu
- [ ] Gate check passes: `python3 -m compileall -q main.py db.py`

**Tests**: none
**Gate**: build

**Commit**: `docs(api): document the task endpoints`

---

## Phase Execution Map

```
Phase 1 → Phase 2 → Phase 3

Phase 1: T1 → T4
Phase 2: T5 → T6 → T7 → T8 → T9 → T10 → T11
Phase 3: T12
```

T2 and T3 have no dependencies. T5 depends on T4, and T12 depends on T11. Those two edges cross phases, so they are not drawn inside a phase diagram.

Execution is sequential. Twelve tasks split into three batches at phase boundaries: Phase 1 (4), Phase 2 (7), Phase 3 (1). That is more than one batch, so Execute offers sub-agents before any worker starts. If the offer is declined, Execute runs inline.

---

## Task Granularity Check

| Task | Scope | Status |
| --- | --- | --- |
| T1: Declare runtime dependencies | 1 file | ✅ Granular |
| T2: Ignore the Neon credential file | 1 file | ✅ Granular |
| T3: Add a credential placeholder | 1 file | ✅ Granular |
| T4: Open Neon and create the tarefas table | 1 module | ✅ Granular |
| T5: Create a task | 1 endpoint; tests co-located in `tests/test_tarefas.py` | ✅ Granular |
| T6: List tasks | 1 endpoint | ✅ Granular |
| T7: Get one task | 1 endpoint | ✅ Granular |
| T8: Replace title and description | 1 endpoint | ✅ Granular |
| T9: Change status | 1 endpoint | ✅ Granular |
| T10: Delete a task | 1 endpoint | ✅ Granular |
| T11: Map a dead database to 503 | 1 failure path | ✅ Granular |
| T12: Document how to run the API | 1 file | ✅ Granular |

---

## Diagram-Definition Cross-Check

| Task | Depends On (task body) | Diagram Shows | Status |
| --- | --- | --- | --- |
| T1 | None | no incoming arrow | ✅ Match |
| T2 | None | no incoming arrow | ✅ Match |
| T3 | None | no incoming arrow | ✅ Match |
| T4 | T1 | T1 → T4 | ✅ Match |
| T5 | T4 | cross-phase, not drawn inside Phase 2 | ✅ Match |
| T6 | T5 | T5 → T6 | ✅ Match |
| T7 | T6 | T6 → T7 | ✅ Match |
| T8 | T7 | T7 → T8 | ✅ Match |
| T9 | T8 | T8 → T9 | ✅ Match |
| T10 | T9 | T9 → T10 | ✅ Match |
| T11 | T10 | T10 → T11 | ✅ Match |
| T12 | T11 | cross-phase, not drawn inside Phase 3 | ✅ Match |

---

## Test Co-location Validation

| Task | Code Layer Created/Modified | Matrix Requires | Task Says | Status |
| --- | --- | --- | --- | --- |
| T1: Declare runtime dependencies | Config | none | none | ✅ OK |
| T2: Ignore the Neon credential file | Config | none | none | ✅ OK |
| T3: Add a credential placeholder | Config | none | none | ✅ OK |
| T4: Open Neon and create the tarefas table | Schema / connection | none | none | ✅ OK |
| T5: Create a task | Route | integration | integration | ✅ OK |
| T6: List tasks | Route | integration | integration | ✅ OK |
| T7: Get one task | Route | integration | integration | ✅ OK |
| T8: Replace title and description | Route | integration | integration | ✅ OK |
| T9: Change status | Route | integration | integration | ✅ OK |
| T10: Delete a task | Route | integration | integration | ✅ OK |
| T11: Map a dead database to 503 | Route | integration | integration | ✅ OK |
| T12: Document how to run the API | Docs | none | none | ✅ OK |

from contextlib import asynccontextmanager

import psycopg
from fastapi import FastAPI
from fastapi.responses import JSONResponse

import db
from migrations import apply
from routes.tasks import router

_schema_ready = False


@asynccontextmanager
async def lifespan(_app):
    global _schema_ready
    if not _schema_ready:
        try:
            connection = db.connect()
        except psycopg.Error:
            pass
        else:
            try:
                apply(connection)
            finally:
                connection.close()
            _schema_ready = True
    yield


app = FastAPI(lifespan=lifespan)
app.include_router(router)


@app.exception_handler(db.DatabaseUnavailable)
def database_unavailable(_request, _exc):
    return JSONResponse(
        status_code=503,
        content={"detail": "Database unavailable"},
    )

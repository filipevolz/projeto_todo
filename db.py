import os

import psycopg
from psycopg.rows import dict_row


class DatabaseUnavailable(Exception):
    pass


def connect():
    return psycopg.connect(os.environ["DATABASE_URL"])


def get_connection():
    try:
        connection = connect()
    except psycopg.Error as exc:
        raise DatabaseUnavailable from exc
    connection.row_factory = dict_row
    try:
        yield connection
        connection.commit()
    except psycopg.Error as exc:
        connection.rollback()
        raise DatabaseUnavailable from exc
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()

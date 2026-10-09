from models.task import Task

COLUMNS = "id, title, description, status, created_at, updated_at"


def to_task(row):
    return Task(
        id=row["id"],
        title=row["title"],
        description=row["description"],
        status=row["status"],
        created_at=row["created_at"],
        updated_at=row["updated_at"],
    )


class TaskRepository:
    def __init__(self, connection):
        self.connection = connection

    def insert(self, title, description):
        cursor = self.connection.execute(
            f"""
            INSERT INTO tasks (title, description)
            VALUES (%s, %s)
            RETURNING {COLUMNS}
            """,
            (title, description),
        )
        row = cursor.fetchone()
        cursor.close()
        return to_task(row)

    def list_all(self):
        cursor = self.connection.execute(
            f"""
            SELECT {COLUMNS}
            FROM tasks
            ORDER BY id ASC
            """
        )
        rows = cursor.fetchall()
        cursor.close()
        return [to_task(row) for row in rows]

    def find_by_id(self, task_id):
        cursor = self.connection.execute(
            f"""
            SELECT {COLUMNS}
            FROM tasks
            WHERE id = %s
            """,
            (task_id,),
        )
        row = cursor.fetchone()
        cursor.close()
        if row is None:
            return None
        return to_task(row)

    def update(self, task_id, title, description):
        cursor = self.connection.execute(
            f"""
            UPDATE tasks
            SET title = %s,
                description = %s,
                updated_at = clock_timestamp()
            WHERE id = %s
            RETURNING {COLUMNS}
            """,
            (title, description, task_id),
        )
        row = cursor.fetchone()
        cursor.close()
        if row is None:
            return None
        return to_task(row)

    def update_status(self, task_id, status):
        cursor = self.connection.execute(
            f"""
            UPDATE tasks
            SET status = %s,
                updated_at = clock_timestamp()
            WHERE id = %s
            RETURNING {COLUMNS}
            """,
            (status, task_id),
        )
        row = cursor.fetchone()
        cursor.close()
        if row is None:
            return None
        return to_task(row)

    def delete(self, task_id):
        cursor = self.connection.execute(
            """
            DELETE FROM tasks
            WHERE id = %s
            RETURNING title
            """,
            (task_id,),
        )
        row = cursor.fetchone()
        cursor.close()
        if row is None:
            return None
        return row["title"]

DO $$
BEGIN
    IF to_regclass('public.tarefas') IS NOT NULL
       AND to_regclass('public.tasks') IS NULL THEN
        ALTER TABLE tarefas RENAME TO tasks;
    END IF;
END $$;

CREATE TABLE IF NOT EXISTS tasks (
    id serial PRIMARY KEY,
    title text NOT NULL,
    description text NOT NULL DEFAULT '',
    status text NOT NULL DEFAULT 'pending'
        CHECK (status IN ('pending', 'completed')),
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now()
);

ALTER TABLE tasks DROP CONSTRAINT IF EXISTS tarefas_status_check;
ALTER TABLE tasks DROP CONSTRAINT IF EXISTS tasks_status_check;
UPDATE tasks SET status = 'pending' WHERE status = 'pendente';
UPDATE tasks SET status = 'completed' WHERE status = 'concluido';
ALTER TABLE tasks ALTER COLUMN status SET DEFAULT 'pending';
ALTER TABLE tasks
    ADD CONSTRAINT tasks_status_check
    CHECK (status IN ('pending', 'completed'));

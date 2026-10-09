class TaskNotFound(Exception):
    def __init__(self, task_id):
        self.task_id = task_id


class TaskService:
    def __init__(self, repository):
        self.repository = repository

    def create(self, title, description):
        return self.repository.insert(title, description)

    def list_all(self):
        return self.repository.list_all()

    def get(self, task_id):
        task = self.repository.find_by_id(task_id)
        if task is None:
            raise TaskNotFound(task_id)
        return task

    def update(self, task_id, title, description):
        task = self.repository.update(task_id, title, description)
        if task is None:
            raise TaskNotFound(task_id)
        return task

    def change_status(self, task_id, status):
        task = self.repository.update_status(task_id, status)
        if task is None:
            raise TaskNotFound(task_id)
        return task

    def remove(self, task_id):
        title = self.repository.delete(task_id)
        if title is None:
            raise TaskNotFound(task_id)
        return title

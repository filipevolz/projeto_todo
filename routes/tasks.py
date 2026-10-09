from fastapi import APIRouter, Depends, HTTPException

from db import get_connection
from repositories.task_repository import TaskRepository
from schemas.task import MessageOut, StatusBody, TaskCreate, TaskOut, TaskReplace
from services.task_service import TaskNotFound, TaskService

router = APIRouter()


def get_service(connection=Depends(get_connection)):
    return TaskService(TaskRepository(connection))


def not_found(task_id):
    raise HTTPException(status_code=404, detail=f"Task {task_id} was not found")


@router.post("/tasks", status_code=201, response_model=TaskOut)
def create_task(body: TaskCreate, service: TaskService = Depends(get_service)):
    task = service.create(body.title, body.description)
    return TaskOut.from_model(task)


@router.get("/tasks", response_model=list[TaskOut])
def list_tasks(service: TaskService = Depends(get_service)):
    return [TaskOut.from_model(task) for task in service.list_all()]


@router.get("/tasks/{task_id}", response_model=TaskOut)
def get_task(task_id: int, service: TaskService = Depends(get_service)):
    try:
        task = service.get(task_id)
    except TaskNotFound:
        not_found(task_id)
    return TaskOut.from_model(task)


@router.put("/tasks/{task_id}", response_model=TaskOut)
def replace_task(
    task_id: int,
    body: TaskReplace,
    service: TaskService = Depends(get_service),
):
    try:
        task = service.update(task_id, body.title, body.description)
    except TaskNotFound:
        not_found(task_id)
    return TaskOut.from_model(task)


@router.patch("/tasks/{task_id}/status", response_model=TaskOut)
def change_status(
    task_id: int,
    body: StatusBody,
    service: TaskService = Depends(get_service),
):
    try:
        task = service.change_status(task_id, body.status)
    except TaskNotFound:
        not_found(task_id)
    return TaskOut.from_model(task)


@router.delete("/tasks/{task_id}", response_model=MessageOut)
def delete_task(task_id: int, service: TaskService = Depends(get_service)):
    try:
        title = service.remove(task_id)
    except TaskNotFound:
        not_found(task_id)
    return MessageOut(message=f"Task {title} was removed successfully!")

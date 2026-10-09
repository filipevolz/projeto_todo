from typing import Literal

from pydantic import BaseModel, Field, field_validator

from models.task import Task


def reject_blank_title(value):
    if value.strip() == "":
        raise ValueError("title must not be blank")
    return value


class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str = Field(default="", max_length=2000)

    @field_validator("title")
    @classmethod
    def title_not_whitespace(cls, value):
        return reject_blank_title(value)


class TaskReplace(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str = Field(max_length=2000)

    @field_validator("title")
    @classmethod
    def title_not_whitespace(cls, value):
        return reject_blank_title(value)


class StatusBody(BaseModel):
    status: Literal["pending", "completed"]


class TaskOut(BaseModel):
    id: int
    title: str
    description: str
    status: str
    created_at: str
    updated_at: str

    @classmethod
    def from_model(cls, task: Task):
        return cls(
            id=task.id,
            title=task.title,
            description=task.description,
            status=task.status,
            created_at=task.created_at.isoformat(),
            updated_at=task.updated_at.isoformat(),
        )


class MessageOut(BaseModel):
    message: str

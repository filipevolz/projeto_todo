from dataclasses import dataclass
from datetime import datetime


@dataclass
class Task:
    id: int
    title: str
    description: str
    status: str
    created_at: datetime
    updated_at: datetime

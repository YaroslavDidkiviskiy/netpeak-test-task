from enum import Enum

from pydantic import BaseModel, Field


class Category(str, Enum):
    automation = "автоматизація"
    integration = "інтеграція"
    report = "звіт/аналітика"
    support = "баг/підтримка"
    consultation = "питання/консультація"
    out_of_scope = "поза скоупом"


class Priority(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"


class ClassifiedRequest(BaseModel):
    id: str
    channel: str
    timestamp: str
    raw_text: str
    category: Category
    target_department: str | None = Field(None)
    priority: Priority
    short_summary: str
    requested_actions: list[str] = Field(default_factory=list)
    needs_clarification: bool


class Stats(BaseModel):
    total: int
    by_category: dict[str, int]
    by_priority: dict[str, int]
    by_department: dict[str, int]
    needs_clarification: list[str]


class ClassifyResponse(BaseModel):
    results: list[ClassifiedRequest]
    stats: Stats

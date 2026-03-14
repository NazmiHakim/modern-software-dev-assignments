from datetime import datetime
from pydantic import BaseModel, Field


class ActionItemRead(BaseModel):
    id: int
    description: str
    completed: bool
    note_id: int | None = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class NoteRead(BaseModel):
    id: int
    title: str
    content: str
    created_at: datetime
    updated_at: datetime
    action_items: list[ActionItemRead] = []

    class Config:
        from_attributes = True


class NoteCreate(BaseModel):
    title: str = Field(..., min_length=3, max_length=200)
    content: str = Field(..., min_length=3)


class NotePatch(BaseModel):
    title: str | None = Field(None, min_length=3, max_length=200)
    content: str | None = Field(None, min_length=3)


class ActionItemCreate(BaseModel):
    description: str = Field(..., min_length=3)
    note_id: int | None = None


class ActionItemPatch(BaseModel):
    description: str | None = Field(None, min_length=3)
    completed: bool | None = None
    note_id: int | None = None



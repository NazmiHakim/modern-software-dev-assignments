from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel


class NoteBase(BaseModel):
    content: str


class NoteCreate(NoteBase):
    pass


class Note(NoteBase):
    id: int
    created_at: str


class ActionItemsExtractRequest(BaseModel):
    text: str
    save_note: bool = False


class ActionItemExtracted(BaseModel):
    id: int
    text: str


class ActionItemsExtractResponse(BaseModel):
    note_id: Optional[int]
    items: List[ActionItemExtracted]


class ActionItemBase(BaseModel):
    text: str


class ActionItem(ActionItemBase):
    id: int
    note_id: Optional[int]
    done: bool
    created_at: str


class ActionItemDoneRequest(BaseModel):
    done: bool = True


class ActionItemDoneResponse(BaseModel):
    id: int
    done: bool


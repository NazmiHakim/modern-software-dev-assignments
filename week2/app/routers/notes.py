from __future__ import annotations

from typing import List

from fastapi import APIRouter, HTTPException

from .. import db
from ..schemas import Note, NoteCreate


router = APIRouter(prefix="/notes", tags=["notes"])


@router.post("", response_model=Note, status_code=201)
def create_note(payload: NoteCreate) -> Note:
    content = payload.content.strip()
    if not content:
        raise HTTPException(status_code=400, detail="content is required")

    note_id = db.insert_note(content)
    note = db.get_note(note_id)
    if note is None:
        # This should not normally happen, but guard against inconsistent state.
        raise HTTPException(status_code=500, detail="failed to retrieve created note")

    return Note(
        id=note["id"],
        content=note["content"],
        created_at=note["created_at"] or "",
    )


@router.get("/{note_id}", response_model=Note)
def get_single_note(note_id: int) -> Note:
    row = db.get_note(note_id)
    if row is None:
        raise HTTPException(status_code=404, detail="note not found")
    return Note(
        id=row["id"],
        content=row["content"],
        created_at=row["created_at"] or "",
    )


@router.get("", response_model=List[Note])
def list_notes() -> List[Note]:
    rows = db.list_notes()
    return [
        Note(
            id=r["id"],
            content=r["content"],
            created_at=r["created_at"] or "",
        )
        for r in rows
    ]



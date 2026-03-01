from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, HTTPException

from .. import db
from ..schemas import (
    ActionItem,
    ActionItemDoneRequest,
    ActionItemDoneResponse,
    ActionItemExtracted,
    ActionItemsExtractRequest,
    ActionItemsExtractResponse,
)
from ..services.extract import extract_action_items, extract_action_items_llm


router = APIRouter(prefix="/action-items", tags=["action-items"])


@router.post("/extract", response_model=ActionItemsExtractResponse)
def extract(payload: ActionItemsExtractRequest) -> ActionItemsExtractResponse:
    text = payload.text.strip()
    if not text:
        raise HTTPException(status_code=400, detail="text is required")

    note_id: Optional[int] = None
    if payload.save_note:
        note_id = db.insert_note(text)

    items = extract_action_items(text)
    ids = db.insert_action_items(items, note_id=note_id)
    extracted_items: List[ActionItemExtracted] = [
        ActionItemExtracted(id=i, text=t) for i, t in zip(ids, items)
    ]
    return ActionItemsExtractResponse(note_id=note_id, items=extracted_items)


@router.post("/extract-llm", response_model=ActionItemsExtractResponse)
def extract_llm(payload: ActionItemsExtractRequest) -> ActionItemsExtractResponse:
    text = payload.text.strip()
    if not text:
        raise HTTPException(status_code=400, detail="text is required")

    note_id: Optional[int] = None
    if payload.save_note:
        note_id = db.insert_note(text)

    items = extract_action_items_llm(text)
    ids = db.insert_action_items(items, note_id=note_id)
    extracted_items: List[ActionItemExtracted] = [
        ActionItemExtracted(id=i, text=t) for i, t in zip(ids, items)
    ]
    return ActionItemsExtractResponse(note_id=note_id, items=extracted_items)


@router.get("", response_model=List[ActionItem])
def list_all(note_id: Optional[int] = None) -> List[ActionItem]:
    rows = db.list_action_items(note_id=note_id)
    return [
        ActionItem(
            id=r["id"],
            note_id=r["note_id"],
            text=r["text"],
            done=bool(r["done"]),
            created_at=r["created_at"],
        )
        for r in rows
    ]


@router.post(
    "/{action_item_id}/done",
    response_model=ActionItemDoneResponse,
)
def mark_done(action_item_id: int, payload: ActionItemDoneRequest) -> ActionItemDoneResponse:
    done = payload.done
    updated = db.mark_action_item_done(action_item_id, done)
    if not updated:
        raise HTTPException(status_code=404, detail="action item not found")
    return ActionItemDoneResponse(id=action_item_id, done=done)



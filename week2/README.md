## Week 2 – Action Item Extractor

This project is a small FastAPI + SQLite application that converts free‑form notes into structured action items.  
It demonstrates:

- **Backend**: FastAPI app (`app/main.py`) with routers for notes and action items, a lightweight SQLite database layer (`app/db.py`), and extraction logic (`app/services/extract.py`) using both heuristics and an LLM (Gemini).
- **Frontend**: Minimal vanilla HTML/JS UI in `frontend/index.html` for submitting notes, extracting action items, toggling completion, and listing saved notes.
- **Tests**: Pytest suite in `tests/test_extract.py` covering heuristic and LLM-based extraction.

High-level architecture:

- `app/main.py` – Creates the FastAPI app, initializes the database, serves the HTML frontend, and mounts static assets.
- `app/db.py` – Handles all SQLite access (notes and action_items tables).
- `app/schemas.py` – Pydantic models for requests and responses.
- `app/services/extract.py` – Text processing and LLM-powered extraction.
- `app/routers/notes.py` – Endpoints to create and fetch notes.
- `app/routers/action_items.py` – Endpoints to extract and manage action items.
- `frontend/index.html` – Browser UI for interacting with the API.

---

## Environment Setup

These instructions assume you are working from the **project root** (`modern-software-dev-assignments`), not inside `week2/`.

### 1. Create / activate the conda environment

If you are following the course conventions:

```bash
conda create -n cs146s python=3.11  # if you have not created it yet
conda activate cs146s
```

### 2. Install project dependencies with Poetry

From the project root (where `pyproject.toml` lives):

```bash
cd modern-software-dev-assignments
poetry install
```

This will install the shared dependencies for all weeks, including FastAPI, Uvicorn, and the extraction libraries.

### 3. Configure environment variables

The LLM-powered extractor uses Google Gemini. You must provide an API key via environment variable:

```bash
export GOOGLE_API_KEY="your-gemini-api-key"    # macOS / Linux
set GOOGLE_API_KEY=your-gemini-api-key        # Windows (PowerShell / cmd)
```

Alternatively, you can store it in a `.env` file at the project root:

```text
GOOGLE_API_KEY=your-gemini-api-key
```

The backend will automatically load this via `python-dotenv`.

---

## Running the FastAPI Server (with Poetry)

From the project root (`modern-software-dev-assignments`), with your conda environment active:

```bash
poetry run uvicorn week2.app.main:app --reload
```

Then open your browser at:

- `http://127.0.0.1:8000/` – Main UI (served by the `/` route).
- `http://127.0.0.1:8000/docs` – Interactive Swagger UI for all API endpoints.

Static frontend assets are served from `week2/frontend`.

---

## API Endpoints

All endpoints are rooted at `http://127.0.0.1:8000/`.

### Root

- **GET `/`**
  - **Description**: Serves the `frontend/index.html` page.
  - **Response**: HTML.

---

### Notes API (`/notes`)

#### Create a note

- **POST `/notes`**
- **Request body** (`application/json`):

  ```json
  {
    "content": "Meeting notes go here..."
  }
  ```

- **Response** (`200`/`201`), schema `Note`:

  ```json
  {
    "id": 1,
    "content": "Meeting notes go here...",
    "created_at": "2024-01-01T12:34:56"
  }
  ```

- **Error responses**:
  - `400` – if `content` is empty or only whitespace.

#### Get a single note

- **GET `/notes/{note_id}`**
  - **Path params**: `note_id` (integer).
  - **Response**: `Note` as above.
  - **Errors**:
    - `404` – if the note does not exist.

#### List all notes

- **GET `/notes`**
  - **Description**: Returns all notes, most recent first.
  - **Response**: `List[Note]`:

  ```json
  [
    {
      "id": 2,
      "content": "Another note",
      "created_at": "2024-01-02T09:00:00"
    },
    {
      "id": 1,
      "content": "First note",
      "created_at": "2024-01-01T12:34:56"
    }
  ]
  ```

---

### Action Items API (`/action-items`)

#### Extract (heuristic)

- **POST `/action-items/extract`**
- **Description**: Uses the heuristic extractor (`extract_action_items`) to parse notes and insert action items into the database.
- **Request body** (`ActionItemsExtractRequest`):

  ```json
  {
    "text": "Notes with bullets and todos...",
    "save_note": true
  }
  ```

  - `text` – free‑form notes.
  - `save_note` (optional, default `false`) – if `true`, the raw note is also stored in the `notes` table.

- **Response** (`ActionItemsExtractResponse`):

  ```json
  {
    "note_id": 1,
    "items": [
      { "id": 10, "text": "Set up database" },
      { "id": 11, "text": "Implement extract endpoint" }
    ]
  }
  ```

- **Error responses**:
  - `400` – if `text` is empty or whitespace.

#### Extract (LLM / Gemini)

- **POST `/action-items/extract-llm`**
- **Description**: Uses the LLM-powered extractor (`extract_action_items_llm`) backed by Gemini 1.5 Pro to identify action items.
- **Request body**: same `ActionItemsExtractRequest` as the heuristic endpoint.
- **Response**: same shape as `/action-items/extract` (`ActionItemsExtractResponse`).
- **Error responses**:
  - `400` – if `text` is empty or whitespace.
  - `500` (runtime) – if the LLM fails or `GOOGLE_API_KEY` is not set (raised in `extract_action_items_llm`).

#### List all action items

- **GET `/action-items`**
  - **Query params (optional)**:
    - `note_id` (int) – if provided, filters action items belonging to that note.
  - **Response**: `List[ActionItem]`:

  ```json
  [
    {
      "id": 10,
      "note_id": 1,
      "text": "Set up database",
      "done": false,
      "created_at": "2024-01-01T12:35:00"
    }
  ]
  ```

#### Mark an action item as done/undone

- **POST `/action-items/{action_item_id}/done`**
  - **Path params**: `action_item_id` (integer).
  - **Request body** (`ActionItemDoneRequest`):

    ```json
    {
      "done": true
    }
    ```

    - `done` defaults to `true` when omitted.

  - **Response** (`ActionItemDoneResponse`):

    ```json
    {
      "id": 10,
      "done": true
    }
    ```

  - **Error responses**:
    - `404` – if the action item does not exist.

---

## Frontend Usage (Browser UI)

When you open `http://127.0.0.1:8000/`, you see a simple page with:

- A **textarea** for notes.
- A **Save as note** checkbox.
- Buttons:
  - **Extract** – calls `POST /action-items/extract`.
  - **Extract LLM** – calls `POST /action-items/extract-llm`.
  - **List Notes** – calls `GET /notes` and renders the results under the extraction area.

Extracted items appear with checkboxes; toggling a checkbox sends `POST /action-items/{id}/done` to mark the item as done/undone.

---

## Running Tests with Pytest

From the project root (`modern-software-dev-assignments`), with your environment activated:

```bash
poetry run pytest week2/tests/test_extract.py -v
```

Or, to run all tests for the project:

```bash
poetry run pytest -v
```

The tests in `week2/tests/test_extract.py` cover:

- Heuristic extraction (`extract_action_items`).
- LLM extraction (`extract_action_items_llm`), with the Gemini API mocked via `unittest.mock.patch` so tests run quickly without real network calls.


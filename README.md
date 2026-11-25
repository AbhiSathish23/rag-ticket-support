# RAG Ticket Support — IT Support Assistant

A small **Retrieval-Augmented Generation (RAG)** API that helps answer IT support questions by finding similar past tickets and using Google Gemini to generate helpful responses.

## Overview

This service stores IT support tickets (problem + solution pairs) in a local vector database. When a user asks a new question:

1. The query is embedded with **Gemini Embeddings** (`gemini-embedding-001`).
2. **ChromaDB** retrieves the **top 3** most similar past tickets by semantic similarity.
3. If the best match is too distant (distance > `0.75`), the API returns `"No relevant past ticket found"` without calling the LLM.
4. Otherwise, **Gemini** (`gemini-2.5-flash`) generates a concise, point-wise answer from those matched tickets.

On first startup, the database is automatically seeded with sample IT tickets if it is empty.

## Tech Stack

| Component | Purpose |
|-----------|---------|
| [FastAPI](https://fastapi.tiangolo.com/) | REST API |
| [ChromaDB](https://www.trychroma.com/) | Persistent vector store (`./chroma.db`) |
| [Google GenAI](https://ai.google.dev/) | Embeddings + text generation |
| [python-dotenv](https://pypi.org/project/python-dotenv/) | Environment variable loading |
| [Uvicorn](https://www.uvicorn.org/) | ASGI server |

## Prerequisites

- Python 3.10+
- A [Google AI API key](https://aistudio.google.com/apikey) with access to Gemini models

## Installation

1. Clone or download this repository.

2. Create and activate a virtual environment:

   ```bash
   python -m venv .venv
   source .venv/bin/activate   # macOS/Linux
   # .venv\Scripts\activate    # Windows
   ```

3. Install dependencies:

   ```bash
   pip install fastapi uvicorn chromadb google-genai python-dotenv
   ```

4. Create a `.env` file in the project root:

   ```env
   GEMINI_API_KEY=your_api_key_here
   ```

## Running the Server

Start the API with Uvicorn:

```bash
uvicorn ticket_support:app --reload
```

The server runs at `http://127.0.0.1:8000` by default.

Interactive API docs are available at:

- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

## API Endpoints

### `GET /health`

Check that the service is running and see how many tickets are stored.

**Response example:**

```json
{
  "status": "running",
  "tickets_in_db": 5
}
```

### `POST /ask`

Ask a support question. The service finds the top 3 closest past tickets and returns an AI-generated answer (or a no-match message if similarity is too low).

**Request body:**

```json
{
  "query": "My computer screen keeps flashing"
}
```

**Response example (match found):**

```json
{
  "query": "My computer screen keeps flashing",
  "similar_past_ticket": [
    "Screen is flickering badly",
    "My laptop won't turn on",
    "Keyboard keys are not working"
  ],
  "past_solution": [
    {"solution": "Update display drivers, check monitor cable connection"},
    {"solution": "Check power adapter, try removing battery and replugging"},
    {"solution": "Clean keyboard, check USB connection or replace batteries"}
  ],
  "ai_answer": "..."
}
```

**Response example (no relevant match, distance > 0.75):**

```json
{
  "query": "How do I bake a cake?",
  "similar_past_ticket": ["...", "...", "..."],
  "past_solution": [{"solution": "..."}, {"solution": "..."}, {"solution": "..."}],
  "ai_answer": "No relevant past ticket found"
}
```

**cURL example:**

```bash
curl -X POST "http://127.0.0.1:8000/ask" \
  -H "Content-Type: application/json" \
  -d '{"query": "My computer screen keeps flashing"}'
```

### `POST /add-ticket`

Add a new ticket to the knowledge base.

**Parameters:**

| Name | Type | Location | Description |
|------|------|----------|-------------|
| `query` | string | body | The problem description |
| `solution` | string | query param | The resolution for that problem |

**Request example:**

```bash
curl -X POST "http://127.0.0.1:8000/add-ticket?solution=Restart%20the%20print%20spooler%20service" \
  -H "Content-Type: application/json" \
  -d '{"query": "Printer is not responding"}'
```

**Response example:**

```json
{
  "message": "Ticket added!",
  "id": "5"
}
```

## Seed Data

If the ChromaDB collection is empty on startup, these sample tickets are loaded automatically:

| Problem | Solution |
|---------|----------|
| My laptop won't turn on | Check power adapter, try removing battery and replugging |
| Internet connection keeps dropping | Restart router, update network drivers |
| Cannot login to my account | Reset password, clear browser cache and cookies |
| Screen is flickering badly | Update display drivers, check monitor cable connection |
| Keyboard keys are not working | Clean keyboard, check USB connection or replace batteries |

## How It Works

```
User query
    │
    ▼
Gemini Embedding (gemini-embedding-001)
    │
    ▼
ChromaDB similarity search (top 3 matches)
    │
    ▼
Distance check (best match > 0.75? → no relevant ticket)
    │
    ▼
Gemini generation (gemini-2.5-flash)
    │
    ▼
Structured JSON response
```

## Project Structure

```
RAG_TICKET_SUPPORT/
├── ticket_support.py   # FastAPI app, embeddings, seeding, and endpoints
├── chroma.db/          # ChromaDB persistent storage (created at runtime)
├── .env                # API keys (not committed to version control)
└── README.md
```

## Evaluation

Labels were first drafted from system output, then revised after reviewing ticket text. The test set is small (6 queries + 2 no-match), so scores are directional.

## Notes

- Embeddings are generated from the **problem** text; solutions are stored as metadata.
- `/ask` retrieves up to **3** similar tickets and uses all of them as context for generation.
- If the closest ticket’s distance is greater than **0.75**, Gemini is skipped and `ai_answer` is `"No relevant past ticket found"`.
- The vector database persists in `./chroma.db`. Delete this folder to reset and re-seed tickets.
- Keep your `GEMINI_API_KEY` private and never commit `.env` to source control.

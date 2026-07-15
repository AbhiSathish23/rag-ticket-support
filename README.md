# RAG Tickets — IT Support Assistant

A small **Retrieval-Augmented Generation (RAG)** API that helps answer IT support questions by finding similar past tickets and using Google Gemini to generate helpful responses.

## Overview

This service stores IT support tickets (problem + solution pairs) in a local vector database. When a user asks a new question:

1. The query is embedded with **Gemini Embeddings** (`gemini-embedding-001`).
2. **ChromaDB** retrieves the most similar past ticket by semantic similarity.
3. **Gemini** (`gemini-2.5-flash`) generates a concise, point-wise answer based on the matched ticket.

On first startup, the database is automatically seeded with sample IT tickets if it is empty.

## Tech Stack

| Component | Purpose |
|-----------|---------|
| [FastAPI](https://fastapi.tiangolo.com/) | REST API |
| [ChromaDB](https://www.trychroma.com/) | Persistent vector store (`./chroma.db`) |
| [Google GenAI](https://ai.google.dev/) | Embeddings + text generation |
| [python-dotenv](https://pypi.org/project/python-dotenv/) | Environment variable loading |

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
uvicorn RAG_Tickets:app --reload
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

Ask a support question. The service finds the closest matching past ticket and returns an AI-generated answer.

**Request body:**

```json
{
  "query": "My computer screen keeps flashing"
}
```

**Response example:**

```json
{
  "query": "My computer screen keeps flashing",
  "similar_past_ticket": "Screen is flickering badly",
  "past_solution": "Update display drivers, check monitor cable connection",
  "ai_answer": "..."
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
ChromaDB similarity search (top 1 match)
    │
    ▼
Gemini generation (gemini-2.5-flash)
    │
    ▼
Structured JSON response
```

## Project Structure

```
RAG/
├── RAG_Tickets.py   # FastAPI app, embeddings, and endpoints
├── chroma.db/       # ChromaDB persistent storage (created at runtime)
├── .env             # API keys (not committed to version control)
└── README.md
```

## Notes

- Embeddings are generated from the **problem** text; solutions are stored as metadata.
- The vector database persists in `./chroma.db`. Delete this folder to reset and re-seed tickets.
- Keep your `GEMINI_API_KEY` private and never commit `.env` to source control.


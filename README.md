# Helpdesk Ticket Viewer

## Quick Start

```bash
cp .env.example .env  # edit with your credentials
docker compose up --build
```

- Frontend: http://localhost:5173
- Backend API: http://localhost:8000/docs


## Discussion Questions

### 1. AI Dev Stack

Claude Code (Claude Opus 4.6) was used throughout the assignment as an interactive coding assistant. It helped scaffold the project structure, and iterate on implementation details.Architectural decisions and code review were done manually.

### 2. API Discovery

To find the model name, I queried the OpenAI-compatible `/v1/models` endpoint:

```bash
curl -s https://llm-test-api.projects.agentica.studio/v1/models \
  -H "Authorization: Bearer agentica-test-API"
```

The response returned a single model: `unsloth/Qwen3.5-9B`. 

### 3. Streaming Architecture

The data flow:

```
Frontend (EventSource) <-- SSE --> Backend (FastAPI) <-- HTTP stream --> LLM API
```

1. Frontend opens an `EventSource` connection to `GET /api/tickets/{id}/summary`
2. Backend creates a streaming chat completion request to the LLM API via the OpenAI client
3. As each token chunk arrives from the LLM, the backend yields it as an SSE `message` event
4. When the stream completes, backend sends an SSE `done` event
5. Frontend listens for `message` events (appends text) and `done` (closes connection)

**Error handling:**
- A 30-second TTFT (time to first token) timeout wraps the initial LLM request + first chunk. If the LLM is slow to respond, the timeout fires and an SSE `error` event is sent to the frontend with a clear message.
- If the LLM drops mid-stream or any other exception occurs, it's caught, logged with full traceback on the backend, and a generic "An unexpected error occurred" SSE `error` event is sent to the frontend (no internal details leaked).
- The frontend displays error messages and resets its loading state on any error event or connection loss.

### 4. Database

Schema is minimal - a single `tickets` table:

| Column | Type | Notes |
|---|---|---|
| id | INTEGER | Primary key, auto-increment |
| title | VARCHAR(255) | |
| description | TEXT | |
| status | VARCHAR(20) | Validated as StrEnum at application level (`open`, `in_progress`, `resolved`) |
| created_at | TIMESTAMPTZ | Server default `now()` |

Status is stored as a plain string rather than a PostgreSQL ENUM because my experience showed its a migration pain - until now I have been doing app-level validations for enums per team's desicions. 

**For thousands of tickets with full-text search:** Add a GIN index on a `tsvector` column generated from `title` and `description`. I believe thousands is a good scale for postgresql to handle. Add cursor-based pagination. Add indexes on `status` and `created_at` for filtered queries.

### 5. Credentials

All credentials (database URL, LLM API key) are passed as environment variables via Docker Compose's `env_file` directive, read from a `.env` file that is gitignored. The application code reads them through `pydantic-settings`.

**In production:** Use a secrets manager (AWS Secrets Manager, HashiCorp Vault) or platform-native secrets (Kubernetes Secrets). Never store credentials in code or images. Rotate API keys regularly.

### 6. Tradeoffs

**Skipped/simplified:**
- No authentication/authorization
- No pagination on the ticket list
- No tests (unit or integration)
- No production-optimized frontend build (running Vite dev server in Docker)
- Minimal CSS - functional but not polished
- No caching of LLM summaries

**Would add first with 3 more hours:**
- Integration tests for the backend (pytest + httpx async client), automatic e2e testing.
- Production frontend build (multi-stage Dockerfile with nginx)
- Caching generated summaries in the database to avoid redundant LLM calls
- Pagination on the ticket list endpoint

### 7. Time Spent

3 hours, together with answering these questions and submitting the assignment. Backend architecture and dependency injection wiring took the most iteration - getting the layering right (stubs, session management, service/repo pattern) required several rounds of coding and reviewing. The frontend was straightforward. SSE streaming worked on first try but tuning the UX (loading dots, error states) took some time.
# langchain-doc-summarizer  
**FastAPI pipeline for LangChain doc ingestion & summarization**

---

## 1. Overview  
`langchain-doc-summarizer` is a lightweight, production‑ready API that ingests documents (PDF, DOCX, TXT, etc.), processes them with LangChain’s powerful retrieval and embedding tools, and returns concise summaries. The service can be used as a microservice inside larger applications or run locally for quick experimentation.

---

## 2. Features  
- **FastAPI backend** – Fast, async request handling with automatic OpenAPI docs.  
- **LangChain integration** – Uses LangChain’s loaders, embeddings, and chain logic.  
- **File ingestion pipeline** – Supports PDF, DOCX, TXT and CSV via `app/utils/file_handler.py`.  
- **Summarization service** – Generates summaries using a pre‑trained LLM (OpenAI/Anthropic) through `app/services/summarizer.py`.  
- **Asynchronous task queue** – Celery worker (`tasks/celery_worker.py`) for long‑running summarizations.  
- **Auth middleware** – Simple token‑based authentication in `middlewares/auth_middleware.py`.  
- **CLI helper** – `cli/cli.py` to seed data and run the server.  
- **Unit tests** – Tests for document processing and summarization logic.  

---

## 3. Tech Stack  
| Layer | Technology |
|-------|------------|
| API | FastAPI, Uvicorn |
| Background Jobs | Celery + Redis |
| LLM & Retrieval | LangChain (OpenAI / Anthropic) |
| Data Storage | Chroma DB (in‑memory by default) |
| Testing | Pytest |
| Packaging | Poetry |

---

## 4. Installation  

```bash
# Clone the repository
git clone https://github.com/yourorg/langchain-doc-summarizer.git
cd langchain-doc-summarizer

# Create virtual environment & install dependencies
poetry install

# Set required environment variables (example)
export OPENAI_API_KEY="sk-..."
export REDIS_URL="redis://localhost:6379"
```

---

## 5. Running the Service  

```bash
# Start Redis locally or point to an existing instance
docker run -p 6379:6379 redis

# Launch Celery worker (in a separate terminal)
poetry run celery -A tasks.celery_worker worker --loglevel=info

# Run FastAPI server
poetry run uvicorn app.main:app --reload
```

Open the Swagger UI at `http://localhost:8000/docs` to try out endpoints.

---

## 6. Usage Examples  

### Upload a Document & Get Summary (synchronous)

```bash
curl -X POST "http://localhost:8000/api/v1/summarize" \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -F "file=@/path/to/report.pdf"
```

Response:

```json
{
  "summary": "The report highlights key findings about market trends..."
}
```

### Upload a Document & Get Summary (asynchronous)

```bash
curl -X POST "http://localhost:8000/api/v1/summarize_async" \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -F "file=@/path/to/report.pdf"
```

Response:

```json
{
  "task_id": "123e4567-e89b-12d3-a456-426614174000",
  "status_url": "/api/v1/tasks/123e4567-e89b-12d3-a456-426614174000/status"
}
```

Poll the status endpoint until `completed`:

```bash
curl -X GET "http://localhost:8000/api/v1/tasks/123e4567-e89b-12d3-a456-426614174000/status" \
     -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 7. API Endpoints  

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/v1/summarize` | Upload file and receive immediate summary |
| POST | `/api/v1/summarize_async` | Upload file, returns task ID for background processing |
| GET  | `/api/v1/tasks/{task_id}/status` | Get status of async summarization |
| DELETE | `/api/v1/files/{file_id}` | Remove stored file and embeddings |

All endpoints require an `Authorization: Bearer <token>` header.

---

## 8. CLI Commands  

```bash
# Seed sample documents into the vector store
poetry run python cli/cli.py seed

# Run the API server (alias for uvicorn)
poetry run python cli/cli.py serve
```

See `cli/cli.py` for additional options.

---

## 9. References and Resources  

1. [GitHub - bosukeme/document-summarizer-langgraph](https://github.com/bosukeme/document-summarizer-langgraph)  
2. [Self Internet hosting RAG Purposes On Edge Units with Langchain](https://blog.goodlaptops.com/laptop-vision/self-internet-hosting-rag-purposes-on-edge-units-with-langchain/)  
3. [Building a RAG API with FastAPI – Analytics Vidhya](https://www.analyticsvidhya.com/blog/2026/03/building-a-rag-api-with-fastapi/)  
4. [Building an AI-Powered Document QA API with FastAPI and LangChain](https://ai.plainenglish.io/building-an-ai-powered-document-qa-api-with-fastapi-and-langchain-df743ec9c6da)  
5. [LangChain Overview – Docs by LangChain](https://docs.langchain.com/oss/python/langchain/overview)

---

## 10. Contributing  

1. Fork the repository and create a feature branch (`git checkout -b feature/<name>`).  
2. Run tests locally: `poetry run pytest`.  
3. Submit a pull request with clear description of changes.

All contributions must follow PEP‑8 coding style and include unit tests where applicable.

---

## 11. License  

MIT © 2026

---
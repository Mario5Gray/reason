# reason

Semantic code indexing with Tree-sitter + AST-like extraction.

## Dev quickstart
- Set `DATABASE_URL` (Postgres).
- Run migrations with Alembic.
- Start API: `uvicorn app.main:app --reload`.

## Endpoints
- `POST /ingest` ingest files
- `GET /query` query AST nodes
- `GET /files/{file_id}` get file metadata
- `GET /nodes/{node_id}` get AST node

# reason

Semantic code indexing with Tree-sitter + AST-like extraction.

## Dev quickstart
- Set `DATABASE_URL` (Postgres).
- Run migrations with Alembic.
- Start API: `uvicorn app.main:app --reload`.

## Endpoints
- `POST /ingest` ingest files
- `GET /query` query AST nodes (supports `kind`, `name`, `run_id`, `file_id`, `limit`)
- `GET /query/defs` query definitions (same filters)
- `GET /query/calls` query call sites (same filters)
- `GET /files/{file_id}` get file metadata
- `GET /nodes/{node_id}` get AST node
- `POST /source` get source slice by byte range

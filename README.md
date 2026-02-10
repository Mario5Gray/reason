# reason

Semantic code indexing with Tree-sitter + AST-like extraction, exposed over a small REST API.
This tutorial walks you from zero → ingest → query → source slices, using Docker.

---

## Configurable variables

These vary across installations and should be adjusted to your environment.

- `HOST_WORKSPACE`: the host path you want mounted into the container (default here: `/opt/workspace`).
- `/workspace` (container path): keep this stable; all ingest `root_path` and `files` should use this prefix.
- `DATABASE_URL`: connection string for Postgres (set in `docker-compose.yml`).

Update the volume mapping in `docker-compose.yml` if your host path differs:

```yaml
api:
  volumes:
    - /path/to/your/workspace:/workspace:rw
```

When calling `/ingest`, use the container path (`/workspace/...`), not the host path.

---

## 1) Start the stack

Build and run the services:

```bash
docker compose up -d --build
```

Run migrations:

```bash
docker compose exec api alembic upgrade head
```

---

## 2) Ingest code

The API ingests a list of files for a specific language. The container can see your host code under `/workspace`.

Example (Python):

```bash
curl -X POST 'http://localhost:8000/ingest' \
  -H 'Content-Type: application/json' \
  -d '{
    "language": "python",
    "root_path": "/workspace/Stability-Toys/server",
    "files": [
      "/workspace/Stability-Toys/server/run.py"
    ]
  }'
```

Response:

```json
{"run_id":7,"files_indexed":1}
```

---

## 3) Query nodes

### Raw node search

All function definitions:

```bash
curl 'http://localhost:8000/query?kind=function_definition&limit=50'
```

Filter by run:

```bash
curl 'http://localhost:8000/query?kind=function_definition&run_id=7'
```

Filter by file:

```bash
curl 'http://localhost:8000/query?kind=function_definition&file_id=12'
```

### Definitions shortcut

```bash
curl 'http://localhost:8000/query/defs?name=foo&run_id=7'
```

### Call sites shortcut

```bash
curl 'http://localhost:8000/query/calls?name=bar&run_id=7'
```

---

## 4) Inspect a node

```bash
curl 'http://localhost:8000/nodes/123'
```

Example response (shape):

```json
{
  "id": 123,
  "file_id": 12,
  "kind": "function_definition",
  "name": "baz",
  "parent_id": null,
  "start": [10, 0],
  "end": [12, 14],
  "start_byte": 120,
  "end_byte": 182,
  "meta": {"params": ["x"]}
}
```

---

## 5) Fetch source slices

```bash
curl -X POST 'http://localhost:8000/source' \
  -H 'Content-Type: application/json' \
  -d '{
    "path": "/workspace/Stability-Toys/server/run.py",
    "start_byte": 100,
    "end_byte": 220
  }'
```

Response:

```json
{
  "path": "/workspace/Stability-Toys/server/run.py",
  "start_byte": 100,
  "end_byte": 220,
  "text": "def baz(x):\n    return x + 1"
}
```

---

## 6) Run tests (containerized)

Tests run in a dedicated `test` service using a separate `reason_test` database.

```bash
scripts/build.sh --test
```

If you see `reason_test does not exist`, rebuild and re-run. The test service creates it automatically.

---

## 7) Notes on languages

`language` is required per ingest. Supported by tree-sitter in this repo:
- `python`
- `javascript`, `js`
- `jsx`
- `ts`, `tsx` (if supported by tree-sitter-languages)
- `css`, `scss`

The AST-like extractor currently captures:
- defs (functions/classes)
- calls
- imports (language-specific)
- CSS rules

---

## API Reference (quick)

- `POST /ingest` → `{ language, root_path, files[] }`
- `GET /query` → filters: `kind`, `name`, `run_id`, `file_id`, `limit`
- `GET /query/defs` → defs only, same filters
- `GET /query/calls` → call sites only, same filters
- `GET /files/{id}` → file metadata
- `GET /nodes/{id}` → node metadata
- `POST /source` → `{ path, start_byte, end_byte }`

---

## Common pitfalls

- **Paths must be container-visible.** Use `/workspace/...` (host path mounted in `docker-compose.yml`).
- **Test DB missing?** `scripts/build.sh --test` runs a setup step to create `reason_test`.
- **No results?** Check language, file path, and that ingestion succeeded.

---

If you want new extractors or additional node types, we can extend `app/ast_extract.py` and re-ingest.

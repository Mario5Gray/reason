from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from .db import SessionLocal
from .schemas import (
    IngestRequest,
    IngestResponse,
    QueryResponse,
    SourceSliceRequest,
    FileResponse,
    NodeResponse,
    SourceSliceResponse,
    RunListResponse,
    FileListResponse,
)
from .ingest import ingest_files
from .query import query_nodes, query_defs, query_calls, list_runs, list_run_files
from .models import AstNode, SourceFile
from .serializers import serialize_node_summary, serialize_node_detail, serialize_file, serialize_run

app = FastAPI(title="reason")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/ingest", response_model=IngestResponse)
def ingest(req: IngestRequest, db: Session = Depends(get_db)):
    run_id = ingest_files(db, req.language, req.files, req.root_path)
    return IngestResponse(run_id=run_id, files_indexed=len(req.files))


@app.get("/query", response_model=QueryResponse)
def query(
    kind: str | None = None,
    name: str | None = None,
    limit: int = 50,
    run_id: int | None = None,
    file_id: int | None = None,
    db: Session = Depends(get_db),
):
    nodes = query_nodes(db, kind=kind, name=name, limit=limit, run_id=run_id, file_id=file_id)
    return QueryResponse(results=[serialize_node_summary(n) for n in nodes])


@app.get("/files/{file_id}", response_model=FileResponse)
def get_file(file_id: int, db: Session = Depends(get_db)):
    file = db.get(SourceFile, file_id)
    if not file:
        raise HTTPException(status_code=404, detail="file not found")
    return FileResponse(**serialize_file(file))


@app.get("/nodes/{node_id}", response_model=NodeResponse)
def get_node(node_id: int, db: Session = Depends(get_db)):
    node = db.get(AstNode, node_id)
    if not node:
        raise HTTPException(status_code=404, detail="node not found")
    return NodeResponse(**serialize_node_detail(node))


@app.post("/source", response_model=SourceSliceResponse)
def get_source(req: SourceSliceRequest):
    with open(req.path, "rb") as f:
        f.seek(req.start_byte)
        data = f.read(max(0, req.end_byte - req.start_byte))
    text = data.decode("utf-8", errors="replace")
    return SourceSliceResponse(
        path=req.path,
        start_byte=req.start_byte,
        end_byte=req.end_byte,
        text=text,
    )


@app.get("/query/defs", response_model=QueryResponse)
def query_defs_endpoint(
    name: str | None = None,
    limit: int = 50,
    run_id: int | None = None,
    file_id: int | None = None,
    db: Session = Depends(get_db),
):
    nodes = query_defs(db, name=name, limit=limit, run_id=run_id, file_id=file_id)
    return QueryResponse(results=[serialize_node_summary(n) for n in nodes])


@app.get("/query/calls", response_model=QueryResponse)
def query_calls_endpoint(
    name: str | None = None,
    limit: int = 50,
    run_id: int | None = None,
    file_id: int | None = None,
    db: Session = Depends(get_db),
):
    nodes = query_calls(db, name=name, limit=limit, run_id=run_id, file_id=file_id)
    return QueryResponse(results=[serialize_node_summary(n) for n in nodes])


@app.get("/runs", response_model=RunListResponse)
def list_runs_endpoint(limit: int = 50, db: Session = Depends(get_db)):
    runs = list_runs(db, limit=limit)
    return RunListResponse(results=[serialize_run(r) for r in runs])


@app.get("/runs/{run_id}/files", response_model=FileListResponse)
def list_run_files_endpoint(run_id: int, limit: int = 200, db: Session = Depends(get_db)):
    files = list_run_files(db, run_id=run_id, limit=limit)
    return FileListResponse(results=[serialize_file(f) for f in files])

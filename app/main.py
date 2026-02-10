from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from .db import SessionLocal
from .schemas import IngestRequest, IngestResponse, QueryResponse, SourceSliceRequest, FileResponse, NodeResponse, SourceSliceResponse
from .ingest import ingest_files
from .query import query_nodes
from .models import AstNode, SourceFile

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
def query(kind: str | None = None, name: str | None = None, limit: int = 50, db: Session = Depends(get_db)):
    nodes = query_nodes(db, kind=kind, name=name, limit=limit)
    results = [
        {
            "id": n.id,
            "file_id": n.file_id,
            "kind": n.kind,
            "name": n.name,
            "start": [n.start_line, n.start_col],
            "end": [n.end_line, n.end_col],
        }
        for n in nodes
    ]
    return QueryResponse(results=results)


@app.get("/files/{file_id}", response_model=FileResponse)
def get_file(file_id: int, db: Session = Depends(get_db)):
    file = db.get(SourceFile, file_id)
    if not file:
        raise HTTPException(status_code=404, detail="file not found")
    return FileResponse(
        id=file.id,
        run_id=file.run_id,
        path=file.path,
        content_hash=file.content_hash,
        size_bytes=file.size_bytes,
    )


@app.get("/nodes/{node_id}", response_model=NodeResponse)
def get_node(node_id: int, db: Session = Depends(get_db)):
    node = db.get(AstNode, node_id)
    if not node:
        raise HTTPException(status_code=404, detail="node not found")
    return NodeResponse(
        id=node.id,
        file_id=node.file_id,
        kind=node.kind,
        name=node.name,
        parent_id=node.parent_id,
        start=[node.start_line, node.start_col],
        end=[node.end_line, node.end_col],
        start_byte=node.start_byte,
        end_byte=node.end_byte,
        meta=node.meta,
    )


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

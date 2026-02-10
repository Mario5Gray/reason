from pydantic import BaseModel
from typing import Any

class IngestRequest(BaseModel):
    language: str
    root_path: str | None = None
    files: list[str]

class IngestResponse(BaseModel):
    run_id: int
    files_indexed: int

class QueryResponse(BaseModel):
    results: list[dict[str, Any]]


class SourceSliceRequest(BaseModel):
    path: str
    start_byte: int
    end_byte: int

class FileResponse(BaseModel):
    id: int
    run_id: int
    path: str
    content_hash: str
    size_bytes: int

class NodeResponse(BaseModel):
    id: int
    file_id: int
    kind: str
    name: str | None
    parent_id: int | None
    start: list[int]
    end: list[int]
    start_byte: int
    end_byte: int
    meta: dict | None

class SourceSliceResponse(BaseModel):
    path: str
    start_byte: int
    end_byte: int
    text: str

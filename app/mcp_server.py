"""Reason MCP Server -- exposes code indexing tools over Model Context Protocol."""
import json
import logging
import sys
from contextlib import contextmanager

from mcp.server.fastmcp import FastMCP

from .db import SessionLocal
from .models import AstNode, SourceFile
from .ingest import ingest_files
from .query import query_nodes, query_defs, query_calls, list_runs, list_run_files
from .serializers import (
    serialize_node_summary,
    serialize_node_detail,
    serialize_file,
    serialize_run,
)

logging.basicConfig(stream=sys.stderr, level=logging.INFO)
logger = logging.getLogger(__name__)

mcp = FastMCP("reason")


@contextmanager
def _get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ── ingest ───────────────────────────────────────────────────

@mcp.tool()
def reason_ingest(language: str, files: list[str], root_path: str | None = None) -> str:
    """Ingest source files into the Reason index for a given language.

    Args:
        language: Programming language (python, javascript, js, ts, tsx, css, scss)
        files: List of absolute file paths to ingest
        root_path: Optional root path for the project
    """
    with _get_db() as db:
        run_id = ingest_files(db, language, files, root_path)
        return json.dumps({"run_id": run_id, "files_indexed": len(files)})


# ── discovery ────────────────────────────────────────────────

@mcp.tool()
def reason_list_runs(limit: int = 50) -> str:
    """List ingestion runs, most recent first.

    Args:
        limit: Maximum number of runs to return (default 50)
    """
    with _get_db() as db:
        runs = list_runs(db, limit=limit)
        return json.dumps([serialize_run(r) for r in runs])


@mcp.tool()
def reason_list_run_files(run_id: int, limit: int = 200) -> str:
    """List files that belong to a specific ingestion run.

    Args:
        run_id: The ID of the ingestion run
        limit: Maximum number of files to return (default 200)
    """
    with _get_db() as db:
        files = list_run_files(db, run_id=run_id, limit=limit)
        return json.dumps([serialize_file(f) for f in files])


# ── queries ──────────────────────────────────────────────────

@mcp.tool()
def reason_query_nodes(
    kind: str | None = None,
    name: str | None = None,
    limit: int = 50,
    run_id: int | None = None,
    file_id: int | None = None,
) -> str:
    """Search AST nodes by kind and/or name.

    Args:
        kind: Node kind filter (e.g. function_definition, class_definition, call_expression, import_statement)
        name: Exact name filter
        limit: Maximum results (default 50)
        run_id: Filter to a specific ingestion run
        file_id: Filter to a specific file
    """
    with _get_db() as db:
        nodes = query_nodes(db, kind=kind, name=name, limit=limit, run_id=run_id, file_id=file_id)
        return json.dumps([serialize_node_summary(n) for n in nodes])


@mcp.tool()
def reason_query_defs(
    name: str | None = None,
    limit: int = 50,
    run_id: int | None = None,
    file_id: int | None = None,
) -> str:
    """Search for function/class definitions.

    Args:
        name: Exact name filter (e.g. 'MyClass', 'process_data')
        limit: Maximum results (default 50)
        run_id: Filter to a specific ingestion run
        file_id: Filter to a specific file
    """
    with _get_db() as db:
        nodes = query_defs(db, name=name, limit=limit, run_id=run_id, file_id=file_id)
        return json.dumps([serialize_node_summary(n) for n in nodes])


@mcp.tool()
def reason_query_calls(
    name: str | None = None,
    limit: int = 50,
    run_id: int | None = None,
    file_id: int | None = None,
) -> str:
    """Search for function/method call sites.

    Args:
        name: Name of the function being called
        limit: Maximum results (default 50)
        run_id: Filter to a specific ingestion run
        file_id: Filter to a specific file
    """
    with _get_db() as db:
        nodes = query_calls(db, name=name, limit=limit, run_id=run_id, file_id=file_id)
        return json.dumps([serialize_node_summary(n) for n in nodes])


# ── lookups ──────────────────────────────────────────────────

@mcp.tool()
def reason_get_file(file_id: int) -> str:
    """Get metadata for a source file by its ID.

    Args:
        file_id: The database ID of the source file
    """
    with _get_db() as db:
        f = db.get(SourceFile, file_id)
        if not f:
            return json.dumps({"error": "file not found"})
        return json.dumps(serialize_file(f))


@mcp.tool()
def reason_get_node(node_id: int) -> str:
    """Get detailed information about an AST node by its ID.

    Args:
        node_id: The database ID of the AST node
    """
    with _get_db() as db:
        n = db.get(AstNode, node_id)
        if not n:
            return json.dumps({"error": "node not found"})
        return json.dumps(serialize_node_detail(n))


@mcp.tool()
def reason_get_source(path: str, start_byte: int, end_byte: int) -> str:
    """Fetch a source code slice by file path and byte range.

    Args:
        path: Absolute path to the source file
        start_byte: Start byte offset (inclusive)
        end_byte: End byte offset (exclusive)
    """
    try:
        with open(path, "rb") as f:
            f.seek(start_byte)
            data = f.read(max(0, end_byte - start_byte))
        text = data.decode("utf-8", errors="replace")
        return json.dumps({"path": path, "start_byte": start_byte, "end_byte": end_byte, "text": text})
    except FileNotFoundError:
        return json.dumps({"error": f"file not found: {path}"})


if __name__ == "__main__":
    mcp.run(transport="stdio")

from .models import AstNode, SourceFile, Run


def serialize_node_summary(n: AstNode) -> dict:
    """Compact node representation for query result lists."""
    return {
        "id": n.id,
        "file_id": n.file_id,
        "kind": n.kind,
        "name": n.name,
        "start": [n.start_line, n.start_col],
        "end": [n.end_line, n.end_col],
    }


def serialize_node_detail(n: AstNode) -> dict:
    """Full node representation including byte offsets and meta."""
    return {
        "id": n.id,
        "file_id": n.file_id,
        "kind": n.kind,
        "name": n.name,
        "parent_id": n.parent_id,
        "start": [n.start_line, n.start_col],
        "end": [n.end_line, n.end_col],
        "start_byte": n.start_byte,
        "end_byte": n.end_byte,
        "meta": n.meta,
    }


def serialize_file(f: SourceFile) -> dict:
    return {
        "id": f.id,
        "run_id": f.run_id,
        "path": f.path,
        "content_hash": f.content_hash,
        "size_bytes": f.size_bytes,
    }


def serialize_run(r: Run) -> dict:
    return {
        "id": r.id,
        "language": r.language,
        "root_path": r.root_path,
        "created_at": r.created_at,
    }

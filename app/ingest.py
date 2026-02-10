from __future__ import annotations
import hashlib
from datetime import datetime
from sqlalchemy.orm import Session
from .models import Run, SourceFile, CstBlob, AstNode
from .treesitter import get_ts_parser
from .ast_extract import extract_ast_like
import orjson


def _hash_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def ingest_files(db: Session, language: str, files: list[str], root_path: str | None = None) -> int:
    run = Run(language=language, root_path=root_path, created_at=datetime.utcnow().isoformat())
    db.add(run)
    db.flush()

    parser = get_ts_parser(language)

    for path in files:
        with open(path, "rb") as f:
            data = f.read()
        file_rec = SourceFile(
            run_id=run.id,
            path=path,
            content_hash=_hash_bytes(data),
            size_bytes=len(data),
        )
        db.add(file_rec)
        db.flush()

        tree = parser.parse(data)
        cst = CstBlob(file_id=file_rec.id, tree=orjson.loads(orjson.dumps(tree.root_node.sexp())))
        db.add(cst)

        ast_nodes = extract_ast_like(language, tree)
        for n in ast_nodes:
            db.add(AstNode(
                file_id=file_rec.id,
                kind=n.kind,
                name=n.name,
                parent_id=None if n.parent_idx is None else n.parent_idx,
                start_byte=n.start_byte,
                end_byte=n.end_byte,
                start_line=n.start_line,
                start_col=n.start_col,
                end_line=n.end_line,
                end_col=n.end_col,
                meta=n.meta,
            ))

    db.commit()
    return run.id

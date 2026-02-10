from sqlalchemy.orm import Session
from sqlalchemy import select
from .models import AstNode, SourceFile


def query_nodes(
    db: Session,
    kind: str | None = None,
    name: str | None = None,
    limit: int = 50,
    kinds: list[str] | None = None,
    run_id: int | None = None,
    file_id: int | None = None,
):
    stmt = select(AstNode)
    if run_id is not None:
        stmt = stmt.join(SourceFile).where(SourceFile.run_id == run_id)
    if file_id is not None:
        stmt = stmt.where(AstNode.file_id == file_id)
    if kinds:
        stmt = stmt.where(AstNode.kind.in_(kinds))
    elif kind:
        stmt = stmt.where(AstNode.kind == kind)
    if name:
        stmt = stmt.where(AstNode.name == name)
    stmt = stmt.limit(limit)
    return db.execute(stmt).scalars().all()


def query_defs(db: Session, name: str | None = None, limit: int = 50, run_id: int | None = None, file_id: int | None = None):
    kinds = [
        "function_definition",
        "class_definition",
        "function_declaration",
        "class_declaration",
        "method_definition",
    ]
    return query_nodes(db, name=name, limit=limit, kinds=kinds, run_id=run_id, file_id=file_id)


def query_calls(db: Session, name: str | None = None, limit: int = 50, run_id: int | None = None, file_id: int | None = None):
    return query_nodes(db, kind="call_expression", name=name, limit=limit, run_id=run_id, file_id=file_id)

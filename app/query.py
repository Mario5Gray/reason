from sqlalchemy.orm import Session
from sqlalchemy import select
from .models import AstNode

def query_nodes(db: Session, kind: str | None = None, name: str | None = None, limit: int = 50):
    stmt = select(AstNode)
    if kind:
        stmt = stmt.where(AstNode.kind == kind)
    if name:
        stmt = stmt.where(AstNode.name == name)
    stmt = stmt.limit(limit)
    return db.execute(stmt).scalars().all()

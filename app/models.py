from sqlalchemy import String, Integer, BigInteger, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import JSONB
from .db import Base

class Run(Base):
    __tablename__ = "runs"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    language: Mapped[str] = mapped_column(String(32), index=True)
    root_path: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[str | None] = mapped_column(String(64), nullable=True)

    files = relationship("SourceFile", back_populates="run", cascade="all, delete-orphan")

class SourceFile(Base):
    __tablename__ = "source_files"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    run_id: Mapped[int] = mapped_column(ForeignKey("runs.id", ondelete="CASCADE"), index=True)
    path: Mapped[str] = mapped_column(Text, index=True)
    content_hash: Mapped[str] = mapped_column(String(64), index=True)
    size_bytes: Mapped[int] = mapped_column(Integer)

    run = relationship("Run", back_populates="files")
    cst = relationship("CstBlob", back_populates="file", uselist=False, cascade="all, delete-orphan")
    ast_nodes = relationship("AstNode", back_populates="file", cascade="all, delete-orphan")

class CstBlob(Base):
    __tablename__ = "cst_blobs"
    file_id: Mapped[int] = mapped_column(ForeignKey("source_files.id", ondelete="CASCADE"), primary_key=True)
    tree: Mapped[dict] = mapped_column(JSONB)

    file = relationship("SourceFile", back_populates="cst")

class AstNode(Base):
    __tablename__ = "ast_nodes"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    file_id: Mapped[int] = mapped_column(ForeignKey("source_files.id", ondelete="CASCADE"), index=True)
    kind: Mapped[str] = mapped_column(String(64), index=True)
    name: Mapped[str | None] = mapped_column(String(256), index=True)
    parent_id: Mapped[int | None] = mapped_column(BigInteger, index=True)

    start_byte: Mapped[int] = mapped_column(Integer)
    end_byte: Mapped[int] = mapped_column(Integer)
    start_line: Mapped[int] = mapped_column(Integer)
    start_col: Mapped[int] = mapped_column(Integer)
    end_line: Mapped[int] = mapped_column(Integer)
    end_col: Mapped[int] = mapped_column(Integer)

    meta: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    file = relationship("SourceFile", back_populates="ast_nodes")

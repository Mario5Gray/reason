from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0001_init"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "runs",
        sa.Column("id", sa.BigInteger(), primary_key=True),
        sa.Column("language", sa.String(length=32), nullable=False, index=True),
        sa.Column("root_path", sa.Text(), nullable=True),
        sa.Column("created_at", sa.String(length=64), nullable=True),
    )
    op.create_table(
        "source_files",
        sa.Column("id", sa.BigInteger(), primary_key=True),
        sa.Column("run_id", sa.BigInteger(), sa.ForeignKey("runs.id", ondelete="CASCADE"), index=True),
        sa.Column("path", sa.Text(), nullable=False, index=True),
        sa.Column("content_hash", sa.String(length=64), nullable=False, index=True),
        sa.Column("size_bytes", sa.Integer(), nullable=False),
    )
    op.create_table(
        "cst_blobs",
        sa.Column("file_id", sa.BigInteger(), sa.ForeignKey("source_files.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("tree", postgresql.JSONB(), nullable=False),
    )
    op.create_table(
        "ast_nodes",
        sa.Column("id", sa.BigInteger(), primary_key=True),
        sa.Column("file_id", sa.BigInteger(), sa.ForeignKey("source_files.id", ondelete="CASCADE"), index=True),
        sa.Column("kind", sa.String(length=64), nullable=False, index=True),
        sa.Column("name", sa.String(length=256), nullable=True, index=True),
        sa.Column("parent_id", sa.BigInteger(), nullable=True, index=True),
        sa.Column("start_byte", sa.Integer(), nullable=False),
        sa.Column("end_byte", sa.Integer(), nullable=False),
        sa.Column("start_line", sa.Integer(), nullable=False),
        sa.Column("start_col", sa.Integer(), nullable=False),
        sa.Column("end_line", sa.Integer(), nullable=False),
        sa.Column("end_col", sa.Integer(), nullable=False),
        sa.Column("meta", postgresql.JSONB(), nullable=True),
    )


def downgrade():
    op.drop_table("ast_nodes")
    op.drop_table("cst_blobs")
    op.drop_table("source_files")
    op.drop_table("runs")

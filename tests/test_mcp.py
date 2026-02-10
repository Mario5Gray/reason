import json
import os
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from unittest.mock import patch

from app.db import Base
from app.mcp_server import (
    reason_ingest,
    reason_list_runs,
    reason_list_run_files,
    reason_query_nodes,
    reason_query_defs,
    reason_query_calls,
    reason_get_file,
    reason_get_node,
    reason_get_source,
)


@pytest.fixture(scope="session")
def db_engine():
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        pytest.skip("DATABASE_URL not set; containerized tests require Postgres")
    engine = create_engine(database_url)
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture()
def mock_db(db_engine):
    TestSession = sessionmaker(bind=db_engine, autoflush=False, autocommit=False)
    with patch("app.mcp_server.SessionLocal", TestSession):
        yield


def test_ingest_and_query_roundtrip(mock_db, tmp_path):
    sample = tmp_path / "sample.py"
    sample.write_text("class Foo:\n    def bar(self): pass\n\ndef baz(x): return x\n")

    result = json.loads(reason_ingest("python", [str(sample)]))
    assert result["run_id"]
    assert result["files_indexed"] == 1
    run_id = result["run_id"]

    runs = json.loads(reason_list_runs())
    assert any(r["id"] == run_id for r in runs)

    files = json.loads(reason_list_run_files(run_id))
    assert len(files) == 1
    assert files[0]["path"] == str(sample)
    file_id = files[0]["id"]

    defs = json.loads(reason_query_defs(run_id=run_id))
    assert len(defs) >= 2
    names = {d["name"] for d in defs}
    assert "Foo" in names
    assert "baz" in names

    calls = json.loads(reason_query_calls(run_id=run_id))
    assert isinstance(calls, list)

    nodes = json.loads(reason_query_nodes(kind="class_definition", run_id=run_id))
    assert len(nodes) >= 1
    assert nodes[0]["name"] == "Foo"
    node_id = nodes[0]["id"]

    node_detail = json.loads(reason_get_node(node_id))
    assert node_detail["kind"] == "class_definition"
    assert node_detail["start_byte"] is not None

    file_detail = json.loads(reason_get_file(file_id))
    assert file_detail["path"] == str(sample)

    source = json.loads(reason_get_source(str(sample), 0, 20))
    assert "class Foo" in source["text"]


def test_get_node_not_found(mock_db):
    result = json.loads(reason_get_node(999999))
    assert result["error"] == "node not found"


def test_get_file_not_found(mock_db):
    result = json.loads(reason_get_file(999999))
    assert result["error"] == "file not found"


def test_get_source_not_found(mock_db):
    result = json.loads(reason_get_source("/nonexistent/path.py", 0, 10))
    assert "error" in result

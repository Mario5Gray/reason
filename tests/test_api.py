from pathlib import Path


def test_ingest_query_and_source(client, tmp_path: Path):
    sample = tmp_path / "sample.py"
    sample.write_text(
        "class Foo:\n    def bar(self):\n        return 42\n\n\n"
        "def baz(x):\n    return x + 1\n",
        encoding="utf-8",
    )

    payload = {
        "language": "python",
        "root_path": str(tmp_path),
        "files": [str(sample)],
    }

    resp = client.post("/ingest", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["files_indexed"] == 1
    run_id = data["run_id"]

    q = client.get("/query", params={"kind": "function_definition", "limit": 10})
    assert q.status_code == 200
    results = q.json()["results"]
    assert len(results) >= 1

    q_run = client.get("/query", params={"kind": "function_definition", "run_id": run_id})
    assert q_run.status_code == 200
    assert len(q_run.json()["results"]) >= 1

    node_id = results[0]["id"]
    node = client.get(f"/nodes/{node_id}")
    assert node.status_code == 200
    node_data = node.json()
    assert node_data["file_id"]

    file_id = node_data["file_id"]
    file_resp = client.get(f"/files/{file_id}")
    assert file_resp.status_code == 200
    file_data = file_resp.json()
    assert file_data["path"] == str(sample)

    q_file = client.get("/query", params={"kind": "function_definition", "file_id": file_id})
    assert q_file.status_code == 200
    assert len(q_file.json()["results"]) >= 1

    source = client.post(
        "/source",
        json={
            "path": str(sample),
            "start_byte": 0,
            "end_byte": 30,
        },
    )
    assert source.status_code == 200
    assert "class Foo" in source.json()["text"]


def test_list_runs(client, tmp_path):
    sample = tmp_path / "sample.py"
    sample.write_text("def foo(): pass\n")
    client.post("/ingest", json={"language": "python", "files": [str(sample)]})

    resp = client.get("/runs")
    assert resp.status_code == 200
    results = resp.json()["results"]
    assert len(results) >= 1
    assert "language" in results[0]
    assert "id" in results[0]


def test_list_run_files(client, tmp_path):
    sample = tmp_path / "sample.py"
    sample.write_text("def foo(): pass\n")
    resp = client.post("/ingest", json={"language": "python", "files": [str(sample)]})
    run_id = resp.json()["run_id"]

    resp = client.get(f"/runs/{run_id}/files")
    assert resp.status_code == 200
    results = resp.json()["results"]
    assert len(results) == 1
    assert results[0]["path"] == str(sample)

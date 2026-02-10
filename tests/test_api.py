from pathlib import Path


def test_ingest_query_and_source(client, tmp_path: Path):
    sample = tmp_path / "sample.py"
    sample.write_text('class Foo:\n    def bar(self):\n        return 42\n\n\ndef baz(x):\n    return x + 1\n', encoding="utf-8")

    payload = {
        "language": "python",
        "root_path": str(tmp_path),
        "files": [str(sample)],
    }

    resp = client.post("/ingest", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["files_indexed"] == 1

    q = client.get("/query", params={"kind": "function_definition", "limit": 10})
    assert q.status_code == 200
    results = q.json()["results"]
    assert len(results) >= 1

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

    source = client.post("/source", json={
        "path": str(sample),
        "start_byte": 0,
        "end_byte": 30,
    })
    assert source.status_code == 200
    assert "class Foo" in source.json()["text"]

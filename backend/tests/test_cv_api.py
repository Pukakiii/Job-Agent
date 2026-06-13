PDF = b"%PDF-1.4\n1 0 obj<<>>endobj\ntrailer<<>>\n%%EOF\n"


async def test_upload_list_download_delete_flow(cv_client):
    up = await cv_client.post(
        "/api/v1/cvs", files={"file": ("resume.pdf", PDF, "application/pdf")}
    )
    assert up.status_code == 201
    body = up.json()
    assert body["original_filename"] == "resume.pdf"
    assert "s3_key" not in body  # internal location never leaked
    cv_id = body["id"]

    lst = await cv_client.get("/api/v1/cvs")
    assert lst.status_code == 200
    assert any(c["id"] == cv_id for c in lst.json())

    dl = await cv_client.get(f"/api/v1/cvs/{cv_id}/download")
    assert dl.status_code == 200
    assert "X-Amz-Signature=" in dl.json()["url"]

    d = await cv_client.delete(f"/api/v1/cvs/{cv_id}")
    assert d.status_code == 204

    gone = await cv_client.get(f"/api/v1/cvs/{cv_id}/download")
    assert gone.status_code == 404
    assert gone.json()["error"]["code"] == "cv_not_found"


async def test_upload_unsupported_type_returns_415_envelope(cv_client):
    r = await cv_client.post(
        "/api/v1/cvs", files={"file": ("notes.txt", b"hello world", "text/plain")}
    )
    assert r.status_code == 415
    assert r.json()["error"]["code"] == "unsupported_cv_type"


async def test_cv_endpoints_require_auth(auth_client):
    # auth_client is NOT logged in
    r = await auth_client.get("/api/v1/cvs")
    assert r.status_code == 401


async def test_upload_enqueues_parse_cv(cv_client):
    from app.api.deps import get_arq_redis
    from app.main import app

    enqueued = []

    class _Recorder:
        async def enqueue_job(self, name, *args, **kwargs):
            enqueued.append((name, args, kwargs))

            class _Job:
                job_id = "job-123"

            return _Job()

    app.dependency_overrides[get_arq_redis] = lambda: _Recorder()
    try:
        resp = await cv_client.post(
            "/api/v1/cvs",
            files={"file": ("cv.pdf", b"%PDF-1.4 minimal", "application/pdf")},
        )
        assert resp.status_code == 201
        assert enqueued and enqueued[0][0] == "parse_cv"
        assert enqueued[0][1][0] == resp.json()["id"]  # cv id passed as first arg
    finally:
        app.dependency_overrides.pop(get_arq_redis, None)
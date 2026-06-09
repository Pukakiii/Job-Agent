REG = {"email": "alice@test.io", "password": "supersecret123"}


async def test_register_creates_user(auth_client):
    r = await auth_client.post("/api/v1/auth/register", json=REG)
    assert r.status_code == 201
    body = r.json()
    assert body["email"] == REG["email"]
    assert body["role"] == "user"
    assert "hashed_password" not in body  # never leaked


async def test_register_duplicate_is_rejected(auth_client):
    await auth_client.post("/api/v1/auth/register", json=REG)
    r = await auth_client.post("/api/v1/auth/register", json=REG)
    assert r.status_code == 400


async def test_login_sets_cookie_and_me_works(auth_client):
    await auth_client.post("/api/v1/auth/register", json=REG)
    login = await auth_client.post(
        "/api/v1/auth/jwt/login",
        data={"username": REG["email"], "password": REG["password"]},
    )
    assert login.status_code == 204  # cookie transport: 204 + Set-Cookie
    assert "jobagent_auth" in login.cookies

    me = await auth_client.get("/api/v1/users/me")  # cookie sent automatically
    assert me.status_code == 200
    assert me.json()["email"] == REG["email"]


async def test_me_requires_auth(auth_client):
    r = await auth_client.get("/api/v1/users/me")
    assert r.status_code == 401


async def test_login_wrong_password_fails(auth_client):
    await auth_client.post("/api/v1/auth/register", json=REG)
    r = await auth_client.post(
        "/api/v1/auth/jwt/login",
        data={"username": REG["email"], "password": "wrongpassword"},
    )
    assert r.status_code == 400

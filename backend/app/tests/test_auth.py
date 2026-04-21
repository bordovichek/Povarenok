#
# def test_register_and_me(client):
#     r = client.post(
#         "/api/auth/register",
#         json={"email": "test@example.com", "password": "password123"},
#     )
#     assert r.status_code == 201, r.text
#     assert r.json()["email"] == "test@example.com"
#
#     r2 = client.get("/api/auth/me")
#     assert r2.status_code == 200
#     assert r2.json()["email"] == "test@example.com"
#
#
# def test_login_logout(client):
#     client.post(
#         "/api/auth/register",
#         json={"email": "a@b.c", "password": "password123"},
#     )
#     client.post("/api/auth/logout")
#
#     r = client.post(
#         "/api/auth/login",
#         json={"email": "a@b.c", "password": "password123"},
#     )
#     assert r.status_code == 200
#
#     r2 = client.post("/api/auth/logout")
#     assert r2.status_code == 204

#
# def _auth(client):
#     r = client.post(
#         "/api/auth/register",
#         json={"email": "p@p.p", "password": "password123"},
#     )
#     assert r.status_code == 201
#
#
# def test_pantry_crud(client):
#     _auth(client)
#
#     r = client.post(
#         "/api/pantry/",
#         json={"name": "яйца", "category": "молочные", "quantity": 6, "unit": "шт"},
#     )
#     assert r.status_code == 201
#     item_id = r.json()["id"]
#
#     r = client.get("/api/pantry/")
#     assert r.status_code == 200
#     assert len(r.json()) == 1
#
#     r = client.put(
#         f"/api/pantry/{item_id}",
#         json={"name": "яйца", "category": "молочные", "quantity": 10, "unit": "шт"},
#     )
#     assert r.status_code == 200
#     assert r.json()["quantity"] == 10
#
#     r = client.delete(f"/api/pantry/{item_id}")
#     assert r.status_code == 204
#
#     r = client.get("/api/pantry/")
#     assert r.status_code == 200
#     assert len(r.json()) == 0

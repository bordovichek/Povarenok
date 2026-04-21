#
# def _auth(client):
#     r = client.post(
#         "/api/auth/register",
#         json={"email": "c@c.c", "password": "password123"},
#     )
#     assert r.status_code == 201
#
#
# def test_cook_flow_and_favorite(client):
#     _auth(client)
#
#     # Find any recipe
#     r = client.post(
#         "/api/recipes/search",
#         json={"ingredients": ["яйца", "молоко", "масло", "соль", "сыр", "помидоры"], "limit": 1},
#     )
#     assert r.status_code == 200
#     recipe_id = r.json()[0]["recipe"]["id"]
#
#     start = client.post("/api/cook/start", json={"recipe_id": recipe_id})
#     assert start.status_code == 201
#     session_id = start.json()["id"]
#
#     upd = client.put(f"/api/cook/sessions/{session_id}", json={"current_step": 2})
#     assert upd.status_code == 200
#
#     fin = client.post(f"/api/cook/sessions/{session_id}/finish", json={"rating": 5, "comment": "ok"})
#     assert fin.status_code == 200
#
#     # Now can favorite
#     fav = client.post(f"/api/cook/favorites/{recipe_id}")
#     assert fav.status_code == 200
#     assert fav.json()["is_favorite"] is True

#
# def _auth(client):
#     r = client.post(
#         "/api/auth/register",
#         json={"email": "r@r.r", "password": "password123"},
#     )
#     assert r.status_code == 201
#
#
# # def test_search_and_detail(client):
# #     _auth(client)
# #
# #     # Minimal required: ingredients list
# #     r = client.post(
# #         "/api/recipes/search",
# #         json={"ingredients": ["овсяные хлопья", "молоко", "банан", "мёд"], "only_owned": True, "limit": 5},
# #     )
# #     assert r.status_code == 200
# #     data = r.json()
# #     assert len(data) > 0
# #
# #     recipe_id = data[0]["recipe"]["id"]
# #
# #     d = client.get(f"/api/recipes/{recipe_id}")
# #     assert d.status_code == 200
# #     assert d.json()["id"] == recipe_id
#
#
# def test_missing_ingredients_reported(client):
#     _auth(client)
#     r = client.post(
#         "/api/recipes/search",
#         json={"ingredients": ["паста", "томатный соус"], "only_owned": False, "limit": 5},
#     )
#     assert r.status_code == 200
#     res = r.json()
#     assert len(res) > 0
#     # should have at least some missing ingredients for pasta recipes
#     assert any(len(x["missing_ingredients"]) >= 1 for x in res)

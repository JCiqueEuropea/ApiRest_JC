def test_create_user_success(client, sample_user_payload):
    response = client.post("/users/", json=sample_user_payload)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test User"
    assert data["id"] == 1


def test_get_user_success(client, created_user):
    user_id = created_user["id"]

    response = client.get(f"/users/{user_id}")
    assert response.status_code == 200
    assert response.json()["name"] == created_user["name"]


def test_update_user(client, created_user):
    user_id = created_user["id"]
    update_payload = {
        "name": "Updated Name",
        "age": 30,
        "music_preferences": ["Jazz"]
    }

    response = client.put(f"/users/{user_id}", json=update_payload)

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Name"

    get_resp = client.get(f"/users/{user_id}")
    assert get_resp.json()["name"] == "Updated Name"


def test_delete_user(client, created_user):
    user_id = created_user["id"]

    del_response = client.delete(f"/users/{user_id}")
    assert del_response.status_code == 200

    get_response = client.get(f"/users/{user_id}")
    assert get_response.status_code == 404

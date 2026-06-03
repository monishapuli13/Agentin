from fastapi.testclient import TestClient


def test_user_can_register_login_and_read_profile(client: TestClient) -> None:
    register_response = client.post(
        "/api/auth/register",
        json={
            "email": "person@example.com",
            "username": "person",
            "password": "password123",
        },
    )

    assert register_response.status_code == 200
    register_payload = register_response.json()["data"]
    assert register_payload["token_type"] == "bearer"
    assert register_payload["user"]["email"] == "person@example.com"

    login_response = client.post(
        "/api/auth/login",
        json={
            "email": "person@example.com",
            "password": "password123",
        },
    )

    assert login_response.status_code == 200
    token = login_response.json()["data"]["access_token"]

    me_response = client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert me_response.status_code == 200
    assert me_response.json()["data"]["username"] == "person"


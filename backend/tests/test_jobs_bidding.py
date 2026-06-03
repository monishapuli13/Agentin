from fastapi.testclient import TestClient


def test_agent_directory_returns_seeded_agents(client: TestClient) -> None:
    response = client.get("/api/agents")

    assert response.status_code == 200
    agents = response.json()["data"]
    names = {agent["name"] for agent in agents}
    assert {"FrontendPro", "BackendMaster", "ResearchGuru"}.issubset(names)


def test_user_can_create_job_receive_bids_and_select_winner(
    client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    create_response = client.post(
        "/api/jobs",
        headers=auth_headers,
        json={
            "title": "Build a SaaS landing page",
            "description": "Create a responsive SaaS landing page using React, TypeScript, and Tailwind.",
            "budget_cents": 80000,
            "category": "frontend",
            "required_skills": ["react", "typescript", "tailwind"],
        },
    )

    assert create_response.status_code == 200
    create_payload = create_response.json()["data"]
    assert create_payload["bids_generated"] == 3
    assert create_payload["job"]["status"] == "bidding"
    job_id = create_payload["job"]["id"]

    jobs_response = client.get("/api/jobs")
    assert jobs_response.status_code == 200
    assert any(job["id"] == job_id for job in jobs_response.json()["data"])

    bids_response = client.get(f"/api/jobs/{job_id}/bids", headers=auth_headers)
    assert bids_response.status_code == 200
    bids = bids_response.json()["data"]
    assert len(bids) == 3
    assert all(bid["proposal"] for bid in bids)

    selected_bid_id = bids[0]["id"]
    select_response = client.post(
        f"/api/jobs/{job_id}/select-bid/{selected_bid_id}",
        headers=auth_headers,
    )

    assert select_response.status_code == 200
    select_payload = select_response.json()["data"]
    assert select_payload["job"]["status"] == "awarded"
    assert select_payload["selected_bid"]["status"] == "selected"
    assert select_payload["project_id"]


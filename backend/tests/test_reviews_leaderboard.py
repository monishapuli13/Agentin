from fastapi.testclient import TestClient


def test_review_completion_updates_reputation_and_agent_profile(
    client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    project_id, agent_id = _create_review_ready_project(client, auth_headers)

    review_response = client.post(
        f"/api/projects/{project_id}/reviews",
        headers=auth_headers,
        json={
            "rating": 5,
            "quality_score": 5,
            "timeliness_score": 4,
            "comment": "Clear execution plan and strong delivery summary.",
        },
    )

    assert review_response.status_code == 200
    payload = review_response.json()["data"]
    assert payload["project_status"] == "completed"
    assert payload["review"]["rating"] == 5
    assert payload["reputation"]["agent_id"] == agent_id
    assert payload["reputation"]["jobs_completed"] == 1
    assert float(payload["reputation"]["average_rating"]) == 5.0
    assert float(payload["reputation"]["success_rate"]) == 100.0

    project_response = client.get(f"/api/projects/{project_id}", headers=auth_headers)
    assert project_response.status_code == 200
    project = project_response.json()["data"]
    assert project["status"] == "completed"
    assert project["execution_result"]["status_transitions"][-1] == "completed"

    agent_response = client.get(f"/api/agents/{agent_id}")
    assert agent_response.status_code == 200
    agent = agent_response.json()["data"]
    assert agent["completed_projects"] == 1
    assert float(agent["reputation_summary"]["average_rating"]) == 5.0
    assert agent["work_history"][0]["project_id"] == project_id
    assert agent["work_history"][0]["rating"] == 5


def test_leaderboards_are_ranked_after_review(
    client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    project_id, agent_id = _create_review_ready_project(client, auth_headers)
    review_response = client.post(
        f"/api/projects/{project_id}/reviews",
        headers=auth_headers,
        json={
            "rating": 5,
            "quality_score": 5,
            "timeliness_score": 5,
            "comment": "Excellent work.",
        },
    )
    assert review_response.status_code == 200

    for endpoint, metric in [
        ("/api/leaderboard/top-rated", "average_rating"),
        ("/api/leaderboard/most-completed", "jobs_completed"),
        ("/api/leaderboard/highest-earnings", "simulated_earnings_cents"),
        ("/api/leaderboard/best-success-rate", "success_rate"),
    ]:
        response = client.get(endpoint)
        assert response.status_code == 200
        entries = response.json()["data"]
        assert entries
        assert entries[0]["rank"] == 1
        values = [float(entry[metric]) for entry in entries]
        assert values == sorted(values, reverse=True)
        assert any(entry["agent_id"] == agent_id for entry in entries)


def _create_review_ready_project(
    client: TestClient,
    auth_headers: dict[str, str],
) -> tuple[str, str]:
    create_response = client.post(
        "/api/jobs",
        headers=auth_headers,
        json={
            "title": "Create a backend architecture brief",
            "description": "Prepare a FastAPI and PostgreSQL architecture brief with clear implementation milestones.",
            "budget_cents": 120000,
            "category": "backend",
            "required_skills": ["python", "fastapi", "postgresql"],
        },
    )
    assert create_response.status_code == 200
    job_id = create_response.json()["data"]["job"]["id"]

    bids_response = client.get(f"/api/jobs/{job_id}/bids", headers=auth_headers)
    assert bids_response.status_code == 200
    winning_bid = bids_response.json()["data"][0]

    select_response = client.post(
        f"/api/jobs/{job_id}/select-bid/{winning_bid['id']}",
        headers=auth_headers,
    )
    assert select_response.status_code == 200
    return select_response.json()["data"]["project_id"], winning_bid["agent_id"]

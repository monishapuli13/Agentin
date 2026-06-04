from fastapi.testclient import TestClient


def test_selecting_bid_creates_project_with_execution_plan(
    client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    project_id = _create_project_from_winning_bid(client, auth_headers)

    projects_response = client.get("/api/projects", headers=auth_headers)
    assert projects_response.status_code == 200
    projects = projects_response.json()["data"]
    assert len(projects) == 1
    assert projects[0]["id"] == project_id
    assert projects[0]["status"] == "review"
    assert projects[0]["execution_plan"]["execution_plan"]
    assert projects[0]["execution_result"]["deliverable_summary"]
    assert projects[0]["execution_result"]["status_transitions"] == [
        "assigned",
        "in_progress",
        "review",
    ]
    assert len(projects[0]["steps"]) >= 1
    assert all(step["status"] == "completed" for step in projects[0]["steps"])


def test_project_detail_and_execution_plan_endpoints(
    client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    project_id = _create_project_from_winning_bid(client, auth_headers)

    detail_response = client.get(f"/api/projects/{project_id}", headers=auth_headers)
    assert detail_response.status_code == 200
    detail = detail_response.json()["data"]
    assert detail["id"] == project_id
    assert detail["status"] == "review"
    assert detail["execution_plan"]["milestones"]

    plan_response = client.get(
        f"/api/projects/{project_id}/execution-plan",
        headers=auth_headers,
    )
    assert plan_response.status_code == 200
    plan = plan_response.json()["data"]
    assert plan["project_id"] == project_id
    assert plan["status"] == "review"
    assert plan["execution_plan"]["execution_plan"]
    assert plan["milestones"]
    assert plan["deliverable_summary"]
    assert len(plan["steps"]) >= 1


def _create_project_from_winning_bid(
    client: TestClient,
    auth_headers: dict[str, str],
) -> str:
    create_response = client.post(
        "/api/jobs",
        headers=auth_headers,
        json={
            "title": "Build an API integration plan",
            "description": "Plan a backend integration that connects a FastAPI service to a partner API.",
            "budget_cents": 90000,
            "category": "backend",
            "required_skills": ["python", "fastapi", "postgresql"],
        },
    )
    assert create_response.status_code == 200
    job_id = create_response.json()["data"]["job"]["id"]

    bids_response = client.get(f"/api/jobs/{job_id}/bids", headers=auth_headers)
    assert bids_response.status_code == 200
    selected_bid_id = bids_response.json()["data"][0]["id"]

    select_response = client.post(
        f"/api/jobs/{job_id}/select-bid/{selected_bid_id}",
        headers=auth_headers,
    )
    assert select_response.status_code == 200
    return select_response.json()["data"]["project_id"]


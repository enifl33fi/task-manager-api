
from httpx import AsyncClient


async def test_create_task_returns_201(
    client: AsyncClient,
    user: dict,
):
    response = await client.post(
        "/tasks",
        json={
            "title": "Test task",
            "description": "Task description",
            "owner_id": user["id"],
        },
    )

    assert response.status_code == 201

    body = response.json()
    assert body["title"] == "Test task"
    assert body["description"] == "Task description"
    assert body["done"] is False
    assert body["owner_id"] == user["id"]


async def test_create_task_with_missing_owner_returns_404(
    client: AsyncClient,
):
    response = await client.post(
        "/tasks",
        json={
            "title": "Orphan task",
            "description": None,
            "owner_id": 999999,
        },
    )

    assert response.status_code == 404


async def test_done_filter_and_pagination(
    client: AsyncClient,
    user: dict,
):
    owner_id = user["id"]

    for title, done in [
        ("Task 1", False),
        ("Task 2", True),
        ("Task 3", False),
        ("Task 4", True),
    ]:
        response = await client.post(
            "/tasks",
            json={
                "title": title,
                "done": done,
                "owner_id": owner_id,
            },
        )
        assert response.status_code == 201

    done_response = await client.get("/tasks?done=true")
    assert done_response.status_code == 200
    assert len(done_response.json()) == 2
    assert all(task["done"] for task in done_response.json())

    page_response = await client.get("/tasks?limit=2&offset=1")
    assert page_response.status_code == 200
    assert len(page_response.json()) == 2
    assert [task["title"] for task in page_response.json()] == [
        "Task 2",
        "Task 3",
    ]


async def test_patch_changes_only_provided_fields(
    client: AsyncClient,
    user: dict,
):
    create_response = await client.post(
        "/tasks",
        json={
            "title": "Original title",
            "description": "Original description",
            "done": False,
            "owner_id": user["id"],
        },
    )

    assert create_response.status_code == 201
    task = create_response.json()

    patch_response = await client.patch(
        f"/tasks/{task['id']}",
        json={"done": True},
    )

    assert patch_response.status_code == 200

    updated = patch_response.json()
    assert updated["done"] is True
    assert updated["title"] == "Original title"
    assert updated["description"] == "Original description"
    assert updated["owner_id"] == user["id"]


async def test_delete_task_then_get_returns_404(
    client: AsyncClient,
    user: dict,
):
    create_response = await client.post(
        "/tasks",
        json={
            "title": "Task to delete",
            "owner_id": user["id"],
        },
    )

    assert create_response.status_code == 201
    task_id = create_response.json()["id"]

    delete_response = await client.delete(f"/tasks/{task_id}")
    assert delete_response.status_code == 204

    get_response = await client.get(f"/tasks/{task_id}")
    assert get_response.status_code == 404

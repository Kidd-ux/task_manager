def test_get_all_tasks(client, task_create):
    response = client.get("/tasks")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["title"] == task_create["title"]


def test_get_all_tasks_empty(client):
    response = client.get("/tasks")
    assert response.status_code == 200
    assert len(response.json()) == 0


def test_get_task_by_id(client, task_create):
    task = client.get(
        f"/tasks/{task_create['id']}",
    )
    assert task.status_code == 200
    assert task.json()["title"] == task_create["title"]


def test_get_task_by_non_existen_id(client, task_create):
    task = client.get("/tasks/999")
    assert task.status_code == 404
    assert task.json()["detail"] == "Task not found"


def test_post_task(client, auth_headers, task_data):
    task = client.post("/tasks", json=task_data, headers=auth_headers)
    assert task.status_code == 200
    assert task.json()["title"] == task_data["title"]
    assert task.json()["project_id"] == task_data["project_id"]
    assert task.json()["status"] == task_data["status"]


def test_post_task_without_auth(client, task_data):
    task = client.post("/tasks", json=task_data)
    assert task.status_code == 401
    assert task.json()["detail"] == "Not authenticated"


def test_post_task_with_invalid_data(client, auth_headers):
    task = client.post(
        "/tasks",
        json={
            "title": 123,
            "description": 321,
            "status": "didn't do",
            "project_id": "abc",
        },
        headers=auth_headers,
    )
    assert task.status_code == 422
    assert task.json()["detail"][0]["loc"] == ["body", "title"]
    assert task.json()["detail"][0]["msg"] == "Input should be a valid string"

    assert task.json()["detail"][1]["loc"] == ["body", "description"]
    assert task.json()["detail"][1]["msg"] == "Input should be a valid string"

    assert task.json()["detail"][2]["loc"] == ["body", "status"]
    assert (
        task.json()["detail"][2]["msg"]
        == "Input should be 'todo', 'in_progress' or 'done'"
    )

    assert task.json()["detail"][3]["loc"] == ["body", "project_id"]
    assert (
        task.json()["detail"][3]["msg"]
        == "Input should be a valid integer, unable to parse string as an integer"
    )


def test_post_task_with_invalid_project_id(client, auth_headers, task_data):
    task = client.post(
        "/tasks",
        json={
            "title": task_data["title"],
            "description": task_data["description"],
            "status": task_data["status"],
            "project_id": 999,
        },
        headers=auth_headers,
    )
    assert task.status_code == 404
    assert task.json()["detail"] == "Project not found"


def test_post_task_in_someone_else_project(
    client, make_headers, project_create, user_data_2
):
    auth = make_headers(user_data_2)
    task = client.post(
        "/tasks",
        json={
            "title": "another_project",
            "description": "empty",
            "status": "in_progress",
            "project_id": int(project_create["id"]),
        },
        headers=auth,
    )
    assert task.status_code == 403
    assert task.json()["detail"] == "You do not have permission"
    response = client.get("/tasks")
    assert response.status_code == 200
    assert len(response.json()) == 0


def test_patch_task(client, auth_headers, task_create):
    response = client.patch(
        f"/tasks/{task_create['id']}",
        json={
            "title": "patched_task",
            "description": "not empty",
            "status": "done",
        },
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert response.json()["title"] == "patched_task"
    assert response.json()["description"] == "not empty"
    assert response.json()["status"] == "done"


def test_patch_task_non_exists(client, auth_headers):
    response = client.patch(
        "/tasks/999",
        json={
            "title": "patched_task",
            "description": "not empty",
            "status": "done",
        },
        headers=auth_headers,
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Task not found"


def test_patch_task_without_auth(client, task_create):
    response = client.patch(
        f"/tasks/{task_create['id']}",
        json={
            "title": "patched_task",
            "description": "not empty",
            "status": "done",
        },
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"


def test_patch_task_someone_else(client, task_create, make_headers, user_data_2):
    auth = make_headers(user_data_2)
    response = client.patch(
        f"/tasks/{task_create['id']}",
        json={
            "title": "patched_task",
            "description": "not empty",
            "status": "done",
        },
        headers=auth,
    )
    assert response.status_code == 403
    assert response.json()["detail"] == "You do not have permission"
    tasks = client.get("/tasks")
    assert tasks.status_code == 200
    assert len(tasks.json()) == 1
    assert tasks.json()[0]["title"] == "test_task"


def test_delete_task(client, task_create, auth_headers):
    response = client.delete(f"/tasks/{task_create['id']}", headers=auth_headers)
    assert response.status_code == 200
    tasks = client.get("/tasks")
    assert tasks.status_code == 200
    assert len(tasks.json()) == 0


def test_delete_task_non_exists(client, auth_headers):
    response = client.delete("/tasks/999", headers=auth_headers)
    assert response.status_code == 404
    assert response.json()["detail"] == "Task not found"


def test_delete_task_without_auth(client, task_create):
    response = client.delete(f"/tasks/{task_create['id']}")
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"
    task = client.get("/tasks")
    assert task.status_code == 200
    assert len(task.json()) == 1


def test_delete_task_someone_else(
    client, task_create, auth_headers, make_headers, user_data_2
):
    auth = make_headers(user_data_2)
    response = client.delete(f"/tasks/{task_create['id']}", headers=auth)
    assert response.status_code == 403
    assert response.json()["detail"] == "You do not have permission"
    task = client.get("/tasks")
    assert task.status_code == 200
    assert len(task.json()) == 1

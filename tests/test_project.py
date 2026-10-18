def test_create_project(auth_headers, client, user):
    data = {"name": "test_project"}
    response = client.post("/projects", headers=auth_headers, json=data)
    assert response.status_code == 200
    assert response.json()["name"] == data["name"]
    assert response.json()["owner_id"] == user["id"]


def test_create_without_auth(client):
    data = {"name": "test_project"}
    response = client.post("/projects", json=data)
    assert response.status_code == 401


def test_create_empty_data(client, auth_headers):
    response = client.post("/projects", json={}, headers=auth_headers)
    assert response.status_code == 422


def test_create_duplicate_project(client, auth_headers):
    created = client.post(
        "/projects", json={"name": "test_project"}, headers=auth_headers
    )
    assert created.status_code == 200
    duplicate = client.post(
        "/projects", json={"name": "test_project"}, headers=auth_headers
    )
    assert duplicate.status_code == 409
    assert duplicate.json()["detail"] == "Project already exists"


def test_get_all_projects(client, auth_headers):
    created_1 = client.post(
        "/projects", json={"name": "test_project_1"}, headers=auth_headers
    )
    assert created_1.status_code == 200
    created_2 = client.post(
        "/projects", json={"name": "test_project_2"}, headers=auth_headers
    )
    assert created_2.status_code == 200
    response = client.get("/projects")
    assert response.status_code == 200
    assert isinstance(response.json(), list)  # [{name:...}, {name:...}]
    assert response.json()[0]["name"] == "test_project_1"
    assert response.json()[1]["name"] == "test_project_2"


def test_get_all_projects_empty(client):
    response = client.get("/projects")
    assert response.status_code == 200
    assert response.json() == []


def test_get_project_by_id(client, auth_headers):
    created = client.post(
        "/projects", json={"name": "test_project"}, headers=auth_headers
    )
    assert created.status_code == 200
    response = client.get(f"/projects/{created.json()['id']}")
    assert response.status_code == 200
    assert response.json()["id"] == created.json()["id"]
    assert response.json()["name"] == created.json()["name"]
    assert response.json()["owner_id"] == created.json()["owner_id"]


def test_get_project_by_non_existen_id(client):
    response = client.get("/projects/999")
    assert response.status_code == 404


def test_get_project_invalid_id(client):
    response = client.get("/projects/abc")
    assert response.status_code == 422


def test_cache_cleared_after_create(client, auth_headers):
    p1 = client.post("/projects", json={"name": "test_pr"}, headers=auth_headers)
    assert p1.status_code == 200
    response_1 = client.get("/projects")
    assert response_1.status_code == 200
    assert len(response_1.json()) == 1
    p2 = client.post("/projects", json={"name": "test_pr2"}, headers=auth_headers)
    assert p2.status_code == 200
    response_2 = client.get("/projects")
    assert response_2.status_code == 200
    assert len(response_2.json()) == 2


def test_patch_project(client, auth_headers):
    old = client.post(
        "/projects", json={"name": "old_test_project"}, headers=auth_headers
    )
    assert old.status_code == 200
    new = client.patch(
        f"/projects/{old.json()['id']}",
        json={"name": "new_test_project"},
        headers=auth_headers,
    )
    assert new.status_code == 200
    response = client.get(f"/projects/{old.json()['id']}")
    assert response.status_code == 200
    assert response.json()["name"] == "new_test_project"


def test_patch_non_exists_project(client, auth_headers):
    new = client.patch(
        "/projects/1111", json={"name": "new_test_project"}, headers=auth_headers
    )
    assert new.status_code == 404
    assert new.json()["detail"] == "Project not found"


def test_patch_project_without_auth(client, auth_headers):
    old = client.post(
        "/projects", json={"name": "old_test_project"}, headers=auth_headers
    )
    assert old.status_code == 200
    new = client.patch(
        f"/projects/{old.json()['id']}", json={"name": "new_test_project"}
    )
    assert new.status_code == 401
    assert new.json()["detail"] == "Not authenticated"
    res = client.get(f"/projects/{old.json()['id']}")
    assert res.status_code == 200
    assert res.json()["name"] == "old_test_project"


def test_delete_project(client, auth_headers):
    p = client.post(
        "/projects", json={"name": "project_for_delete"}, headers=auth_headers
    )
    assert p.status_code == 200
    delete = client.delete(f"/projects/{p.json()['id']}", headers=auth_headers)
    assert delete.status_code == 200
    res = client.get(f"/projects/{p.json()['id']}")
    assert res.status_code == 404


def test_delete_project_without_auth(client, auth_headers):
    p = client.post(
        "/projects", json={"name": "project_for_delete"}, headers=auth_headers
    )
    assert p.status_code == 200
    delete = client.delete(f"/projects/{p.json()['id']}")
    assert delete.status_code == 401
    assert delete.json()["detail"] == "Not authenticated"
    res = client.get(f"/projects/{p.json()['id']}")
    assert res.status_code == 200
    assert res.json()["name"] == "project_for_delete"


def test_patch_someone_else_project_error(
    client, auth_headers, make_headers, user_data_2
):
    project = client.post(
        "/projects", json={"name": "old_test_project"}, headers=auth_headers
    )
    assert project.status_code == 200

    auth = make_headers(user_data_2)

    response = client.patch(
        f"/projects/{project.json()['id']}",
        json={"name": "updated_test"},
        headers=auth,
    )
    assert response.status_code == 403
    assert response.json()["detail"] == "You do not have permission"
    check = client.get(f"/projects/{project.json()['id']}")
    assert check.status_code == 200
    assert check.json()["name"] == "old_test_project"


def test_delete_someone_else_project_error(
    client, auth_headers, make_headers, user_data_2
):
    project = client.post(
        "/projects", json={"name": "old_test_project"}, headers=auth_headers
    )
    assert project.status_code == 200

    auth = make_headers(user_data_2)

    response = client.delete(
        f"/projects/{project.json()['id']}",
        headers=auth,
    )
    assert response.status_code == 403
    assert response.json()["detail"] == "You do not have permission"
    check = client.get(f"/projects/{project.json()['id']}")
    assert check.status_code == 200
    assert check.json()["name"] == "old_test_project"

def test_get_all_comments(client, comment_create):
    response = client.get("/comments")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["text"] == "test_comment"


def test_get_all_comments_empty(client):
    response = client.get("/comments")
    assert response.status_code == 200
    assert len(response.json()) == 0


def test_get_comment_by_id(client, comment_create):
    response = client.get(f"/comments/{comment_create['id']}")
    assert response.status_code == 200
    assert response.json()["text"] == "test_comment"


def test_get_comment_by_non_existen_id(client):
    response = client.get("/comments/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Comment not found"


def test_post_comment(client, comment_data, auth_headers):
    response = client.post("/comments", json=comment_data, headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["text"] == comment_data["text"]
    comment = client.get("/comments")
    assert comment.status_code == 200
    assert len(comment.json()) == 1
    assert comment.json()[0]["text"] == comment_data["text"]


def test_post_comment_without_auth(client, comment_data):
    response = client.post("/comments", json=comment_data)
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"


def test_post_comment_with_invalid_data(client, auth_headers):
    response = client.post(
        "/comments",
        json={"text": 123, "task_id": "abc"},
        headers=auth_headers,
    )
    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] == ["body", "text"]
    assert response.json()["detail"][0]["msg"] == "Input should be a valid string"

    assert response.json()["detail"][1]["loc"] == ["body", "task_id"]
    assert (
        response.json()["detail"][1]["msg"]
        == "Input should be a valid integer, unable to parse string as an integer"
    )


def test_post_comment_with_invalid_task(client, auth_headers):
    response = client.post(
        "/comments", json={"text": "test_comment", "task_id": 999}, headers=auth_headers
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Task not found"


def test_post_comment_someone_else(client, make_headers, comment_create, user_data_2):
    auth = make_headers(user_data_2)
    response = client.post(
        f"/comments",
        json={"text": "test_comment_2", "task_id": comment_create["task_id"]},
        headers=auth,
    )
    assert response.status_code == 403
    assert response.json()["detail"] == "You do not have permission"
    comment = client.get("/comments")
    assert comment.status_code == 200
    assert len(comment.json()) == 1
    assert comment.json()[0]["text"] == "test_comment"


def test_patch_comment(client, auth_headers, comment_create):
    response = client.patch(
        f"/comments/{comment_create['id']}",
        json={"text": "patched_comment"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert response.json()["text"] == "patched_comment"
    comment = client.get(f"/comments/{response.json()['id']}")
    assert comment.status_code == 200
    assert comment.json()["text"] == "patched_comment"


def test_patch_comment_by_non_exists_id(client, auth_headers):
    response = client.patch(
        "/comments/999",
        json={"text": "patched_comment"},
        headers=auth_headers,
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Comment not found"
    comment = client.get("/comments")
    assert comment.status_code == 200
    assert comment.json() == []


def test_patch_comment_without_auth(client, comment_create):
    response = client.patch(
        f"/comments/{comment_create['id']}",
        json={"text": "patched_comment"},
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"
    comment = client.get(f"/comments/{comment_create['id']}")
    assert comment.status_code == 200
    assert comment.json()["text"] == comment_create["text"]


def test_patch_comment_someone_else(client, comment_create, make_headers, user_data_2):
    auth = make_headers(user_data_2)
    response = client.patch(
        f"/comments/{comment_create['id']}",
        json={"text": "patched_comment"},
        headers=auth,
    )
    assert response.status_code == 403
    assert response.json()["detail"] == "You do not have permission"
    comment = client.get(f"/comments/{comment_create['id']}")
    assert comment.status_code == 200
    assert comment.json()["text"] == comment_create["text"]


def test_delete_comment(client, comment_create, auth_headers):
    response = client.delete(f"/comments/{comment_create['id']}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json() == "Comment has been deleted"
    comment = client.get(f"/comments/{comment_create['id']}")
    assert comment.status_code == 404
    assert comment.json()["detail"] == "Comment not found"


def test_delete_comment_by_non_exists_id(client, auth_headers):
    response = client.delete("/comments/999", headers=auth_headers)
    assert response.status_code == 404
    assert response.json()["detail"] == "Comment not found"


def test_delete_comment_wuthout_auth(client, comment_create):
    response = client.delete(f"/comments/{comment_create['id']}")
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"
    comment = client.get(f"/comments/{comment_create['id']}")
    assert comment.status_code == 200
    assert comment.json()["text"] == comment_create["text"]


def test_delete_comment_someone_else(client, comment_create, make_headers, user_data_2):
    auth = make_headers(user_data_2)
    response = client.delete(
        f"/comments/{comment_create['id']}",
        headers=auth,
    )
    assert response.status_code == 403
    assert response.json()["detail"] == "You do not have permission"
    comment = client.get(f"/comments/{comment_create['id']}")
    assert comment.status_code == 200
    assert comment.json()["text"] == comment_create["text"]


def test_check_comments_cache(client, auth_headers, comment_create):
    response = client.get("/comments")
    assert response.status_code == 200
    delete = client.delete(f"/tasks/{comment_create['task_id']}", headers=auth_headers)
    assert delete.status_code == 200
    cache = client.get("/comments")
    assert cache.status_code == 200
    assert cache.json() == []

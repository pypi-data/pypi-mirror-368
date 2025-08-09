import pytest
import requests


def test_get_request_success(zendesk_client, requests_mock):
    # Mock the GET request to the Zendesk API
    url = f"{zendesk_client.base_url}/test_endpoint"
    requests_mock.get(url, json={"success": True}, status_code=200)

    response = zendesk_client.get("/test_endpoint")
    assert response == {"success": True}


def test_get_request_failure(zendesk_client, requests_mock):
    # Mock a failed GET request to the Zendesk API
    url = f"{zendesk_client.base_url}/test_endpoint"
    requests_mock.get(url, status_code=404)

    with pytest.raises(requests.exceptions.HTTPError):
        zendesk_client.get("/test_endpoint")


def test_post_request_success(zendesk_client, requests_mock):
    # Mock the POST request to the Zendesk API
    url = f"{zendesk_client.base_url}/test_endpoint"
    requests_mock.post(url, json={"id": "123"}, status_code=201)

    data = {"name": "Test"}
    response = zendesk_client.post("/test_endpoint", data)
    assert response == {"id": "123"}


def test_post_request_failure(zendesk_client, requests_mock):
    # Mock a failed POST request to the Zendesk API
    url = f"{zendesk_client.base_url}/test_endpoint"
    requests_mock.post(url, text="Bad Request", status_code=400)

    data = {"name": "Test"}
    response = zendesk_client.post("/test_endpoint", data)
    assert response == {
        "error": {
            "title": "Bad Request",
            "message": "Expecting value: line 1 column 1 (char 0)",
        },
        "status_code": 400,
    }


def test_patch_request_success(zendesk_client, requests_mock):
    # Mock the PATCH request to the Zendesk API
    url = f"{zendesk_client.base_url}/test_endpoint"
    requests_mock.patch(url, json={"updated": True}, status_code=200)

    data = {"name": "Updated"}
    response = zendesk_client.patch("/test_endpoint", data)
    assert response == {"updated": True}


def test_patch_request_failure(zendesk_client, requests_mock):
    # Mock a failed PATCH request to the Zendesk API
    url = f"{zendesk_client.base_url}/test_endpoint"
    requests_mock.patch(url, text="Bad Request", status_code=400)

    data = {"name": "Updated"}
    response = zendesk_client.patch("/test_endpoint", data)
    assert response == {
        "error": {
            "title": "Bad Request",
            "message": "Expecting value: line 1 column 1 (char 0)",
        },
        "status_code": 400,
    }


def test_put_request_success(zendesk_client, requests_mock):
    # Mock the PUT request to the Zendesk API
    url = f"{zendesk_client.base_url}/test_endpoint"
    requests_mock.put(url, json={"updated": True}, status_code=200)

    data = {"name": "Updated"}
    response = zendesk_client.put("/test_endpoint", data)
    assert response == {"updated": True}


def test_put_request_failure(zendesk_client, requests_mock):
    # Mock a failed PUT request to the Zendesk API
    url = f"{zendesk_client.base_url}/test_endpoint"
    requests_mock.put(url, text="Bad Request", status_code=400)

    data = {"name": "Updated"}
    response = zendesk_client.put("/test_endpoint", data)
    assert response == {
        "error": {
            "title": "Bad Request",
            "message": "Expecting value: line 1 column 1 (char 0)",
        },
        "status_code": 400,
    }


def test_delete_request_success(zendesk_client, requests_mock):
    # Mock the DELETE request to the Zendesk API
    url = f"{zendesk_client.base_url}/test_endpoint"
    requests_mock.delete(url, status_code=204)

    response = zendesk_client.delete("/test_endpoint")
    assert response == {"status_code": 204}


def test_delete_request_failure(zendesk_client, requests_mock):
    # Mock a failed DELETE request to the Zendesk API
    url = f"{zendesk_client.base_url}/test_endpoint"
    requests_mock.delete(url, text="Not Found", status_code=404)

    response = zendesk_client.delete("/test_endpoint")
    assert response == {
        "error": {
            "title": "Not Found",
            "message": "Expecting value: line 1 column 1 (char 0)",
        },
        "status_code": 404,
    }

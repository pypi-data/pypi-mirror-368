import pytest
from mercuryorm.zendesk_manager import ZendeskAPIClient
from mercuryorm.exceptions import BadRequestError, NotFoundError


def test_create_record(record_manager, requests_mock):
    url = f"{record_manager.model.__name__.lower()}/records"
    requests_mock.post(
        f"{ZendeskAPIClient.BASE_URL}/custom_objects/{url}",
        json={"custom_object_record": {"id": "123"}},
    )

    record_data = {"name": "Test Record", "description": "This is a test record"}
    record = record_manager.create(**record_data)

    assert record["id"] == "123"
    assert "custom_object_fields" in record


def test_get_record_by_id(record_manager, requests_mock):
    # Mock da requisição GET para obter um record pelo ID
    record_id = "123"
    url = f"{record_manager.model.__name__.lower()}/records/{record_id}"
    mock_response = {"custom_object_record": {"id": record_id, "name": "Test Record"}}
    requests_mock.get(
        f"{ZendeskAPIClient.BASE_URL}/custom_objects/{url}", json=mock_response
    )

    record = record_manager.get(id=record_id)
    assert record.id == record_id
    assert record.name == "Test Record"


def test_get_record_not_found(record_manager, requests_mock):
    record_id = "nonexistent"
    url = f"{record_manager.model.__name__.lower()}/records/{record_id}"
    requests_mock.get(
        f"{ZendeskAPIClient.BASE_URL}/custom_objects/{url}", status_code=404
    )

    with pytest.raises(NotFoundError):
        record_manager.get(id=record_id)


def test_get_bad_request(record_manager, requests_mock):
    record_id = "invalid"
    url = f"{record_manager.model.__name__.lower()}/records/{record_id}"
    requests_mock.get(
        f"{ZendeskAPIClient.BASE_URL}/custom_objects/{url}",
        status_code=400,
        json={"error": "Bad Request"},
    )

    with pytest.raises(BadRequestError):
        record_manager.get(id=record_id)


def test_filter_records(record_manager, requests_mock):
    url = f"{record_manager.model.__name__.lower()}/records"
    mock_response = {
        "custom_object_records": [
            {"id": "1", "name": "Record 1"},
            {"id": "2", "name": "Qualquer"},
        ]
    }
    requests_mock.get(
        f"{ZendeskAPIClient.BASE_URL}/custom_objects/{url}", json=mock_response
    )

    records = record_manager.filter(name="Record 1")
    record_some = record_manager.filter(name="Qualquer")
    assert len(records) == 1
    assert record_some[0].id == "2"


def test_get_last_record(record_manager, requests_mock):
    url = f"{record_manager.model.__name__.lower()}/records"
    mock_response = {
        "custom_object_records": [
            {"id": "3", "name": "Last Record", "updated_at": "2024-09-29T08:02:57Z"}
        ]
    }
    requests_mock.get(
        f"{ZendeskAPIClient.BASE_URL}/custom_objects/{url}", json=mock_response
    )

    last_record = record_manager.last()
    assert last_record.id == "3"
    assert last_record.name == "Last Record"


def test_delete_record(record_manager, requests_mock):
    record_id = "123"
    url = f"{record_manager.model.__name__.lower()}/records/{record_id}"
    requests_mock.delete(
        f"{ZendeskAPIClient.BASE_URL}/custom_objects/{url}", status_code=204
    )
    response = record_manager.delete(record_id)
    assert response == {"status_code": 204}


def test_no_records_found(record_manager, requests_mock):
    url = f"{record_manager.model.__name__.lower()}/records"
    requests_mock.get(
        f"{ZendeskAPIClient.BASE_URL}/custom_objects/{url}",
        json={"custom_object_records": []},
    )

    with pytest.raises(ValueError):
        record_manager.get(name="Nonexistent Record")


def test_multiple_records_found(record_manager, requests_mock):
    url = f"{record_manager.model.__name__.lower()}/records"
    mock_response = {
        "custom_object_records": [
            {"id": "1", "name": "Record 1"},
            {"id": "2", "name": "Record 2"},
        ]
    }
    requests_mock.get(
        f"{ZendeskAPIClient.BASE_URL}/custom_objects/{url}", json=mock_response
    )

    with pytest.raises(ValueError):
        record_manager.get(name="Multiple Records")


def test_get_all(record_manager, requests_mock):
    url = f"{record_manager.model.__name__.lower()}/records"
    mock_response = {
        "custom_object_records": [
            {"id": "1", "name": "Record 1"},
            {"id": "2", "name": "Qualquer"},
        ]
    }
    requests_mock.get(
        f"{ZendeskAPIClient.BASE_URL}/custom_objects/{url}", json=mock_response
    )
    all = record_manager.all()
    assert len(all) > 1


def test_get_last_none(record_manager, requests_mock):
    url = f"{record_manager.model.__name__.lower()}/records"
    mock_response = {}
    requests_mock.get(
        f"{ZendeskAPIClient.BASE_URL}/custom_objects/{url}", json=mock_response
    )
    last = record_manager.last()
    assert last == None

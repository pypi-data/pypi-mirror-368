import pytest

from mercuryorm.fields import FieldTypes
from .conftest import MockModel


def test_get_custom_object_exists(zendesk_object_manager, requests_mock):
    # Mock the GET request for listing custom objects
    url = f"{zendesk_object_manager.client.base_url}/custom_objects"
    mock_response = {"custom_objects": [{"key": "test_object", "title": "Test Object"}]}
    requests_mock.get(url, json=mock_response)

    custom_object = zendesk_object_manager.get_custom_object("test_object")
    assert custom_object["key"] == "test_object"
    assert custom_object["title"] == "Test Object"


def test_get_custom_object_not_exists(zendesk_object_manager, requests_mock):
    # Mock the GET request for listing custom objects
    url = f"{zendesk_object_manager.client.base_url}/custom_objects"
    mock_response = {"custom_objects": []}
    requests_mock.get(url, json=mock_response)

    custom_object = zendesk_object_manager.get_custom_object("non_existent_object")
    assert custom_object is None


def test_create_custom_object(zendesk_object_manager, requests_mock):
    # Mock the POST request for creating a custom object
    url = f"{zendesk_object_manager.client.base_url}/custom_objects"
    mock_response = {
        "custom_object": {
            "key": "test_object",
            "title": "Test Object",
            "description": "A test custom object",
        }
    }
    requests_mock.post(url, json=mock_response)

    new_object = zendesk_object_manager.create_custom_object(
        key="test_object", title="Test Object", description="A test custom object"
    )
    assert new_object["custom_object"]["key"] == "test_object"
    assert new_object["custom_object"]["title"] == "Test Object"


def test_get_or_create_custom_object_exists(zendesk_object_manager, requests_mock):
    # Mock the GET request for listing custom objects
    url = f"{zendesk_object_manager.client.base_url}/custom_objects"
    mock_response = {"custom_objects": [{"key": "test_object", "title": "Test Object"}]}
    requests_mock.get(url, json=mock_response)

    existing_object, created = zendesk_object_manager.get_or_create_custom_object(
        key="test_object", title="Test Object", description="A test custom object"
    )
    assert existing_object["key"] == "test_object"
    assert not created  # Object already exists, so created should be False


def test_get_or_create_custom_object_created(zendesk_object_manager, requests_mock):
    # Mock the GET request for listing custom objects (empty result)
    url_get = f"{zendesk_object_manager.client.base_url}/custom_objects"
    requests_mock.get(url_get, json={"custom_objects": []})

    # Mock the POST request for creating a custom object
    url_post = f"{zendesk_object_manager.client.base_url}/custom_objects"
    mock_post_response = {
        "custom_object": {
            "key": "test_object",
            "title": "Test Object",
            "description": "A test custom object",
        }
    }
    requests_mock.post(url_post, json=mock_post_response)

    new_object, created = zendesk_object_manager.get_or_create_custom_object(
        key="test_object", title="Test Object", description="A test custom object"
    )
    assert new_object["custom_object"]["key"] == "test_object"
    assert created


def test_create_custom_object_field(zendesk_object_manager, requests_mock):
    url = f"{zendesk_object_manager.client.base_url}/custom_objects/test_object/fields"
    mock_response = {
        "custom_object_field": {
            "type": "text",
            "key": "field_key",
            "title": "Field Title",
        }
    }
    requests_mock.post(url, json=mock_response)

    field = zendesk_object_manager.create_custom_object_field(
        custom_object_key="test_object",
        field_type=FieldTypes.TEXT,
        key="field_key",
        title="Field Title",
    )
    assert field["custom_object_field"]["key"] == "field_key"
    assert field["custom_object_field"]["title"] == "Field Title"


def test_create_custom_object_field_with_name(zendesk_object_manager, requests_mock):
    url = f"{zendesk_object_manager.client.base_url}/custom_objects/test_object/fields"
    mock_response = {
        "custom_object_field": {"type": "text", "key": "name", "title": "Field Title"}
    }
    requests_mock.post(url, json=mock_response)

    field = zendesk_object_manager.create_custom_object_field(
        custom_object_key="test_object",
        field_type=FieldTypes.TEXT,
        key="name",
        title="Field Title",
    )
    expected = {"message": "Field 'name' is not allowed to be created"}
    assert field == expected


def test_create_custom_object_field_with_external_id(
    zendesk_object_manager, requests_mock
):
    url = f"{zendesk_object_manager.client.base_url}/custom_objects/test_object/fields"
    mock_response = {
        "custom_object_field": {
            "type": "text",
            "key": "external_id",
            "title": "Field Title",
        }
    }
    requests_mock.post(url, json=mock_response)

    field = zendesk_object_manager.create_custom_object_field(
        custom_object_key="test_object",
        field_type=FieldTypes.TEXT,
        key="external_id",
        title="Field Title",
    )
    expected = {"message": "Field 'external_id' is not allowed to be created"}
    assert field == expected


def test_create_custom_object_field_with_invalid_field(
    zendesk_object_manager, requests_mock
):
    url = f"{zendesk_object_manager.client.base_url}/custom_objects/test_object/fields"
    mock_response = {
        "custom_object_field": {"type": "text", "key": "codigo", "title": "Field Title"}
    }
    requests_mock.post(url, json=mock_response)

    with pytest.raises(Exception) as e_info:
        field = zendesk_object_manager.create_custom_object_field(
            custom_object_key="test_object",
            field_type="json",
            key="codigo",
            title="Field Title",
        )


def test_create_custom_object_record(zendesk_object_manager, requests_mock):
    # Mock the POST request for creating a custom object record
    url = f"{zendesk_object_manager.client.base_url}/custom_objects/test_object/records"
    mock_response = {
        "record": {
            "id": "123",
            "custom_object_fields": {
                "name": "Test Record",
                "description": "This is a test record",
            },
        }
    }
    requests_mock.post(url, json=mock_response)

    record_data = {"name": "Test Record", "description": "This is a test record"}
    record = zendesk_object_manager.create_custom_object_record(
        custom_object_key="test_object", record_data=record_data
    )
    assert record["record"]["id"] == "123"
    assert record["record"]["custom_object_fields"]["name"] == "Test Record"


def test_list_custom_objects(zendesk_object_manager, requests_mock):
    # Mock the GET request for listing custom objects
    url = f"{zendesk_object_manager.client.base_url}/custom_objects"
    mock_response = {"custom_objects": [{"key": "test_object", "title": "Test Object"}]}
    requests_mock.get(url, json=mock_response)

    custom_objects = zendesk_object_manager.list_custom_objects()
    assert len(custom_objects) == 1
    assert custom_objects[0]["key"] == "test_object"
    assert custom_objects[0]["title"] == "Test Object"


def test_list_custom_objects_fields(zendesk_object_manager, requests_mock):
    url = f"{zendesk_object_manager.client.base_url}/custom_objects/test_object/fields"
    mock_response = {"custom_object_fields": [{"key": "codigo"}]}
    requests_mock.get(url, json=mock_response)

    object_fields_list = zendesk_object_manager.list_custom_object_fields("test_object")
    assert object_fields_list == ["codigo"]

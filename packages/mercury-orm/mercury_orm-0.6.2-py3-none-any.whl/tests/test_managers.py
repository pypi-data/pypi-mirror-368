import pytest
import requests
from mercuryorm.client.connection import ZendeskAPIClient
from mercuryorm.managers import QuerySet


class MockModel:
    __name__ = "MockModel"

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    @classmethod
    def parse_record_fields(cls, **kwargs):
        return MockModel(**kwargs, **kwargs.get("custom_object_fields", {}))


@pytest.fixture
def queryset():
    return QuerySet(model=MockModel)


def test_all_records(queryset, requests_mock):
    url = f"/custom_objects/{queryset.model.__name__.lower()}/records"
    mock_response = {
        "custom_object_records": [
            {
                "id": "1",
                "name": "Record 1",
                "custom_object_fields": {"field1": "value1"},
            },
            {
                "id": "2",
                "name": "Record 2",
                "custom_object_fields": {"field2": "value2"},
            },
        ]
    }
    requests_mock.get(f"{ZendeskAPIClient.BASE_URL}{url}", json=mock_response)

    records = queryset.all()
    assert len(records) == 2
    assert records[0].id == "1"
    assert records[1].id == "2"


def test_all_with_pagination(queryset, requests_mock):
    base_url = ZendeskAPIClient.BASE_URL
    url = f"/custom_objects/{queryset.model.__name__.lower()}/records"
    count_url = f"{base_url}{url}/count"

    requests_mock.get(count_url, json={"count": {"value": 1}})

    mock_response = {
        "custom_object_records": [
            {
                "id": "1",
                "name": "Record 1",
                "custom_object_fields": {"field1": "value1"},
            }
        ],
        "meta": {"page_size": 1},
        "links": {"next": "next_url"},
    }
    requests_mock.get(f"{base_url}{url}", json=mock_response)

    response = queryset.all_with_pagination(page_size=1)

    assert len(response["results"]) == 1
    result = response["results"][0]
    assert isinstance(result, MockModel)
    assert result.id == "1"
    assert result.name == "Record 1"
    assert response["meta"]["page_size"] == 1
    assert response["links"]["next"] == "next_url"


def test_filter_records(queryset, requests_mock):
    url = f"/custom_objects/{queryset.model.__name__.lower()}/records"
    mock_response = {
        "custom_object_records": [
            {
                "id": "1",
                "name": "Record 1",
                "custom_object_fields": {"field1": "value1"},
            },
            {
                "id": "2",
                "name": "Record 2",
                "custom_object_fields": {"field1": "value2"},
            },
        ]
    }
    requests_mock.get(f"{ZendeskAPIClient.BASE_URL}{url}", json=mock_response)

    records = queryset.filter(field1="value1")

    assert len(records) == 1
    assert records[0].id == "1"
    assert records[0].field1 == "value1"


def test_parse_response(queryset):
    response_data = {
        "custom_object_records": [
            {
                "id": "1",
                "name": "Record 1",
                "custom_object_fields": {"field1": "value1"},
            },
            {
                "id": "2",
                "name": "Record 2",
                "custom_object_fields": {"field2": "value2"},
            },
        ]
    }

    records = queryset._parse_response(response_data)
    assert len(records) == 2
    assert records[0].id == "1"
    assert records[1].id == "2"


def test_all_with_pagination_after_cursor(queryset, requests_mock):
    base_url = ZendeskAPIClient.BASE_URL
    url = f"/custom_objects/{queryset.model.__name__.lower()}/records"
    count_url = f"{base_url}{url}/count"

    # Mock para o endpoint /count com a estrutura correta
    requests_mock.get(count_url, json={"count": {"value": 1}})
    mock_response = {
        "custom_object_records": [
            {
                "id": "3",
                "name": "Record 3",
                "custom_object_fields": {"field1": "value1"},
            }
        ],
        "meta": {"page_size": 1},
        "links": {"next": "next_url"},
    }
    requests_mock.get(f"{ZendeskAPIClient.BASE_URL}{url}", json=mock_response)

    response = queryset.all_with_pagination(page_size=1, after_cursor="abc123")

    assert len(response["results"]) == 1
    assert response["results"][0].id == "3"
    assert response["meta"]["page_size"] == 1
    assert response["links"]["next"] == "next_url"

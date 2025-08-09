import pytest
import requests
from unittest.mock import patch
from mercuryorm.zendesk_manager import ZendeskObjectManager
from mercuryorm.client.connection import ZendeskAPIClient
from mercuryorm.record_manager import RecordManager
from mercuryorm import fields


@pytest.fixture
def zendesk_client(monkeypatch):
    with patch.object(ZendeskAPIClient, "__init__", return_value=None):
        client = ZendeskAPIClient()
        client.base_url = "https://mockdomain.zendesk.com/api/v2"
        client.auth = None
        client.headers = {"Content-Type": "application/json"}
        client.default_params = {"locale": "en"}
        client.session = requests.Session()
        yield client


@pytest.fixture
def zendesk_object_manager():
    with patch.object(ZendeskAPIClient, "__init__", return_value=None):
        manager = ZendeskObjectManager()
        manager.client.base_url = "https://mockdomain.zendesk.com/api/v2"
        manager.client.headers = {"Content-Type": "application/json"}
        manager.client.auth = None
        manager.client.default_params = {"locale": "en"}
        manager.client.session = requests.Session()
        yield manager


@pytest.fixture
def custom_object():
    class MockCustomObject:
        def __init__(self, name, codigo, ativo):
            self.name = name
            self.codigo = codigo
            self.ativo = ativo
            self.id = None

        def __str__(self):
            return self.__class__.__name__

        def save(self):
            data = {
                "custom_object_record": {
                    "id": "1",
                    "name": self.name,
                    "custom_object_fields": {
                        "codigo": self.codigo,
                        "ativo": self.ativo,
                    },
                }
            }
            self.id = data["custom_object_record"]["id"]
            return data

        def to_dict(self):
            return {
                "id": self.id,
                "name": self.name,
                "codigo": self.codigo,
                "ativo": self.ativo,
            }

        def delete(self):
            if self.id:
                return 204
            return {"error": "Object does not exist"}

    return MockCustomObject(name="Test Object", codigo="1234", ativo=True)


class MockModel:
    name = fields.TextField("name")
    codigo = fields.TextField("codigo")
    ativo = fields.CheckboxField("ativo")

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    def save(self):
        return {"id": "123", "custom_object_fields": self.__dict__}

    @classmethod
    def parse_record_fields(cls, **kwargs):
        return MockModel(**kwargs, **kwargs.get("custom_object_fields", {}))


@pytest.fixture
def record_manager():
    return RecordManager(model=MockModel)

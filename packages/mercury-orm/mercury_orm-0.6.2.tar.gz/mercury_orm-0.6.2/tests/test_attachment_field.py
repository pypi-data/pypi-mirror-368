import base64

import pytest

from mercuryorm.fields import AttachmentField, IntegerField
from mercuryorm.file import AttachmentFile
from mercuryorm.base import CustomObject


class AttachTeste(CustomObject):
    ticket_id = IntegerField("ticket_id")
    attach_field = AttachmentField("field", ticket_field_name="ticket_id")


@pytest.fixture
def attachment_zendesk():
    return {
        "attachment": {
            "content_type": "image/png",
            "content_url": "https://company.zendesk.com/attachments/my_funny_profile_pic.png",
            "file_name": "my_funny_profile_pic.png",
            "id": 123456,
            "size": 1024,
        }
    }


@pytest.fixture
def attachment_response_mock(requests_mock, attachment_zendesk):
    requests_mock.get(
        "https://mockdomain.zendesk.com/api/v2/attachments/123456.json",
        json=attachment_zendesk,
    )
    return attachment_zendesk


@pytest.fixture
def attachteste_zendesk():
    return {
        "id": 1,
        "name": "Test Object",
        "custom_object_fields": {
            "ticket_id": 1,
            "attach_field_id": 123456,
            "attach_field_url": "https://company.zendesk.com/attachments/my_funny_profile_pic.png",
            "attach_field_filename": "my_funny_profile_pic.png",
            "attach_field_size": 1024,
        },
    }


@pytest.fixture
def attachteste_get_response_mock(requests_mock, attachteste_zendesk):
    attach = {"custom_object_record": attachteste_zendesk}
    requests_mock.get(
        "https://mockdomain.zendesk.com/api/v2/custom_objects/attachteste/records/1",
        json=attach,
    )
    return attachteste_zendesk


@pytest.fixture
def attachteste_all_response_mock(requests_mock, attachteste_zendesk):
    attachs = {"custom_object_records": [attachteste_zendesk]}
    requests_mock.get(
        "https://mockdomain.zendesk.com/api/v2/custom_objects/attachteste/records",
        json=attachs,
    )
    return attachs


@pytest.fixture
def attachteste_create_response_mock(requests_mock, attachteste_zendesk):
    attachs = {"custom_object_record": attachteste_zendesk}
    requests_mock.post(
        "https://mockdomain.zendesk.com/api/v2/custom_objects/attachteste/records",
        json=attachs,
    )
    return attachs


@pytest.fixture
def ticket_update_response_mock(requests_mock, attachteste_zendesk):
    attachs = {}
    requests_mock.put(
        "https://mockdomain.zendesk.com/api/v2/tickets/1.json", json=attachs
    )
    return attachs


@pytest.fixture
def attachteste_upload_file_response_mock(requests_mock):
    upload = {
        "upload": {
            "attachment": {
                "id": 123456,
                "content_url": "https://company.zendesk.com/attachments/my_funny_profile_pic.png",
                "file_name": "my_funny_profile_pic.png",
                "size": 1024,
            },
            "token": "1234567890",
        }
    }
    requests_mock.post("https://mockdomain.zendesk.com/api/v2/uploads", json=upload)
    return upload


def test_attachment_field_response_type_none(requests_mock):
    teste = AttachTeste()
    assert teste.attach_field is None


def test_attachment_field_get(attachteste_get_response_mock):
    attach = AttachTeste.objects.get(id=1)
    assert (
        attach.attach_field.id
        == attachteste_get_response_mock["custom_object_fields"]["attach_field_id"]
    )
    assert (
        attach.attach_field.url
        == attachteste_get_response_mock["custom_object_fields"]["attach_field_url"]
    )
    assert (
        attach.attach_field.filename
        == attachteste_get_response_mock["custom_object_fields"][
            "attach_field_filename"
        ]
    )
    assert (
        attach.attach_field.size
        == attachteste_get_response_mock["custom_object_fields"]["attach_field_size"]
    )


def test_attachment_filed_all(attachteste_all_response_mock, attachteste_zendesk):
    attachs = AttachTeste.objects.all()
    assert (
        attachs[0].attach_field.id
        == attachteste_zendesk["custom_object_fields"]["attach_field_id"]
    )
    assert (
        attachs[0].attach_field.url
        == attachteste_zendesk["custom_object_fields"]["attach_field_url"]
    )
    assert (
        attachs[0].attach_field.filename
        == attachteste_zendesk["custom_object_fields"]["attach_field_filename"]
    )
    assert (
        attachs[0].attach_field.size
        == attachteste_zendesk["custom_object_fields"]["attach_field_size"]
    )


def test_attachment_field_save(
    attachteste_upload_file_response_mock,
    attachteste_create_response_mock,
    ticket_update_response_mock,
):
    attach = AttachTeste(ticket_id=1)
    file = AttachmentFile(
        content=base64.b64decode("U2FsdmUK"),
        attachment_filename="my_funny_profile_pic.png",
    )
    attach.attach_field = file
    attach.save()
    assert attach.attach_field.id == 123456
    assert (
        attach.attach_field.url
        == "https://company.zendesk.com/attachments/my_funny_profile_pic.png"
    )
    assert attach.attach_field.filename == "my_funny_profile_pic.png"
    assert attach.attach_field.size == 1024

"""
Module for handling CustomObject base functionality, including saving, deleting,
and managing fields for integration with Zendesk API.
"""

from mercuryorm import fields
from mercuryorm.client.connection import ZendeskAPIClient
from mercuryorm.exceptions import (
    CreateRecordError,
    DeleteRecordError,
    UniqueConstraintError,
    UpdateRecordError,
)
from mercuryorm.record_manager import RecordManager
from mercuryorm.file import AttachmentFile


class CustomObject:
    """
    A base class for custom objects that are synchronized with the Zendesk API.

    Provides methods for saving, deleting, and converting the object to a dictionary
    format for API communication. Automatically assigns a RecordManager to child classes.
    """

    def __init_subclass__(cls, **kwargs):
        """
        This method is called automatically whenever a subclass of CustomObject is created.
        It automatically assigns the RecordManager to the child class,
        without the need to define 'objects' manually.
        """
        super().__init_subclass__(**kwargs)
        cls.objects = RecordManager(cls)
        for attr_name, attr_value in cls.__dict__.items():
            if isinstance(attr_value, fields.Field):
                attr_value.name = attr_name
                attr_value.contribute_to_class(cls, attr_name)

    def __init__(self, **kwargs):
        self.client = ZendeskAPIClient()
        self.id = None  # pylint: disable=invalid-name
        self.name = None
        for field_name, field in self.__class__.__dict__.items():
            if isinstance(field, fields.Field):
                setattr(self, field_name, kwargs.get(field_name))

    def __str__(self):
        return self.__class__.__name__

    def __repr__(self):
        """
        Returns a detailed representation of the object.
        """
        return f"<{self.__str__()} object at {hex(id(self))}>"

    def is_namefield_autoincrement(self):
        """Check if the object has a NameField and if its autoincrement is enabled."""
        # Encontra o campo 'name' na classe
        name_field = next(
            (value for key, value in self.__class__.__dict__.items() if key == "name"),
            None,
        )

        if isinstance(name_field, fields.NameField):
            return name_field.autoincrement_enabled

        return False

    def format_record(self):
        """
        Formats the current object to be sent to the API.
        """
        data = {
            "custom_object_record": {
                "custom_object_fields": self.to_save(),
                "id": getattr(self, "id", None),
                "external_id": getattr(self, "external_id", None),
            }
        }
        if not self.is_namefield_autoincrement():
            data["custom_object_record"]["name"] = getattr(self, "name", None)

        return data

    def save(self):
        """
        Saves the record in Zendesk (creates or updates).

        Raises:
            CreateRecordError: If the record could not be created.
            UpdateRecordError: If the record could not be updated.
            UniqueConstraintError: If a unique constraint is violated.
        """
        data = self.format_record()
        # -> If object not contains a NameField type
        # the name field is Unnamed Object or a name passed

        if not hasattr(self, "id") or not self.id:
            response = self.client.post(
                f"/custom_objects/{self.__class__.__name__.lower()}/records", data
            )
            if (
                response.get("details", {}).get("base", [{}])[0].get("description", "")
                == "Name already exists. Try another one."
            ):
                raise UniqueConstraintError(getattr(self, "name"))
            if response.get("status_code", 201) != 201:
                raise CreateRecordError(
                    message=response.get("details", "Error creating record")
                )
            self.id = response["custom_object_record"]["id"]
            self.name = response["custom_object_record"]["name"]
            return response
        response = self.client.patch(
            f"/custom_objects/{self.__class__.__name__.lower()}/records/{self.id}", data
        )
        if response.get("status_code", 200) != 200:
            raise UpdateRecordError(
                message=response.get("details", "Error updating record")
            )
        return response

    def delete(self):
        """
        Deletes the current object from Zendesk using its ID.

        Raises:
            DeleteRecordError: If the record could not be deleted.
        """
        response = self.client.delete(
            f"/custom_objects/{self.__class__.__name__}/records/{self.id}"
        )
        if response.get("status_code", 204) != 204:
            raise DeleteRecordError(
                message=response.get("description", "Error deleting record")
            )

        return response

    def to_save(self):
        """
        Converts the current object to a dictionary format for saving in Zendesk.

        Returns:
            dict: A dictionary containing the object's fields and values.
        """
        return self._format_fields(to_save=True)

    def to_dict(self):
        """
        Converts the current object to a dictionary format, including custom fields and
        default fields required by Zendesk API.

        Returns:
            dict: A dictionary containing the object's fields and values.
        """
        return self._format_fields()

    def to_representation(self):
        """
        Converts the current object to a dictionary format for representation, using labels.

        Returns:
            dict: A dictionary containing the object's fields and values.
            in choice fields return {value: value, label: label}
        """
        return self._format_fields(to_representation=True)

    def _format_fields(
        self, to_representation: bool = False, to_save: bool = False
    ) -> dict:
        """
        Formats the fields of the object to be sent to the API.

        Args:
            to_representation (bool, optional): If True, the method will format the fields
            for representation in Zendesk. If False, it will format the fields
            for conversion to a dictionary.

        Returns:
            dict: A dictionary containing the object's fields and values.
        """
        fields_dict = {}
        model_attributes = self.__class__.__dict__

        for field_name, field in model_attributes.items():
            if isinstance(field, fields.Field):
                if (
                    isinstance(
                        field,
                        (
                            fields.DropdownField,
                            fields.MultiselectField,
                            fields.AttachmentField,
                        ),
                    )
                    and to_representation
                ):
                    fields_dict[field_name] = None
                    if getattr(self, field_name) is not None:
                        fields_dict[field_name] = field.get_to_representation(
                            self, None
                        )
                elif (
                    isinstance(field, fields.AttachmentField)
                    and to_save
                    and getattr(self, field_name) is not None
                ):
                    field_instance = getattr(self, field_name)
                    ticket_field_name = field.ticket_field_name
                    ticket_id = getattr(self, ticket_field_name)
                    if ticket_id is None:
                        raise ValueError(
                            f"Ticket ID field '{ticket_field_name}' not found."
                        )
                    field_instance.save_with_ticket(ticket_id, "Attachment")
                    fields_dict[f"{field_name}_id"] = field_instance.id
                    fields_dict[f"{field_name}_url"] = field_instance.url
                    fields_dict[f"{field_name}_filename"] = field_instance.filename
                    fields_dict[f"{field_name}_size"] = field_instance.size
                else:
                    fields_dict[field_name] = getattr(self, field_name)

        return fields_dict

    @classmethod
    def parse_record_fields(cls, **record_data):
        """
        Parses the fields of a record from the Zendesk API response.

        Args:
            record_data (dict): The data of the record to parse.

        Returns:
            CustomObject: A CustomObject instance with the fields populated.
        """
        instance = cls()
        custom_fields = dict(record_data.get("custom_object_fields", {}).items())

        for field_name, field in instance.__class__.__dict__.items():
            if isinstance(field, fields.Field):
                if isinstance(field, fields.AttachmentField):
                    attach_id = custom_fields.get(f"{field_name}_id", None)
                    attach_url = custom_fields.get(f"{field_name}_url", None)
                    attach_filename = custom_fields.get(f"{field_name}_filename", None)
                    attach_size = custom_fields.get(f"{field_name}_size", None)
                    setattr(
                        instance,
                        field_name,
                        AttachmentFile(
                            attachment_id=attach_id,
                            attachment_filename=attach_filename,
                            attachment_url=attach_url,
                            attachment_size=attach_size,
                        ),
                    )
                else:
                    setattr(instance, field_name, custom_fields.get(field_name))

        for field in fields.DEFAULT_FIELDS:
            setattr(instance, field, record_data.get(field))

        return instance

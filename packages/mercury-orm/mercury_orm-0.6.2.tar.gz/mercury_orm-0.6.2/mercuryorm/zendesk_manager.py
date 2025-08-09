"""
This module contains the `ZendeskObjectManager` class, which manages the operations
related to Zendesk custom objects and their fields.
"""

import logging
import os

from dotenv import load_dotenv  # pylint: disable=import-error
from unidecode import unidecode

from mercuryorm import fields
from mercuryorm.client.connection import ZendeskAPIClient
from mercuryorm.exceptions import (
    CustomObjectFieldCreationError,
    NameFieldError,
    NameFieldUniqueAndAutoIncrementConflictError,
)

load_dotenv()


class ZendeskObjectManager:
    """
    Manages the interactions with Zendesk custom objects, including creating objects,
    fields, and records. Also provides methods to list existing objects and fields.
    """

    def __init__(self, email=os.getenv("ZENDESK_EMAIL", "mock@mock.com")):
        """
        Initializes the ZendeskObjectManager with the given email for authentication.
        Args:
            email (str): The email associated with the Zendesk account.
        """
        self.client = ZendeskAPIClient(email)

    def get_custom_object(self, key):
        """
        Returns the Custom Object with the given key, if it exists.
        Args:
            key (str): The key of the custom object.

        Returns:
            dict: The custom object details if found, otherwise None.
        """
        custom_objects = self.list_custom_objects()
        for obj in custom_objects:
            if obj["key"] == key:
                return obj
        return None

    def create_custom_object(self, key, title, description=""):
        """
        Creates a Custom Object (equivalent to a table in relational databases).
        Args:
            key (str): The key for the custom object.
            title (str): The title for the custom object.
            description (str, optional): A description for the custom object.

        Returns:
            dict: The response from Zendesk API with the newly created custom object.
        """
        endpoint = "/custom_objects"
        data = {
            "custom_object": {
                "key": key,
                "title": title,
                "title_pluralized": f"{title}s",
                "description": description,
                "include_in_list_view": True,
            }
        }
        return self.client.post(endpoint, data)

    def get_or_create_custom_object(self, key, title, description):
        """
        Checks if the Custom Object already exists, and creates it if it doesn't.
        Args:
            key (str): The key for the custom object.
            title (str): The title for the custom object.
            description (str): A description for the custom object.

        Returns:
            tuple: A tuple of the custom object and a boolean indicating if it was created.
        """
        existing_object = self.get_custom_object(key)
        if existing_object:
            return existing_object, False

        new_object = self.create_custom_object(key, title, description)
        return new_object, True

    def list_custom_object_fields(self, custom_object_key):
        """
        Returns a list of existing fields from a Custom Object.
        Args:
            custom_object_key (str): The key of the custom object to list fields for.

        Returns:
            list: A list of field keys for the custom object.
        """
        endpoint = f"/custom_objects/{custom_object_key}/fields"
        response = self.client.get(endpoint)
        return [field["key"] for field in response.get("custom_object_fields", [])]

    def create_custom_object_field(
        self, custom_object_key, field_type: fields.FieldTypes, key, title, **kwargs
    ):
        """
        Creates fields (columns) for a Custom Object.
        Args:
            custom_object_key (str): The key of the custom object to add fields to.
            field_type (FieldTypes): The type of the field (e.g., text, integer).
            key (str): The key of the field.
            title (str): The title of the field.
            choices (list(str), list(tuple(str))): A list of choices
            if the field is a dropdown or multiselect.

        Returns:
            dict: The response from Zendesk API with the newly created field.
        """
        pattern = kwargs.get("pattern")
        choices = kwargs.get("choices")
        if key in fields.DEFAULT_FIELDS:
            return {"message": f"Field '{key}' is not allowed to be created"}

        endpoint = f"/custom_objects/{custom_object_key}/fields"
        data = {
            "custom_object_field": {
                "type": field_type.value,  # Field type: "text", "integer", etc.
                "key": key,
                "title": title,
            }
        }
        if (
            field_type in [fields.FieldTypes.DROPDOWN, fields.FieldTypes.MULTISELECT]
            and choices
        ):
            data["custom_object_field"]["custom_field_options"] = [
                {
                    "name": choice if isinstance(choice, str) else choice[1],
                    "raw_name": choice if isinstance(choice, str) else choice[1],
                    "value": (
                        unidecode(choice).lower().replace(" ", "_")
                        if isinstance(choice, str)
                        else choice[0]
                    ),
                }
                for choice in choices
            ]
        if field_type == fields.FieldTypes.LOOKUP:
            is_custom_object = kwargs.get("is_custom_object")
            related_object = kwargs.get("related_object")
            if not is_custom_object:
                data["custom_object_field"][
                    "relationship_target_type"
                ] = f"zen:{related_object}"
            else:
                data["custom_object_field"][
                    "relationship_target_type"
                ] = f"zen:custom_object:{related_object}"
        if field_type == fields.FieldTypes.REGEXP and pattern:
            data["custom_object_field"]["regexp_for_validation"] = kwargs.get("pattern")

        return self.client.post(endpoint, data)

    def update_custom_object_name(
        self,
        custom_object_key,
        unique,
        autoincrement_enabled,
        autoincrement_prefix,
        autoincrement_padding,
        autoincrement_next_sequence,
    ):  # pylint: disable=too-many-arguments
        """
        Updates the name field properties of a Custom Object.
        Args:
            custom_object_key (str): The key of the custom object.
            unique (bool): Whether the name field should be unique.
            autoincrement_enabled (bool): Whether the name field should be autoincremented.
            autoincrement_prefix (str): The prefix for the autoincremented name field.
            autoincrement_padding (int): The padding for the autoincremented name field.
            autoincrement_next_sequence (int): The next sequence number for
            the autoincremented name field.

        Returns:
            dict: The response from Zendesk API with the updated field.
        """

        if unique == autoincrement_enabled:
            raise NameFieldUniqueAndAutoIncrementConflictError()

        endpoint = f"/custom_objects/{custom_object_key}/fields/standard::name"
        data = {
            "custom_object_field": {
                "properties": {
                    "is_unique": unique,
                    "autoincrement_enabled": autoincrement_enabled,
                    "autoincrement_prefix": autoincrement_prefix,
                    "autoincrement_padding": autoincrement_padding,
                    "autoincrement_next_sequence": autoincrement_next_sequence,
                }
            }
        }
        return self.client.put(endpoint, data)

    def get_custom_object_fields(self, custom_object_key):
        """
        Returns a list of existing fields from a Custom Object.
        Args:
            custom_object_key (str): The key of the custom object to list fields for.

        Returns:
            list: A list of field keys for the custom object.
        """
        endpoint = f"/custom_objects/{custom_object_key}/fields"
        response = self.client.get(endpoint)
        return response.get("custom_object_fields", [])

    def create_custom_object_record(self, custom_object_key, record_data):
        """
        Adds a record (row) to a Custom Object.
        Args:
            custom_object_key (str): The key of the custom object.
            record_data (dict): The data for the new record.

        Returns:
            dict: The response from Zendesk API with the newly created record.
        """
        endpoint = f"/custom_objects/{custom_object_key}/records"
        data = {"record": record_data}
        return self.client.post(endpoint, data)

    def list_custom_objects(self):
        """
        Lists all custom objects.
        Returns:
            list: A list of custom objects.
        """
        endpoint = "/custom_objects"
        return self.client.get(endpoint).get("custom_objects", [])

    def create_custom_object_from_model(self, model):  # pylint: disable=too-many-locals
        """
        Creates a Custom Object and its fields based on the provided template/model.
        Args:
            model (type): The model class representing the custom object.

        Returns:
            None
        """
        for field_name, field in model.__dict__.items():
            if isinstance(field, fields.NameField):
                if field_name != "name":
                    raise NameFieldError()

        custom_object_key = model.__name__.lower()
        self.create_custom_object(
            key=custom_object_key,
            title=model.__name__,
            description=f"Custom Object for {model.__name__}",
        )

        existing_fields = self.list_custom_object_fields(custom_object_key)

        for field_name, field in model.__dict__.items():  # pylint: disable=too-many-nested-blocks
            if isinstance(field, fields.Field):
                title = field.name if hasattr(field, "name") else field_name
                if field_name not in existing_fields:
                    if isinstance(field, fields.AttachmentField):
                        extra_fields = (
                            (f"{field_name}_id", fields.FieldTypes.INTEGER),
                            (f"{field_name}_filename", fields.FieldTypes.TEXT),
                            (f"{field_name}_url", fields.FieldTypes.TEXT),
                            (f"{field_name}_size", fields.FieldTypes.INTEGER),
                        )
                        for extra_field, type_field in extra_fields:
                            response = self.create_custom_object_field(
                                custom_object_key=custom_object_key,
                                field_type=type_field,
                                key=extra_field,
                                title=extra_field,
                                choices=None,
                                pattern=None,
                                is_custom_object=None,
                                related_object=None,
                            )
                            if response.get("status_code", 201) != 201:
                                error = (
                                    response.get("details", {})
                                    .get("key", [{}])[0]
                                    .get("description", "Unknown error")
                                )
                                raise CustomObjectFieldCreationError(
                                    f"Error creating field '{extra_field}': {error}"
                                )
                            logging.info(
                                "Field '%s' created for Custom Object '%s'.",
                                extra_field,
                                custom_object_key,
                            )
                    else:
                        choices = getattr(field, "choices", None)
                        pattern = getattr(field, "pattern", None)
                        is_custom_object = getattr(field, "is_custom_object", None)
                        related_object = getattr(field, "related_object", None)
                        response = self.create_custom_object_field(
                            custom_object_key=custom_object_key,
                            field_type=field.field_type,
                            key=field_name,
                            title=title,
                            choices=choices,
                            pattern=pattern,
                            is_custom_object=is_custom_object,
                            related_object=related_object,
                        )
                        if response.get("status_code", 201) != 201:
                            error = (
                                response.get("details", {})
                                .get("key", [{}])[0]
                                .get("description", "Unknown error")
                            )
                            raise CustomObjectFieldCreationError(
                                f"Error creating field '{field_name}': {error}"
                            )
                        logging.info(
                            "Field '%s' created for Custom Object '%s'.",
                            field_name,
                            custom_object_key,
                        )
            if isinstance(field, fields.NameField):
                self.update_custom_object_name(
                    custom_object_key=custom_object_key,
                    unique=field.unique,
                    autoincrement_enabled=field.autoincrement_enabled,
                    autoincrement_prefix=field.autoincrement_prefix,
                    autoincrement_padding=field.autoincrement_padding,
                    autoincrement_next_sequence=field.autoincrement_next_sequence,
                )
                logging.info(
                    "Field '%s' created for Custom Object '%s'.",
                    field.name,
                    custom_object_key,
                )

    def get_or_create_custom_object_from_model(self, model):  # pylint: disable=too-many-locals
        """
        Checks if the Custom Object already exists and creates missing fields.
        Args:
            model (type): The model class representing the custom object.

        Returns:
            tuple: A tuple of the custom object and a boolean indicating if it was created.
        """
        custom_object_key = model.__name__.lower()

        custom_object, created = self.get_or_create_custom_object(
            key=custom_object_key,
            title=model.__name__,
            description=f"Custom Object for {model.__name__}",
        )

        existing_fields = self.list_custom_object_fields(custom_object_key)

        for field_name, field in model.__dict__.items():  # pylint: disable=too-many-nested-blocks
            if isinstance(field, fields.Field):
                title = field.name if hasattr(field, "name") else field_name
                if field_name not in existing_fields:
                    if isinstance(field, fields.AttachmentField):
                        extra_fields = (
                            (f"{field_name}_id", fields.FieldTypes.INTEGER),
                            (f"{field_name}_filename", fields.FieldTypes.TEXT),
                            (f"{field_name}_url", fields.FieldTypes.TEXT),
                            (f"{field_name}_size", fields.FieldTypes.INTEGER),
                        )
                        for extra_field, type_field in extra_fields:
                            response = self.create_custom_object_field(
                                custom_object_key=custom_object_key,
                                field_type=type_field,
                                key=extra_field,
                                title=extra_field,
                                choices=None,
                                pattern=None,
                                is_custom_object=None,
                                related_object=None,
                            )
                            if response.get("status_code", 201) != 201:
                                error = (
                                    response.get("details", {})
                                    .get("key", [{}])[0]
                                    .get("description", "Unknown error")
                                )
                                raise CustomObjectFieldCreationError(
                                    f"Error creating field '{extra_field}': {error}"
                                )
                            logging.info(
                                "Field '%s' created for Custom Object '%s'.",
                                field_name,
                                custom_object_key,
                            )
                    else:
                        choices = getattr(field, "choices", None)
                        pattern = getattr(field, "pattern", None)
                        is_custom_object = getattr(field, "is_custom_object", None)
                        related_object = getattr(field, "related_object", None)
                        response = self.create_custom_object_field(
                            custom_object_key=custom_object_key,
                            field_type=field.field_type,
                            key=field_name,
                            title=title,
                            choices=choices,
                            pattern=pattern,
                            is_custom_object=is_custom_object,
                            related_object=related_object,
                        )
                        if response.get("status_code", 201) != 201:
                            error = (
                                response.get("details", {})
                                .get("key", [{}])[0]
                                .get("description", "Unknown error")
                            )
                            raise CustomObjectFieldCreationError(
                                f"Error creating field '{field_name}': {error}"
                            )
                        logging.info(
                            "Field '%s' created for Custom Object '%s'.",
                            field_name,
                            custom_object_key,
                        )
            if isinstance(field, fields.NameField):
                self.update_custom_object_name(
                    custom_object_key=custom_object_key,
                    unique=field.unique,
                    autoincrement_enabled=field.autoincrement_enabled,
                    autoincrement_prefix=field.autoincrement_prefix,
                    autoincrement_padding=field.autoincrement_padding,
                    autoincrement_next_sequence=field.autoincrement_next_sequence,
                )
                logging.info(
                    "Field '%s' created for Custom Object '%s'.",
                    field.name,
                    custom_object_key,
                )
        return custom_object, created

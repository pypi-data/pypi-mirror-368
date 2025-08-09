"""
This module handles the management of custom object records for integration
with the Zendesk API, including creating, retrieving, and deleting records.
"""

import requests
from mercuryorm.managers import BulkActions, QuerySet
from mercuryorm.zendesk_manager import ZendeskAPIClient
from mercuryorm.exceptions import (
    BadRequestError,
    BulkRecordsError,
    DeleteRecordError,
    NotFoundError,
)


class RecordManager:
    """
    Manages custom object records by interacting with the Zendesk API.
    Provides methods to create, retrieve, filter, and delete records.
    """

    def __init__(self, model):
        self.model = model
        self.queryset = QuerySet(model)
        self.client = ZendeskAPIClient()
        self.bulk = Bulk(self.queryset)

    def create(self, **kwargs):
        """
        Creates a new record for the Custom Object.
        """
        record = self.model(**kwargs)
        return record.save()

    def get(self, **kwargs):
        """
        Returns a single record based on the given parameters.
        If 'id' is given, searches directly by URL.
        Otherwise, uses the filter method for other criteria.
        """
        if "id" in kwargs:
            record_id = kwargs.pop("id")
            try:
                response = self.client.get(
                    f"/custom_objects/{self.model.__name__.lower()}/records/{record_id}"
                )
            except requests.exceptions.HTTPError as e:  # pylint: disable=invalid-name
                if e.response.status_code == 400:
                    error_response = e.response.json()
                    raise BadRequestError(
                        f"Bad request for record with ID {record_id}. Response: {error_response}"
                    ) from e
                if e.response.status_code == 404:
                    raise NotFoundError(self.model.__name__, record_id) from e
                raise e
            record_data = response.get("custom_object_record", {})
            record = self.model.parse_record_fields(**record_data)
            return record

        result = self.filter(**kwargs)
        if len(result) == 0:
            raise ValueError(f"{self.model.__name__} matching query does not exist.")
        if len(result) > 1:
            raise ValueError(
                f"Multiple {self.model.__name__} objects returned; expected exactly one."
            )
        return result[0]

    def all(self):
        """
        Returns all records using QuerySet.
        """
        return self.queryset.all()

    def all_paginated(self, page_size=100, after_cursor=None, before_cursor=None):
        """
        Returns all records using QuerySet.
        """
        return self.queryset.all_with_pagination(
            page_size=page_size, after_cursor=after_cursor, before_cursor=before_cursor
        )

    def filter(self, **criteria):
        """
        Filters records based on the given criteria using QuerySet.
        """
        return self.queryset.filter(**criteria)

    def delete(self, record_id):
        """
        Deletes a record by ID.

        Raises:
            DeleteRecordError: If the record could not be deleted.
        """
        response = self.client.delete(
            f"/custom_objects/{self.model.__name__.lower()}/records/{record_id}"
        )
        if response.get("status_code", 204) != 204:
            raise DeleteRecordError(
                message=response.get("description", "Error deleting record")
            )

        return response

    def last(self):
        """
        Returns the last record based on the update date (updated_at).
        Sorts the records by 'updated_at' in descending order and returns the first one.
        """
        params = {"sort": "-updated_at", "page[size]": 1}

        response = self.client.get(
            f"/custom_objects/{self.model.__name__.lower()}/records", params=params
        )

        if response.get("custom_object_records"):
            record = self.model.parse_record_fields(
                **response["custom_object_records"][0]
            )
            return record
        return None

    def search(self, word):
        """
        Returns the object with a word.
        """
        results = []
        response = self.client.get(
            f"/custom_objects/{self.model.__name__.lower()}/records/search?query={word}&sort="
        )
        if response.get("custom_object_records"):
            records = response.get("custom_object_records", [])
            for record in records:
                results.append(self.model.parse_record_fields(**record))
        return results

    def search_paginated(
        self, word, page_size=10, after_cursor=None, before_cursor=None
    ):
        """
        Returns paginated search results with a word.
        """
        return self.queryset.search_with_pagination(
            word=word,
            page_size=page_size,
            after_cursor=after_cursor,
            before_cursor=before_cursor,
        )

    def find(self, filters):
        """
        Returns a list of records based on a filter.
        """
        return self.queryset.find(filters)

    def find_paginated(
        self, filters, page_size=100, after_cursor=None, before_cursor=None
    ):
        """
        Returns paginated search results with a filter.
        """
        return self.queryset.find_with_pagination(
            filters=filters,
            page_size=page_size,
            after_cursor=after_cursor,
            before_cursor=before_cursor,
        )


class Bulk:
    """
    Manages the creation of multiple records in bulk.
    """

    def __init__(self, queryset):
        self.queryset = queryset

    def _validate(self, field: str, records: list):
        """
        Validates the field to be used in the bulk action.

        Raises:
            BulkRecordsError: If the field is not present in all records.
        """
        for record in records:
            if not getattr(record, field):
                raise BulkRecordsError(
                    f"Every Record will contain the field: '{field}'."
                )

    def create(self, records: list, wait_to_complete: bool = True):
        """
        Creates multiple records in bulk.

        Args:
            records (list[CustomObject]): A list of records to create.
        """
        return self.queryset.bulk(records, BulkActions.CREATE, wait_to_complete)

    def update(self, records: list, wait_to_complete: bool = True):
        """
        Updates multiple records in bulk.

        Args:
            records (list[CustomObject]): A list of records to update.
        """
        self._validate("id", records)
        return self.queryset.bulk(records, BulkActions.UPDATE, wait_to_complete)

    def delete(self, records: list, wait_to_complete: bool = False):
        """
        Deletes multiple records in bulk.

        Args:
            records (list[CustomObject]): A list of records to delete.
        """
        self._validate("id", records)
        return self.queryset.bulk(records, BulkActions.DELETE, wait_to_complete)

    def delete_by_external_id(self, records: list, wait_to_complete: bool = False):
        """
        Deletes multiple records by external ID in bulk.

        Args:
            records (list[CustomObject]): A list of records to delete,
            every will have to have a external_id.
        """
        self._validate("external_id", records)
        return self.queryset.bulk(records, BulkActions.DELETE_BY_EXTERNAL_ID, wait_to_complete)

    def create_or_update_by_external_id(self, records: list, wait_to_complete: bool = True):
        """
        Creates or updates multiple records by external ID in bulk.

        Args:
            records (list[CustomObject]): A list of records to create or update,
            every will have to have a external_id.
        """
        self._validate("external_id", records)
        return self.queryset.bulk(
            records,
            BulkActions.CREATE_OR_UPDATE_BY_EXTERNAL_ID,
            wait_to_complete
        )

    def create_or_update_by_name(self, records: list, wait_to_complete: bool = True):
        """
        Creates or updates multiple records by name in bulk.

        Args:
            records (list[CustomObject]): A list of records to create or update,
            every will have to have a name.
        """
        self._validate("name", records)
        return self.queryset.bulk(records, BulkActions.CREATE_OR_UPDATE_BY_NAME, wait_to_complete)

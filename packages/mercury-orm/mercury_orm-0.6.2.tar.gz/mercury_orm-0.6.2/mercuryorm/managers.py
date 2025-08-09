"""
For Manager and querysets to Records CustomObject
"""

import time

from enum import Enum
from urllib.parse import parse_qs, urlparse
from mercuryorm.client.connection import ZendeskAPIClient
from mercuryorm.exceptions import BulkRecordsError


class BulkActions(Enum):
    """
    Enumeration of the bulk operations on records.

    Attributes:
        CREATE: Create records in bulk.
        UPDATE: Update records in bulk.
        DELETE_BY_EXTERNAL_ID: Delete records by external ID in bulk.
        CREATE_OR_UPDATE_BY_EXTERNAL_ID: Create or update records by external ID in bulk.
        CREATE_OR_UPDATE_BY_NAME: Create or update records by name in bulk.
        DELETE: Delete records in bulk.
    """

    CREATE = "create"
    UPDATE = "update"
    DELETE_BY_EXTERNAL_ID = "delete_by_external_id"
    CREATE_OR_UPDATE_BY_EXTERNAL_ID = "create_or_update_by_external_id"
    CREATE_OR_UPDATE_BY_NAME = "create_or_update_by_name"
    DELETE = "delete"


class QuerySet:
    """
    For Manager and querysets to Records CustomObject.
    """

    def __init__(self, model):
        self.model = model
        self.base_url = f"/custom_objects/{self.model.__name__.lower()}/records"
        self.client = ZendeskAPIClient()

    def all(self):
        """
        Returns the 100 first records from the Custom Object without metadata or links.
        """
        records = []
        next_cursor = None

        while True:
            params = {"page[size]": 100}
            if next_cursor:
                params["page[after]"] = next_cursor

            response = self.client.get(self.base_url, params=params)

            if "error" in response:
                raise ValueError(
                    f"Error from Zendesk API: {response['error']} - {response.get('description')}"
                )

            records.extend(self._parse_response(response))

            links = response.get("links", {})
            next_cursor_url = links.get("next")

            if not next_cursor_url:
                break

            parsed_url = urlparse(next_cursor_url)
            next_cursor = parse_qs(parsed_url.query).get("page[after]", [None])[0]
        return records

    def all_with_pagination(self, page_size=100, after_cursor=None, before_cursor=None):
        """
        Returns a paginated response including metadata and links.
        """
        params = {"page[size]": page_size}
        if after_cursor:
            params["page[after]"] = after_cursor
        if before_cursor:
            params["page[before]"] = before_cursor

        response = self.client.get(self.base_url, params=params)

        if "error" in response:
            raise ValueError(
                f"Error from Zendesk API: {response['error']} - {response.get('description')}"
            )

        return {
            "count": self.count(),
            "results": self._parse_response(response),
            "meta": response.get("meta", {}),
            "links": response.get("links", {}),
        }

    def find(self, filters):
        """
        Returns a list of records that match the specified filter.
        The filter is a dictionary and can take the following forms:
            - A single dictionary with a key (field_name) and a value
            that is another dictionary containing an operator and a value.
            - Key(s) named `$and` or `$or`, where the value is a
            list of dictionaries. Each dictionary contains a key (field_name) and a value
            that is another dictionary with an operator and a value.
        """
        records = []
        next_cursor = None

        while True:
            params = {"page[size]": 100}
            if next_cursor:
                params["page[after]"] = next_cursor

            response = self.client.post(
                self.base_url + "/search",
                data={"filter": filters},
                params=params,
            )

            if "error" in response:
                raise ValueError(
                    f"Error from Zendesk API: {response['error']} - {response.get('description')}"
                )

            records.extend(self._parse_response(response))
            links = response.get("links", {})
            next_cursor_url = links.get("next")

            if not next_cursor_url:
                break
            # Extract value from 'page[after]' of URL 'next'
            # Example "next_cursor_url": "/custom_objects/myobject/records?page[after]=xyz"
            parsed_url = urlparse(next_cursor_url)
            next_cursor = parse_qs(parsed_url.query).get("page[after]", [None])[0]
        return records

    def find_with_pagination(
        self, filters, page_size=100, after_cursor=None, before_cursor=None
    ):
        """
        Returns a paginated response including metadata and links.
        The instrunctions for the filter are the same as the find method.
        """
        params = {"page[size]": page_size}
        if after_cursor:
            params["page[after]"] = after_cursor
        if before_cursor:
            params["page[before]"] = before_cursor

        response = self.client.post(
            self.base_url + "/search", data={"filter": filters}, params=params
        )

        if "error" in response:
            raise ValueError(
                f"Error from Zendesk API: {response['error']} - {response.get('description')}"
            )

        return {
            "count": response.get("count", ""),
            "results": self._parse_response(response),
            "meta": response.get("meta", {}),
            "links": response.get("links", {}),
        }

    def search_with_pagination(
        self, word, page_size=100, after_cursor=None, before_cursor=None
    ):
        """
        Returns paginated search results with a word.
        """
        params = {"query": word, "sort": "", "page[size]": page_size}
        if after_cursor:
            params["page[after]"] = after_cursor
        if before_cursor:
            params["page[before]"] = before_cursor

        response = self.client.get(
            f"/custom_objects/{self.model.__name__.lower()}/records/search",
            params=params,
        )

        results = []
        if response.get("custom_object_records"):
            records = response.get("custom_object_records", [])
            for record in records:
                results.append(self.model.parse_record_fields(**record))

        return {
            "count": response.get("count", ""),
            "results": results,
            "meta": response.get("meta", {}),
            "links": response.get("links", {}),
        }

    def filter(self, **kwargs):
        """
        Filters records in memory based on the parameters provided.
        The Zendesk API does not support native filtering by custom fields, so
        we take all records and filter them locally.
        """
        records = self.all()

        filtered_records = []
        for record in records:
            match = True
            for key, value in kwargs.items():
                if getattr(record, key, None) != value:
                    match = False
                    break
            if match:
                filtered_records.append(record)

        return filtered_records

    def count(self):
        """
        Deletes a record by ID.
        """
        response = self.client.get(
            f"/custom_objects/{self.model.__name__.lower()}/records/count"
        )
        return response["count"]["value"]

    def bulk(
        self, records: list, action: BulkActions, wait_to_complete: bool = False
    ):  # pylint: disable=too-many-locals, too-many-branches
        """
        Create, update, delete records in bulk, using the Bulk API.

        Args:
            records (list): List of records to be created, updated or deleted.

        Returns:
            dict: Response from the API.
        """
        if not records:
            return []

        start = 0
        end = 100
        limit = len(records)

        responses = []

        while True:
            if action == BulkActions.DELETE:
                items = [
                    record.format_record()["custom_object_record"]["id"]
                    for record in records[start:end]
                ]
            elif action == BulkActions.DELETE_BY_EXTERNAL_ID:
                items = [
                    record.format_record()["custom_object_record"]["external_id"]
                    for record in records[start:end]
                ]
            else:
                items = [
                    record.format_record()["custom_object_record"]
                    for record in records[start:end]
                ]

            data = {
                "job": {
                    "action": action.value,
                    "items": items,
                }
            }

            responses.append(
                self.client.post(
                    f"/custom_objects/{self.model.__name__.lower()}/jobs", data
                )
            )

            start = end
            if end >= limit:
                break
            if end + 100 > limit:
                end = limit
            else:
                end += 100

        if wait_to_complete:
            WAIT_TIMEOUT = 120  # pylint: disable=invalid-name
            for response in responses:
                status = response["job_status"]["status"]
                url = response["job_status"]["url"].replace(
                    ZendeskAPIClient.BASE_URL, ""
                )
                start_time = time.time()

                while status != "completed":
                    if time.time() - start_time > WAIT_TIMEOUT:
                        raise BulkRecordsError(
                            "Timeout exceeded while waiting for bulk operation to complete."
                        )

                    responses_status = self.client.get(url)
                    status = responses_status["job_status"]["status"]
                    response.update(responses_status)

                    if status in ["failed", "aborted"]:
                        break

        return responses

    def _parse_response(self, response):
        """
        Internal method to process the API response and extract the records.
        """
        records = []
        for record_data in response.get("custom_object_records", []):
            record = self.model.parse_record_fields(**record_data)
            records.append(record)
        return records

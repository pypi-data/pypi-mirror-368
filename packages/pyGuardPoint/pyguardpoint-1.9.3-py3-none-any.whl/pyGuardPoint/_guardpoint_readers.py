import validators
from ._odata_filter import _compose_filter
from .guardpoint_utils import GuardPointResponse
from .guardpoint_dataclasses import Reader
from .guardpoint_error import GuardPointError, GuardPointUnauthorized


class ReadersAPI:
    """
    A class to interact with the Readers API.

    Methods
    -------
    get_readers():
        Retrieves a list of all readers from the API.

    get_reader(reader_uid: str):
        Retrieves a specific reader by its unique identifier (UID).
    """

    def get_readers(self, offset: int = 0, limit: int = 500, **reader_kwargs):
        """
        Retrieve a list of readers from the GuardPoint API.

        This method sends a GET request to the GuardPoint API to fetch a list of readers.
        It processes the response and returns a list of `Reader` objects.

        :raises GuardPointUnauthorized: If the API response status code is 401 (Unauthorized).
        :raises GuardPointError: If the API response status code is 404 (Not Found) or any other error occurs.
        :raises GuardPointError: If the response is not properly formatted.

        :return: A list of `Reader` objects.
        :rtype: list
        """
        readers = []

        if limit <= 0:
            return readers
        if limit > 50:
            i_offset = offset
            offset = 0
            batch_limit = 40
            while len(readers) == offset:
                if offset + batch_limit > limit:
                    batch_limit = limit - offset
                if batch_limit > 0:
                    readers.extend(self.get_readers(offset=offset + i_offset, limit=batch_limit))
                if (offset + batch_limit) >= limit:
                    break
                elif len(readers) > offset:
                    offset = len(readers)
                else:
                    break
            return readers
        else:
            url = "/odata/API_Readers"
            headers = {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }

            # Filter arguments which have to exact match
            match_args = dict()
            for k, v in reader_kwargs.items():
                if hasattr(Reader, k):
                    match_args[k] = v

            # Force site_uid filter if present
            if self.site_uid is not None:
                if 'ownerSiteUID' in match_args:
                    match_args['ownerSiteUID'] = self.site_uid

            filter_str = _compose_filter(exact_match=match_args)
            url_query_params = ("?" + filter_str)
            url_query_params += "$top=" + str(limit) + "&$skip=" + str(offset)

            code, json_body = self.gp_json_query("GET", headers=headers, url=(url + url_query_params))

            if code != 200:
                error_msg = GuardPointResponse.extract_error_msg(json_body)

                if code == 401:
                    raise GuardPointUnauthorized(f"Unauthorized - ({error_msg})")
                elif code == 404:  # Not Found
                    raise GuardPointError(f"Cardholder Not Found")
                else:
                    raise GuardPointError(f"{error_msg}")

            if not isinstance(json_body, dict):
                raise GuardPointError("Badly formatted response.")
            if 'value' not in json_body:
                raise GuardPointError("Badly formatted response.")
            if not isinstance(json_body['value'], list):
                raise GuardPointError("Badly formatted response.")

            readers = []
            for x in json_body['value']:
                readers.append(Reader(x))

            return readers

    def get_reader(self, reader_uid: str):
        """
        Retrieve a reader's information from the API using the provided reader UID.

        This method sends a GET request to the `/odata/API_Readers` endpoint with the specified
        `reader_uid` to fetch the reader's details. It validates the `reader_uid` to ensure it is
        a properly formatted UUID and handles various error conditions that may arise during the
        request.

        :param reader_uid: The unique identifier of the reader to be retrieved.
        :type reader_uid: str
        :raises ValueError: If the `reader_uid` is not a valid UUID.
        :raises GuardPointError: If the API response indicates an error or is improperly formatted.
        :return: An instance of the `Reader` class containing the reader's details.
        :rtype: Reader
        """
        if not validators.uuid(reader_uid):
            raise ValueError(f"Malformed reader_uid: {reader_uid}")

        url = "/odata/API_Readers"
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        }

        url_query_params = f"({reader_uid})"

        code, json_body = self.gp_json_query("GET", headers=headers, url=(url + url_query_params))

        if code != 200:
            if isinstance(json_body, dict):
                if 'error' in json_body:
                    raise GuardPointError(json_body['error'])
            else:
                raise GuardPointError(str(code))

        # Check response body is formatted as expected
        if not isinstance(json_body, dict):
            raise GuardPointError("Badly formatted response.")
        if 'value' not in json_body:
            raise GuardPointError("Badly formatted response.")

        return Reader(json_body['value'])


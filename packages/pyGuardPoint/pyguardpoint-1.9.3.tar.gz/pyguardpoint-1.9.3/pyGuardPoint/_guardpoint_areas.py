from .guardpoint_utils import GuardPointResponse
from .guardpoint_dataclasses import Area
from .guardpoint_error import GuardPointError, GuardPointUnauthorized


class AreasAPI:
    """
    A class to interact with the Areas API.

    Methods
    -------
    get_areas():
        Fetches a list of areas from the API and returns them as a list of Area objects.
    """
    def get_areas(self):
        """
        Retrieve a list of areas from the GuardPoint API.

        This method sends a GET request to the GuardPoint API to fetch a list of areas.
        It processes the response and returns a list of `Area` objects.

        :raises GuardPointUnauthorized: If the API response status code is 401 (Unauthorized).
        :raises GuardPointError: If the API response status code is 404 (Not Found) or any other error occurs.
        :raises GuardPointError: If the response is not properly formatted.

        :return: A list of `Area` objects.
        :rtype: list
        """
        url = "/odata/API_Areas"
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

        code, json_body = self.gp_json_query("GET", headers=headers, url=url)

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

        areas = []
        for x in json_body['value']:
            areas.append(Area(x))
        return areas
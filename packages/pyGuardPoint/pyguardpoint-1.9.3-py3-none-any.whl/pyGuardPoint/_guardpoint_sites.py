import validators

from .guardpoint_dataclasses import Site
from .guardpoint_utils import GuardPointResponse
from .guardpoint_error import GuardPointError, GuardPointUnauthorized


class SitesAPI:
    def get_site(self, site_uid):
        """
        Retrieve a site by its unique identifier (UID).

        This method fetches the details of a site from the GuardPoint API using the provided site UID.
        It validates the UID, constructs the appropriate API request, and handles the response.

        :param site_uid: The unique identifier of the site to retrieve.
        :type site_uid: str
        :raises ValueError: If the provided site_uid is not a valid UUID.
        :raises GuardPointUnauthorized: If the API response indicates an unauthorized request (HTTP 401).
        :raises GuardPointError: If the site is not found (HTTP 404) or if there is any other error in the response.
        :return: An instance of the Site class if the site is found, otherwise None.
        :rtype: Site or None
        """
        if not validators.uuid(site_uid):
            raise ValueError(f"Malformed site_uid: {site_uid}")

        url = f"/odata/API_Sites({site_uid})"
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
                raise GuardPointError(f"Site Not Found")
            else:
                raise GuardPointError(f"{error_msg}")

        if not isinstance(json_body, dict):
            raise GuardPointError("Badly formatted response.")
        if 'value' not in json_body:
            raise GuardPointError("Badly formatted response.")

        if len(json_body['value']) > 0:
            return Site(json_body['value'][0])
        else:
            return None

    def get_sites(self):
        """
        Retrieve a list of sites from the GuardPoint API.

        This method sends a GET request to the GuardPoint API to fetch a list of sites.
        It handles various HTTP response codes and raises appropriate exceptions for
        error conditions.

        :raises GuardPointUnauthorized: If the API response code is 401 (Unauthorized).
        :raises GuardPointError: If the API response code is 404 (Not Found) or any other error occurs.
        :raises GuardPointError: If the response is not properly formatted.

        :return: A list of Site objects representing the sites retrieved from the API.
        :rtype: list
        """
        url = "/odata/API_Sites"
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
                raise GuardPointError(f"Site Not Found")
            else:
                raise GuardPointError(f"{error_msg}")

        if not isinstance(json_body, dict):
            raise GuardPointError("Badly formatted response.")
        if 'value' not in json_body:
            raise GuardPointError("Badly formatted response.")
        if not isinstance(json_body['value'], list):
            raise GuardPointError("Badly formatted response.")

        sites = []
        for x in json_body['value']:
            sites.append(Site(x))
        return sites

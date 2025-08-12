from ._odata_filter import _compose_filter
from .guardpoint_utils import GuardPointResponse
from .guardpoint_dataclasses import SecurityGroup
from .guardpoint_error import GuardPointError, GuardPointUnauthorized


class SecurityGroupsAPI:
    """
    A class to interact with the Security Groups API.

    Methods
    -------
    get_security_groups():
        Retrieves a list of security groups from the API.
    """
    def get_security_groups(self):
        """
        Retrieve a list of security groups from the GuardPoint API.

        This method sends a GET request to the GuardPoint API to fetch security groups.
        It handles various HTTP response codes and raises appropriate exceptions for
        unauthorized access, not found errors, and other errors. The response is expected
        to be a JSON object containing a list of security groups.

        :raises GuardPointUnauthorized: If the API response code is 401 (Unauthorized).
        :raises GuardPointError: If the API response code is 404 (Not Found) or any other error occurs.
        :raises GuardPointError: If the response body is not formatted as expected.

        :return: A list of SecurityGroup objects.
        :rtype: list
        """
        url = self.baseurl + "/odata/api_SecurityGroups"
        url_query_params = "?"

        if self.site_uid is not None:
            match_args = {'ownerSiteUID': self.site_uid}
            filter_str = _compose_filter(exact_match=match_args)
            url_query_params += ("&" + filter_str)

        code, json_body = self.gp_json_query("GET", url=(url + url_query_params))

        if code != 200:
            error_msg = GuardPointResponse.extract_error_msg(json_body)

            if code == 401:
                raise GuardPointUnauthorized(f"Unauthorized - ({error_msg})")
            elif code == 404:  # Not Found
                raise GuardPointError(f"Security Group Not Found")
            else:
                raise GuardPointError(f"{error_msg}")

        # Check response body is formatted as expected
        if not isinstance(json_body, dict):
            raise GuardPointError("Badly formatted response.")
        if 'value' not in json_body:
            raise GuardPointError("Badly formatted response.")
        if not isinstance(json_body['value'], list):
            raise GuardPointError("Badly formatted response.")

        # Compose list of security groups
        security_groups = []
        for entry in json_body['value']:
            if isinstance(entry, dict):
                sg = SecurityGroup(entry)
                security_groups.append(sg)
        return security_groups

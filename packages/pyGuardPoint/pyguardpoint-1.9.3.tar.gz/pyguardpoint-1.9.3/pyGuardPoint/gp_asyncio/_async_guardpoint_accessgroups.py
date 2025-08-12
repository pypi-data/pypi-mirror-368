from .._odata_filter import _compose_filter
from ..guardpoint_utils import GuardPointResponse
from ..guardpoint_dataclasses import AccessGroup
from ..guardpoint_error import GuardPointError, GuardPointUnauthorized


class AccessGroupsAPI:

    async def get_access_groups(self):
        url = self.baseurl + "/odata/api_AccessGroups"
        url_query_params = "?"

        if self.site_uid is not None:
            match_args = {'ownerSiteUID': self.site_uid}
            filter_str = _compose_filter(exact_match=match_args)
            url_query_params += ("&" + filter_str)

        code, json_body = await self.gp_json_query("GET", url=(url + url_query_params))

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
        access_groups = []
        for entry in json_body['value']:
            if isinstance(entry, dict):
                sg = AccessGroup(entry)
                access_groups.append(sg)
        return access_groups

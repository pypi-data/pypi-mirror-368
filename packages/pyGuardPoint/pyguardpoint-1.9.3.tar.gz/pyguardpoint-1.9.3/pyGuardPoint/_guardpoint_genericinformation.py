import json
from json import JSONDecodeError

import validators
from .guardpoint_utils import GuardPointResponse
from .guardpoint_error import GuardPointError, GuardPointUnauthorized


class GenericInfoAPI:
    def get_info(self, info_uid):

        if not validators.uuid(info_uid):
            raise ValueError(f"Malformed site_uid: {info_uid}")

        url = f"/odata/API_GenericInformations({info_uid})"
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
        if 'serializedData' not in json_body:
            raise GuardPointError("Badly formatted response.")

        if len(json_body['serializedData']) > 0:
            try:
                return json.loads(json_body['serializedData'])
            except JSONDecodeError as e:
                return json_body['serializedData']
        else:
            return None

    def get_infos(self):

        url = "/odata/API_GenericInformations"
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

        return json_body

    def is_sigr_enabled(self):
        info = self.get_info('00000000-0000-0000-0000-000000000003')
        return info['CommunicationSettings']['PassEventsToApi']['Value']

    def gp_version(self):
        return self.get_info('00000000-0000-0000-0000-000000000011')

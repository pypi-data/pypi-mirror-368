import validators

from .guardpoint_dataclasses import Relay
from .guardpoint_utils import GuardPointResponse
from .guardpoint_error import GuardPointError, GuardPointUnauthorized


class OutputsAPI:

    def get_relay(self, relay_uid):
        url = self.baseurl + "/odata/API_Outputs"
        url_query_params = f"({relay_uid})"
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        }
        code, json_body = self.gp_json_query("GET", headers=headers, url=(url + url_query_params))

        if code != 200:
            error_msg = GuardPointResponse.extract_error_msg(json_body)

            if code == 401:
                raise GuardPointUnauthorized(f"Unauthorized - ({error_msg})")
            elif code == 404:  # Not Found
                return None
            else:
                raise GuardPointError(f"{error_msg}")

        # Check response body is formatted as expected
        if not isinstance(json_body, dict):
            raise GuardPointError("Badly formatted response.")
        if 'value' not in json_body:
            raise GuardPointError("Badly formatted response.")
        if not isinstance(json_body['value'], list):
            raise GuardPointError("Badly formatted response.")

        return Relay(json_body['value'][0])


    def get_relays(self):
        url = self.baseurl + "/odata/API_Outputs"

        code, json_body = self.gp_json_query("GET", url=url)

        if code != 200:
            error_msg = GuardPointResponse.extract_error_msg(json_body)

            if code == 401:
                raise GuardPointUnauthorized(f"Unauthorized - ({error_msg})")
            elif code == 404:  # Not Found
                raise GuardPointError(f"No Outputs Found")
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
        relays = []
        for entry in json_body['value']:
            if isinstance(entry, dict):
                relay = Relay(entry)
                relays.append(relay)
        return relays

    def activate_relay(self, relay: Relay, period: int = 0):
        return self.activate_relay_by_uid(relay.uid, period)

    def activate_relay_by_uid(self, relay_uid: str, period: int = 0):

        url = self.baseurl + "/odata/API_Outputs/Activate"
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        }

        if not validators.uuid(relay_uid):
            raise ValueError("Malformed Relay UID")

        body = dict()
        body["uids"] = [relay_uid]
        body["period"] = period

        code, json_body = self.gp_json_query("POST", headers=headers, url=url, json_body=body)

        if code != 200:
            error_msg = GuardPointResponse.extract_error_msg(json_body)
            if isinstance(json_body, dict):
                if len(json_body) == 1:
                    r_uid = list(json_body.keys())[0]
                    if validators.uuid(r_uid):
                        if 'item1' in json_body[r_uid]:
                            error_msg = GuardPointResponse.extract_error_msg(json_body[r_uid]['item1'])

            if code == 401:
                raise GuardPointUnauthorized(f"Unauthorized - ({error_msg})")
            elif code == 404:  # Not Found
                raise GuardPointError(f"Relay Not Found")
            else:
                raise GuardPointError(f"{error_msg}")

        return True

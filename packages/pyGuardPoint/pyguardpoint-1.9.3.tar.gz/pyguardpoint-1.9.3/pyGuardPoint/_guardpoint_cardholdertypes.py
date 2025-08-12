from .guardpoint_utils import GuardPointResponse
from .guardpoint_dataclasses import CardholderType
from .guardpoint_error import GuardPointError, GuardPointUnauthorized


class CardholderTypesAPI:
    def get_cardholder_types(self):
        url = "/odata/API_CardholderTypes"
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
                raise GuardPointError(f"CardholderType Not Found")
            else:
                raise GuardPointError(f"{error_msg}")

        if not isinstance(json_body, dict):
            raise GuardPointError("Badly formatted response.")
        if 'value' not in json_body:
            raise GuardPointError("Badly formatted response.")
        if not isinstance(json_body['value'], list):
            raise GuardPointError("Badly formatted response.")

        cardholder_types = []
        for x in json_body['value']:
            cardholder_types.append(CardholderType(x))
        return cardholder_types

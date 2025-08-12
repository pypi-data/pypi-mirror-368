import validators
from .guardpoint_utils import GuardPointResponse
from .guardpoint_dataclasses import ScheduledMag, Cardholder
from .guardpoint_error import GuardPointError, GuardPointUnauthorized


class ScheduledMagsAPI:

    def get_scheduled_mags(self, cardholder: Cardholder = None):
        url = self.baseurl + "/odata/API_ScheduledMags"
        if cardholder:
            if not validators.uuid(cardholder.uid):
                raise ValueError(f'Malformed Cardholder UID {cardholder.uid}')
            url_query_params = f"?$filter=cardholderUid%20eq%20'{cardholder.uid}'"
        else:
            url_query_params = ""

        code, json_body = self.gp_json_query("GET", url=(url + url_query_params))

        if code != 200:
            error_msg = GuardPointResponse.extract_error_msg(json_body)

            if code == 401:
                raise GuardPointUnauthorized(f"Unauthorized - ({error_msg})")
            elif code == 404:  # Not Found
                raise GuardPointError(f"MAG Not Found")
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
        scheduled_mags = []
        for entry in json_body['value']:
            if isinstance(entry, dict):
                sm = ScheduledMag(entry)
                scheduled_mags.append(sm)
        return scheduled_mags

    def add_scheduled_mag(self, scheduled_mag: ScheduledMag):
        url = self.baseurl + "/odata/API_ScheduledMags"
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        }
        body = scheduled_mag.dict(editable_only=True)

        code, json_body = self.gp_json_query("POST", headers=headers, url=url, json_body=body)

        if code == 201:  # HTTP CREATED
            return json_body['uid']
        else:
            if 'value' in json_body:
                if isinstance(json_body['value'], list):
                    json_body = json_body['value'][0]
            else:
                error_msg = GuardPointResponse.extract_error_msg(json_body)

                if code == 401:
                    raise GuardPointUnauthorized(f"Unauthorized - ({error_msg})")
                elif code == 404:  # Not Found
                    raise GuardPointError(f"Cardholder Not Found")
                else:
                    raise GuardPointError(f"{error_msg}")
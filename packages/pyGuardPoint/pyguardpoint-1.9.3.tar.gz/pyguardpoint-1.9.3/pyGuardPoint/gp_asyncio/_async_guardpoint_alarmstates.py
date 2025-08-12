import validators

from ..guardpoint_utils import GuardPointResponse
from ..guardpoint_dataclasses import AlarmState
from ..guardpoint_error import GuardPointError, GuardPointUnauthorized


class AlarmStatesAPI:
    async def get_alarm_state(self, alarm_uid):
        if not validators.uuid(alarm_uid):
            raise ValueError(f"Malformed alarm_uid: {alarm_uid}")

        url = f"/odata/API_AlarmStates({alarm_uid})?=&$expand=Input"
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

        code, json_body = await self.gp_json_query("GET", headers=headers, url=url)

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

        return AlarmState(json_body['value'])

    async def get_alarm_states(self):
        url = "/odata/API_AlarmStates?=&$expand=Input"
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

        code, json_body = await self.gp_json_query("GET", headers=headers, url=url)

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

        alarm_states = []
        for x in json_body['value']:
            alarm_states.append(AlarmState(x))
        return alarm_states

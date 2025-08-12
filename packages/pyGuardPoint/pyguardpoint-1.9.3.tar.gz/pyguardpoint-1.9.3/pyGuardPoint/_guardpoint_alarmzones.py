from enum import Enum

import validators

from .guardpoint_dataclasses import AlarmZone, AlarmZoneOption
from .guardpoint_utils import GuardPointResponse
from .guardpoint_error import GuardPointError, GuardPointUnauthorized


class AlarmZonesAPI:

    def arm_alarm_zone(self, alarm_zone: AlarmZone, option=AlarmZoneOption.ReturnAlarmZoneToWeeklyProgram):
        if option == AlarmZoneOption.ReturnAlarmZoneToWeeklyProgram:
            url = self.baseurl + "/odata/API_AlarmZones/ReturnAlarmZoneToWeeklyProgram"
        else:
            raise GuardPointError(f"Unsupported Arming Option")

        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        }

        body = dict()
        body['uid'] = alarm_zone.uid

        code, json_body = self.gp_json_query("POST", headers=headers, url=url, json_body=body)

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
        if 'success' in json_body:
            if json_body['success']:
                return True

    def disarm_alarm_zone(self, alarm_zone: AlarmZone):
        url = self.baseurl + "/odata/API_AlarmZones/DisarmAlarmZone"
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        }

        body = dict()
        body["uid"] = alarm_zone.uid
        body["disarmType"] = "DisarmUntilNextIntervalInWP"
        body["period"] = "1"
        body["isMinute"] = "true"

        code, json_body = self.gp_json_query("POST", headers=headers, url=url, json_body=body)

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
        if 'success' in json_body:
            if json_body['success']:
                return True

    def get_alarm_zone(self, zone_uid):
        url = self.baseurl + "/odata/API_AlarmZones"
        url_query_params = f"({zone_uid})"
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

        return AlarmZone(json_body['value'][0])

    def get_alarm_zones(self):
        url = self.baseurl + "/odata/API_AlarmZones"

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
        alarm_zones = []
        for entry in json_body['value']:
            if isinstance(entry, dict):
                relay = AlarmZone(entry)
                alarm_zones.append(relay)
        return alarm_zones

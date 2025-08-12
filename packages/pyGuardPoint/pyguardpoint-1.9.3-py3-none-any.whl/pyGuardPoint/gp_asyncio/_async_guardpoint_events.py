from enum import Enum

from .._odata_filter import _compose_filter
from ..guardpoint_utils import GuardPointResponse
from ..guardpoint_dataclasses import AccessEvent, AlarmEvent, EventOrder, AuditEvent
from ..guardpoint_error import GuardPointError, GuardPointUnauthorized


class EventsAPI:

    @staticmethod
    def _build_url_params(site_uid, limit, offset, count, orderby, min_log_id):
        if count:
            url_query_params = "?$count=true&$top=0"
        else:
            if orderby == EventOrder.DATETIME_ASC:
                url_query_params = "?$orderby=dateTime%20asc"
            elif orderby == EventOrder.DATETIME_DESC:
                url_query_params = "?$orderby=dateTime%20desc"
            elif orderby == EventOrder.LOG_ID_ASC:
                url_query_params = "?$orderby=logID%20asc"
            else:
                url_query_params = "?$orderby=logID%20desc"

        greater_than_args = None
        if min_log_id is not None and min_log_id > 0:
            greater_than_args = {'logID': min_log_id}

        match_args = None
        if site_uid is not None:
            match_args = {'ownerSiteUID': site_uid}

        if match_args is not None or greater_than_args is not None:
            filter_str = _compose_filter(exact_match=match_args, greater_than=greater_than_args)
            url_query_params += ("&" + filter_str)

        if limit:
            url_query_params += "&$top=" + str(limit)
        if offset:
            url_query_params += "&$skip=" + str(offset)

        return url_query_params

    async def get_access_events_count(self):
        return await self.get_access_events(limit=None, offset=None, count=True, orderby=EventOrder.DATETIME_DESC)

    async def get_access_events(self, limit=None, offset=None, count=False, orderby=EventOrder.DATETIME_DESC,
                          min_log_id=None):
        url = f"/odata/API_AccessEventLogs"
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

        url_query_params = EventsAPI._build_url_params(self.site_uid, limit, offset, count, orderby, min_log_id)

        code, json_body = await self.gp_json_query("GET", headers=headers, url=(url + url_query_params))

        if code != 200:
            error_msg = GuardPointResponse.extract_error_msg(json_body)

            if code == 401:
                raise GuardPointUnauthorized(f"Unauthorized - ({error_msg})")
            elif code == 404:  # Not Found
                raise GuardPointError(f"Access Events Not Found")
            else:
                raise GuardPointError(f"{error_msg}")

        # Check response body is formatted as expected
        if not isinstance(json_body, dict):
            raise GuardPointError("Badly formatted response.")
        if 'value' not in json_body:
            raise GuardPointError("Badly formatted response.")
        if not isinstance(json_body['value'], list):
            raise GuardPointError("Badly formatted response.")

        if count:
            return json_body['@odata.count']
        else:
            access_events = []
            for x in json_body['value']:
                access_events.append(AccessEvent(x))
            return access_events

    async def get_alarm_events_count(self):
        return await self.get_alarm_events(limit=None, offset=None, count=True, orderby=EventOrder.DATETIME_DESC)

    async def get_alarm_events(self, limit=None, offset=None, count=False, orderby=EventOrder.DATETIME_DESC):
        url = "/odata/API_AlarmEventLogs"
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

        url_query_params = EventsAPI._build_url_params(self.site_uid, limit, offset, count, orderby, None)

        code, json_body = await self.gp_json_query("GET", headers=headers, url=(url + url_query_params))

        if code != 200:
            error_msg = GuardPointResponse.extract_error_msg(json_body)

            if code == 401:
                raise GuardPointUnauthorized(f"Unauthorized - ({error_msg})")
            elif code == 404:  # Not Found
                raise GuardPointError(f"Alarm Events Not Found")
            else:
                raise GuardPointError(f"{error_msg}")

        if not isinstance(json_body, dict):
            raise GuardPointError("Badly formatted response.")
        if 'value' not in json_body:
            raise GuardPointError("Badly formatted response.")
        if not isinstance(json_body['value'], list):
            raise GuardPointError("Badly formatted response.")

        if count:
            return json_body['@odata.count']
        else:
            alarm_events = []
            for x in json_body['value']:
                alarm_events.append(AlarmEvent(x))
            return alarm_events

    async def get_audit_events_count(self):
        return await self.get_audit_events(limit=None, offset=None, count=True, orderby=EventOrder.DATETIME_DESC)

    async def get_audit_events(self, limit=None, offset=None, count=False, orderby=EventOrder.DATETIME_DESC,
                         min_log_id=None):

        url = "/odata/API_AuditEventLogs"
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

        url_query_params = EventsAPI._build_url_params(self.site_uid, limit, offset, count, orderby, min_log_id)

        code, json_body = await self.gp_json_query("GET", headers=headers, url=(url + url_query_params))

        if code != 200:
            error_msg = GuardPointResponse.extract_error_msg(json_body)

            if code == 401:
                raise GuardPointUnauthorized(f"Unauthorized - ({error_msg})")
            elif code == 404:  # Not Found
                raise GuardPointError(f"Audit Events Not Found")
            else:
                raise GuardPointError(f"{error_msg}")

        if not isinstance(json_body, dict):
            raise GuardPointError("Badly formatted response.")
        if 'value' not in json_body:
            raise GuardPointError("Badly formatted response.")
        if not isinstance(json_body['value'], list):
            raise GuardPointError("Badly formatted response.")

        if count:
            return json_body['@odata.count']
        else:
            audit_events = []
            for x in json_body['value']:
                audit_events.append(AuditEvent(x))
            return audit_events



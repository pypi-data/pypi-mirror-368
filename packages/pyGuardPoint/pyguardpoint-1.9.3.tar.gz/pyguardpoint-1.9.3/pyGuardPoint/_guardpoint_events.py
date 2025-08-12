from ._odata_filter import _compose_filter
from .guardpoint_utils import GuardPointResponse
from .guardpoint_dataclasses import AlarmEvent, AccessEvent, EventOrder, AuditEvent
from .guardpoint_error import GuardPointError, GuardPointUnauthorized


class EventsAPI:
    """
    A class to interact with the events API, providing methods to retrieve access and alarm events.

    Methods
    -------
    get_access_events(limit=None, offset=None)
        Retrieves access events from the API with optional pagination.

    get_alarm_events(limit=None, offset=None)
        Retrieves alarm events from the API with optional pagination.
    """

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

    def get_access_events_count(self):
        return self.get_access_events(limit=None, offset=None, count=True, orderby=EventOrder.DATETIME_DESC)

    def get_access_events(self, limit=None, offset=None, count=False, orderby=EventOrder.DATETIME_DESC,
                          min_log_id=None):
        """
        Retrieve access event logs from the API with optional filtering, ordering, and pagination.

        :param limit: Optional; the maximum number of access events to retrieve. If not specified, all available events are retrieved.
        :type limit: int, optional
        :param offset: Optional; the number of access events to skip before starting to collect the result set.
        :type offset: int, optional
        :param count: Optional; if True, only the count of access events is returned without the actual event data.
        :type count: bool, optional
        :param orderby: Optional; the order in which to sort the access events. Defaults to descending order by date and time.
        :type orderby: EventOrder, optional
        :param min_log_id: Optional; the minimum log ID to filter access events. Only events with a log ID greater than this value are retrieved.
        :type min_log_id: int, optional
        :return: A list of AccessEvent objects representing the access events retrieved from the API.
        :rtype: list of AccessEvent
        :raises GuardPointUnauthorized: If the API request is unauthorized (HTTP status code 401).
        :raises GuardPointError: If the access events are not found (HTTP status code 404) or if there is any other error in the response.
        :raises GuardPointError: If the response body is not formatted as expected.
        """
        url = f"/odata/API_AccessEventLogs"
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

        url_query_params = EventsAPI._build_url_params(self.site_uid, limit, offset, count, orderby, min_log_id)

        code, json_body = self.gp_json_query("GET", headers=headers, url=(url + url_query_params))

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

    def get_alarm_events_count(self):
        """
        Retrieve the count of alarm events.

        This method returns the total number of alarm events by utilizing the
        `get_access_events` method with specific parameters to ensure that only
        the count is returned. The events are ordered by date and time in
        descending order.

        :return: The total count of alarm events.
        :rtype: int
        """
        return self.get_alarm_events(limit=None, offset=None, count=True, orderby=EventOrder.DATETIME_DESC)

    def get_alarm_events(self, limit=None, offset=None, count=False, orderby=EventOrder.DATETIME_DESC):
        """
        Retrieve a list of alarm events from the API with optional filtering, ordering, and pagination.

        :param limit: Optional; the maximum number of alarm events to return. If not specified, all available events are returned.
        :type limit: int, optional
        :param offset: Optional; the number of alarm events to skip before starting to collect the result set.
        :type offset: int, optional
        :param count: Optional; if True, only the count of alarm events is returned. Defaults to False.
        :type count: bool, optional
        :param orderby: Optional; the order in which to sort the alarm events. Defaults to descending order by date and time.
                        Possible values are `EventOrder.DATETIME_ASC`, `EventOrder.DATETIME_DESC`, `EventOrder.LOG_ID_ASC`,
                        and `EventOrder.LOG_ID_DESC`.
        :type orderby: EventOrder, optional
        :param min_log_id: Optional; the minimum log ID to filter the alarm events. Only events with a log ID greater than
                           this value will be returned.
        :type min_log_id: int, optional

        :raises GuardPointUnauthorized: If the API response indicates an unauthorized request (HTTP 401).
        :raises GuardPointError: If the API response indicates an error or if the response is badly formatted.

        :return: A list of `AlarmEvent` objects representing the alarm events retrieved from the API.
        :rtype: list of AlarmEvent
        """

        url = "/odata/API_AlarmEventLogs"
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

        url_query_params = EventsAPI._build_url_params(self.site_uid, limit, offset, count, orderby, None)

        code, json_body = self.gp_json_query("GET", headers=headers, url=(url + url_query_params))

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

    def get_audit_events_count(self):
        return self.get_audit_events(limit=None, offset=None, count=True, orderby=EventOrder.DATETIME_DESC)

    def get_audit_events(self, limit=None, offset=None, count=False, orderby=EventOrder.DATETIME_DESC,
                         min_log_id=None):

        url = "/odata/API_AuditEventLogs"
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

        url_query_params = EventsAPI._build_url_params(self.site_uid, limit, offset, count, orderby, min_log_id)

        code, json_body = self.gp_json_query("GET", headers=headers, url=(url + url_query_params))

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

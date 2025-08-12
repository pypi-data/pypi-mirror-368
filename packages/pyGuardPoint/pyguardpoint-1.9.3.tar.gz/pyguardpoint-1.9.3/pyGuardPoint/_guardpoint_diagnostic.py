import validators
from pyGuardPoint.guardpoint_utils import GuardPointResponse

from .guardpoint_error import GuardPointError, GuardPointUnauthorized


class DiagnosticAPI:
    """
    A class to interact with the diagnostic API for simulating access events.

    Methods
    -------
    simulate_access_event(controller_uid: str, reader_num: int, card_code: str) -> bool
        Simulates an access event for a given controller, reader, and card code.
    """
    def simulate_access_event(self, controller_uid: str, reader_num: int, card_code: str):
        """
        Simulates an access event by sending a command to the specified controller.

        This method sends a command to the controller identified by `controller_uid` to simulate an access event
        using the specified `reader_num` and `card_code`. It performs validation on the inputs and handles
        the response from the server.

        :param controller_uid: The unique identifier of the controller.
        :type controller_uid: str
        :param reader_num: The reader number (must be between 0 and 255).
        :type reader_num: int
        :param card_code: The card code (must be at least 8 characters long).
        :type card_code: str
        :raises ValueError: If `controller_uid` is not a valid UUID, `card_code` is too short, or `reader_num` is greater than 255.
        :raises GuardPointUnauthorized: If the server responds with a 401 Unauthorized status.
        :raises GuardPointError: If the server responds with an error or the response is badly formatted.
        :return: True if the access event simulation was successful, False otherwise.
        :rtype: bool
        """
        if not validators.uuid(controller_uid):
            raise ValueError(f"Malformed controller_uid: {controller_uid}")
        if len(card_code) < 8:
            raise ValueError(f"card_code too short (8 character minimum): {card_code}")
        if reader_num > 255:
            raise ValueError(f"Reader num too great (Max 255) {reader_num}")

        url = "/api/Diagnostic"
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

        controllers_uids = []
        controllers_uids.append(controller_uid)
        body = dict()
        body['controllersUIDs'] = controllers_uids
        body['command'] = "79{0:0>2X}{1:0>12s}".format(reader_num, card_code)

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

        return False

import validators
from .guardpoint_utils import GuardPointResponse
from .guardpoint_dataclasses import Controller
from .guardpoint_error import GuardPointError, GuardPointUnauthorized


class ControllersAPI:
    """
    API for interacting with controller resources.

    This class provides methods to retrieve information about controllers
    from a remote API.

    Methods
    -------
    get_controllers()
        Retrieves a list of all controllers.

    get_controller(controller_uid: str)
        Retrieves a specific controller by its unique identifier.
    """
    def get_controllers(self, ):
        """
        Retrieve a list of controllers from the GuardPoint API.

        This method sends a GET request to the GuardPoint API to fetch a list of controllers.
        It processes the response and returns a list of `Controller` objects.

        :raises GuardPointUnauthorized: If the API response status code is 401 (Unauthorized).
        :raises GuardPointError: If the API response status code is 404 (Not Found) or if the response is badly formatted.

        :return: A list of `Controller` objects.
        :rtype: list

        Example usage:

        .. code-block:: python

            controllers = guardpoint_instance.get_controllers()
            for controller in controllers:
                print(controller)

        """
        url = "/odata/API_Controllers"
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
                raise GuardPointError(f"Cardholder Not Found")
            else:
                raise GuardPointError(f"{error_msg}")

        if not isinstance(json_body, dict):
            raise GuardPointError("Badly formatted response.")
        if 'value' not in json_body:
            raise GuardPointError("Badly formatted response.")
        if not isinstance(json_body['value'], list):
            raise GuardPointError("Badly formatted response.")

        controllers = []
        for x in json_body['value']:
            controllers.append(Controller(x))
        return controllers

    def get_controller(self, controller_uid: str):
        """
        Retrieve a controller object by its unique identifier (UID).

        This method sends a GET request to the GuardPoint API to fetch details
        of a controller specified by the `controller_uid`. If the UID is not
        a valid UUID, a `ValueError` is raised. If the API response indicates
        an error or is not properly formatted, a `GuardPointError` is raised.

        :param controller_uid: The unique identifier of the controller to retrieve.
        :type controller_uid: str
        :raises ValueError: If the `controller_uid` is not a valid UUID.
        :raises GuardPointError: If the API response indicates an error or is not properly formatted.
        :return: A `Controller` object if the controller is found, otherwise `None`.
        :rtype: Controller or None
        """
        if not validators.uuid(controller_uid):
            raise ValueError(f"Malformed controller_uid: {controller_uid}")

        url = "/odata/API_Controllers"
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        }

        url_query_params = f"({controller_uid})"

        code, json_body = self.gp_json_query("GET", headers=headers, url=(url + url_query_params))

        if code != 200:
            if isinstance(json_body, dict):
                if 'error' in json_body:
                    raise GuardPointError(json_body['error'])
            else:
                raise GuardPointError(str(code))

        # Check response body is formatted as expected
        if not isinstance(json_body, dict):
            raise GuardPointError("Badly formatted response.")
        if 'value' not in json_body:
            raise GuardPointError("Badly formatted response.")
        if len(json_body) < 1:
            return None
        else:
            return Controller(json_body['value'][0])
import validators
from .guardpoint_utils import GuardPointResponse
from .guardpoint_error import GuardPointError, GuardPointUnauthorized
from .guardpoint_dataclasses import CardholderPersonalDetail


class PersonalDetailsAPI:
    """
    API class for updating personal details of a cardholder.

    Methods
    -------
    update_personal_details(cardholder_uid: str, personal_details: CardholderPersonalDetail)
        Updates the personal details of a cardholder identified by the given UID.
    """

    def update_personal_details(self, cardholder_uid: str, personal_details: CardholderPersonalDetail):
        """
        Update the personal details of a cardholder.

        This method updates the personal details of a cardholder identified by the given UID.
        It sends a PATCH request to the GuardPoint API with the updated details.

        :param cardholder_uid: The unique identifier of the cardholder.
        :type cardholder_uid: str
        :param personal_details: An instance of `CardholderPersonalDetail` containing the updated personal details.
        :type personal_details: CardholderPersonalDetail
        :raises ValueError: If the provided `cardholder_uid` is not a valid UUID.
        :raises GuardPointUnauthorized: If the request is unauthorized (HTTP 401).
        :raises GuardPointError: If the cardholder is not found (HTTP 404) or any other error occurs.
        :return: True if the update is successful.
        :rtype: bool
        """
        if not validators.uuid(cardholder_uid):
            raise ValueError(f'Malformed Cardholder UID {cardholder_uid}')

        url = "/odata/API_CardholderPersonalDetails"
        url_query_params = f"({cardholder_uid})"

        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            # 'IgnoreNonEditable': ''
        }

        ch = personal_details.dict(editable_only=True, changed_only=True)

        if len(ch) == 0:
            return True

        code, json_body = self.gp_json_query("PATCH", headers=headers, url=(url + url_query_params), json_body=ch)

        if code != 204:  # HTTP NO_CONTENT
            error_msg = GuardPointResponse.extract_error_msg(json_body)

            if code == 401:
                raise GuardPointUnauthorized(f"Unauthorized - ({error_msg})")
            elif code == 404:  # Not Found
                raise GuardPointError(f"Cardholder Not Found")
            else:
                raise GuardPointError(f"{error_msg}")

        return True
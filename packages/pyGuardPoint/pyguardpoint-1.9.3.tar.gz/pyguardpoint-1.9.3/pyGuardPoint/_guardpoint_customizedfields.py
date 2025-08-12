import validators
from .guardpoint_utils import GuardPointResponse
from .guardpoint_error import GuardPointError, GuardPointUnauthorized
from .guardpoint_dataclasses import CardholderCustomizedField


class CustomizedFieldsAPI:
    """
    API class for updating customized fields of a cardholder.

    Methods
    -------
    update_custom_fields(cardholder_uid: str, customFields: CardholderCustomizedField)
        Updates the custom fields for a specified cardholder.
    """

    def update_custom_fields(self, cardholder_uid: str, customFields: CardholderCustomizedField):
        """
        Update custom fields for a specific cardholder.

        This method updates the custom fields of a cardholder identified by the given UID.
        It sends a PATCH request to the GuardPoint API with the updated custom fields.

        :param cardholder_uid: The unique identifier of the cardholder.
        :type cardholder_uid: str
        :param customFields: An instance of `CardholderCustomizedField` containing the custom fields to be updated.
        :type customFields: CardholderCustomizedField

        :raises ValueError: If the provided `cardholder_uid` is not a valid UUID.
        :raises GuardPointUnauthorized: If the request is unauthorized (HTTP 401).
        :raises GuardPointError: If the cardholder is not found (HTTP 404) or any other error occurs.

        :return: True if the update is successful.
        :rtype: bool
        """
        if not validators.uuid(cardholder_uid):
            raise ValueError(f'Malformed Cardholder UID {cardholder_uid}')

        url = "/odata/API_CardholderCustomizedFields"
        url_query_params = f"({cardholder_uid})"

        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            # 'IgnoreNonEditable': ''
        }

        ch = customFields.dict(changed_only=True)

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

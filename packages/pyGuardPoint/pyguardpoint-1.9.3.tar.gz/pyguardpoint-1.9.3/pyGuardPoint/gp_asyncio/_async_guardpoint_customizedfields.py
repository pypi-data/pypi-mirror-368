import validators
from ..guardpoint_utils import GuardPointResponse
from ..guardpoint_error import GuardPointError, GuardPointUnauthorized
from ..guardpoint_dataclasses import CardholderCustomizedField


class CustomizedFieldsAPI:

    async def update_custom_fields(self, cardholder_uid: str, customFields: CardholderCustomizedField):
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

        code, json_body = await self.gp_json_query("PATCH", headers=headers, url=(url + url_query_params), json_body=ch)

        if code != 204:  # HTTP NO_CONTENT
            error_msg = GuardPointResponse.extract_error_msg(json_body)

            if code == 401:
                raise GuardPointUnauthorized(f"Unauthorized - ({error_msg})")
            elif code == 404:  # Not Found
                raise GuardPointError(f"Cardholder Not Found")
            else:
                raise GuardPointError(f"{error_msg}")

        return True

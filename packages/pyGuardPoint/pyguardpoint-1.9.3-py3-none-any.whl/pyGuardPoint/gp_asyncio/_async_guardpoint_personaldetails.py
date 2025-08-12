import validators
from ..guardpoint_utils import GuardPointResponse
from ..guardpoint_error import GuardPointError, GuardPointUnauthorized
from ..guardpoint_dataclasses import CardholderPersonalDetail


class PersonalDetailsAPI:

    async def update_personal_details(self, cardholder_uid: str, personal_details: CardholderPersonalDetail):
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
import validators
from .guardpoint_utils import GuardPointResponse
from ._odata_filter import _compose_filter
from .guardpoint_dataclasses import Card, Cardholder
from .guardpoint_error import GuardPointError, GuardPointUnauthorized


class CardsAPI:
    """
    A class to interact with the Cards API, providing methods to manage card entities.

    Methods
    -------
    get_cards(count=False, **card_kwargs)
        Retrieve a list of cards or the count of cards based on the provided filters.

    delete_card(card: Card)
        Delete a card identified by its UID.

    update_card(card: Card)
        Update the details of an existing card.

    new_card(card: Card)
        Create a new card.

    get_card(card_uid: str)
        Retrieve a card by its UID.

    get_cardholder_by_card_code(card_code)
        Retrieve a cardholder by the card code.
    """
    def get_cards(self, count=False, **card_kwargs):
        """
        Retrieve a list of cards or the count of cards based on the provided filters.

        This method interacts with the GuardPoint API to fetch card data. It can either return
        a list of `Card` objects that match the given criteria or the count of such cards.

        :param count: If `True`, the method returns the count of cards that match the criteria.
                      If `False`, it returns a list of `Card` objects. Default is `False`.
        :type count: bool
        :param card_kwargs: Keyword arguments corresponding to the attributes of the `Card` class
                            that will be used to filter the cards. Only exact matches are considered.
        :type card_kwargs: dict
        :return: A list of `Card` objects if `count` is `False`, or an integer count of cards if `count` is `True`.
        :rtype: list[Card] or int
        :raises GuardPointUnauthorized: If the API response indicates an unauthorized request (HTTP 401).
        :raises GuardPointError: If the API response indicates an error or is badly formatted.
        """
        match_args = dict()
        for k, v in card_kwargs.items():
            if hasattr(Card, k):
                match_args[k] = v

        url = "/odata/API_Cards"
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

        if count:
            url_query_params = "?$count=true&$top=0"
        else:
            filter_str = _compose_filter(exact_match=match_args)
            url_query_params = ("?" + filter_str)

        code, json_body = self.gp_json_query("GET", headers=headers, url=(url+url_query_params))

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

        if count:
            return json_body['@odata.count']

        cards = []
        for x in json_body['value']:
            cards.append(Card(x))
        return cards

    def delete_card(self, card: Card):
        """
        Delete a card from the system using its unique identifier (UID).

        This method sends a DELETE request to the GuardPoint API to remove a card
        identified by its UID. It validates the UID format before making the request
        and handles various HTTP response codes to provide appropriate error messages.

        :param card: The card object to be deleted.
        :type card: Card
        :raises ValueError: If the card UID is malformed.
        :raises GuardPointUnauthorized: If the request is unauthorized (HTTP 401).
        :raises GuardPointError: If the card is not found (HTTP 404) or any other error occurs.
        :return: True if the card was successfully deleted.
        :rtype: bool
        """
        if not validators.uuid(card.uid):
            raise ValueError(f'Malformed Card UID {card.uid}')

        url = "/odata/API_Cards"
        url_query_params = "(" + card.uid + ")"
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

        code, json_body = self.gp_json_query("DELETE", headers=headers, url=(url + url_query_params))

        if code != 204:  # HTTP NO_CONTENT
            error_msg = GuardPointResponse.extract_error_msg(json_body)

            if code == 401:
                raise GuardPointUnauthorized(f"Unauthorized - ({error_msg})")
            elif code == 404:  # Not Found
                raise GuardPointError(f"Card Not Found")
            else:
                raise GuardPointError(f"{error_msg}")

        return True

    def update_card(self, card: Card):
        """
        Update the details of an existing card in the system.

        This method sends a PATCH request to the API to update the card details.
        It validates the card UID before making the request and handles various
        HTTP response codes to ensure the update was successful.

        :param card: The card object containing updated details.
        :type card: Card
        :raises ValueError: If the card UID is malformed.
        :raises GuardPointUnauthorized: If the request is unauthorized (HTTP 401).
        :raises GuardPointError: If there is an error in the request or response.
        :return: True if the card was successfully updated.
        :rtype: bool
        """
        if not validators.uuid(card.uid):
            raise ValueError(f'Malformed Card UID {card.uid}')

        url = "/odata/API_Cards"
        url_query_params = f"({card.uid})"

        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            # 'IgnoreNonEditable': ''
        }

        ch = card.dict(changed_only=True)

        code, json_body = self.gp_json_query("PATCH", headers=headers, url=(url + url_query_params), json_body=ch)

        if code != 204:  # HTTP NO_CONTENT
            error_msg = GuardPointResponse.extract_error_msg(json_body)

            if code == 401:
                raise GuardPointUnauthorized(f"Unauthorized - ({error_msg})")
            else:
                raise GuardPointError(f"No body - ({code})")

        return True

    def new_card(self, card: Card):
        """
        Create a new card in the system.

        This method sends a POST request to the API to create a new card with the provided details.
        If the card is successfully created, it returns a `Card` object representing the newly created card.
        If the creation fails, it raises a `GuardPointError` with an appropriate error message.

        :param card: The `Card` object containing the details of the card to be created.
        :type card: Card
        :raises GuardPointError: If the card creation fails, an error is raised with the relevant error message.
        :return: A `Card` object representing the newly created card.
        :rtype: Card
        """
        url = "/odata/API_Cards"
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        }
        body = card.dict(editable_only=True)

        code, json_body = self.gp_json_query("POST", headers=headers, url=url, json_body=body)

        if code == 201:  # HTTP CREATED
            return Card(json_body)
        else:
            if "errorMessages" in json_body:
                raise GuardPointError(json_body["errorMessages"][0]["other"])
            elif "message" in json_body:
                raise GuardPointError(json_body['message'])
            else:
                raise GuardPointError(str(code))

    def get_card(self, card_uid: str):
        """
        Retrieve a card's details from the GuardPoint system using its unique identifier.

        This method sends a GET request to the GuardPoint API to fetch the details of a card
        identified by the provided `card_uid`. If the request is successful and the response
        is properly formatted, it returns a `Card` object containing the card's details.
        Otherwise, it raises a `GuardPointError`.

        :param card_uid: The unique identifier of the card to be retrieved.
        :type card_uid: str
        :raises GuardPointError: If the request fails or the response is improperly formatted.
        :return: A `Card` object containing the details of the requested card.
        :rtype: Card
        """
        url = "/odata/API_Cards"
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        }

        url_query_params = f"({card_uid})"

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

        return Card(json_body['value'])

    def get_cardholder_by_card_code(self, card_code):
        """
        Retrieve the cardholder information associated with a specific card code.

        This method queries the GuardPoint API to fetch details of the cardholder
        whose card has the specified card code and is marked as 'Used'. The response
        includes expanded details about the cardholder, such as security group,
        cardholder type, personal details, customized fields, and inside area.

        :param card_code: The code of the card to search for.
        :type card_code: str
        :return: The cardholder associated with the given card code.
        :rtype: Cardholder
        :raises GuardPointError: If the API response is malformed or if no cardholder is found.
        """
        url = "/odata/API_Cards"
        filter_str = f"?$filter=cardcode%20eq%20'{card_code}'%20and%20status%20eq%20'Used'%20&"
        url_query_params = f"{filter_str}" \
                           f"$expand=cardholder(" \
                           "$expand=securityGroup($select=name)," \
                           "cardholderType($select=typeName)," \
                           "cards," \
                           "cardholderPersonalDetail," \
                           "cardholderCustomizedField," \
                           "securityGroup," \
                           "insideArea)" \

        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        }

        code, json_body = self.gp_json_query("GET", headers=headers, url=(url + url_query_params))

        if code != 200:
            if isinstance(json_body, dict):
                if 'error' in json_body:
                    raise GuardPointError(json_body['error'])

        if not isinstance(json_body, dict):
            raise GuardPointError("Badly formatted response.")
        if 'value' not in json_body:
            raise GuardPointError("Badly formatted response.")
        if not isinstance(json_body['value'], list):
            raise GuardPointError("Badly formatted response.")

        card_holders = []
        for x in json_body['value']:
            if 'cardholder' in x:
                card_holders.append(Cardholder(x['cardholder']))

        if len(card_holders) > 0:
            return card_holders[0]
        else:
            raise GuardPointError("No Cardholder Found")

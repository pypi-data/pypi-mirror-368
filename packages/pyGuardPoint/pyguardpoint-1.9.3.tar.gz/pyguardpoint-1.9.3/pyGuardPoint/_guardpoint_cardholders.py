import logging
from datetime import datetime

import validators
from ._odata_filter import _compose_filter, _compose_select, _compose_expand
from ._str_match_algo import fuzzy_match
from .guardpoint_dataclasses import Cardholder, SortAlgorithm, Area, CardholderOrderBy
from .guardpoint_error import GuardPointError, GuardPointUnauthorized
from .guardpoint_utils import GuardPointResponse

log = logging.getLogger(__name__)


class CardholdersAPI:
    """
    A class to interact with the Cardholders API, providing methods to manage cardholders, including creating, updating, deleting, and retrieving cardholder information.

    Methods
    -------
    delete_card_holder(cardholder: Cardholder)
        Deletes a cardholder from the system.

    update_card_holder_area(cardholder_uid: str, area: Area)
        Updates the area associated with a cardholder.

    update_card_holder(cardholder: Cardholder)
        Updates the details of a cardholder.

    new_card_holder(cardholder: Cardholder, changed_only=False)
        Creates a new cardholder in the system.

    get_card_holder(uid: str = None, card_code: str = None)
        Retrieves a cardholder by UID or card code.

    get_card_holder_photo(uid)
        Retrieves the photo of a cardholder by UID.

    get_card_holders(offset: int = 0, limit: int = 10, search_terms: str = None, areas: list = None, filter_expired: bool = False, cardholder_type_name: str = None, sort_algorithm: SortAlgorithm = SortAlgorithm.SERVER_DEFAULT, threshold: int = 75, count: bool = False, earliest_last_pass: datetime = None, select_ignore_list: list = None, select_include_list: list = None, **cardholder_kwargs)
        Retrieves a list of cardholders based on various filters and search criteria.
    """

    def delete_card_holder(self, cardholder: Cardholder):
        """
        Delete a cardholder from the system.

        This method deletes a cardholder identified by their UID from the system.
        It performs a validation check on the UID to ensure it is a valid UUID.
        If the UID is malformed, a `ValueError` is raised. The method then sends
        a DELETE request to the API endpoint to remove the cardholder.

        :param cardholder: The cardholder object to be deleted.
        :type cardholder: Cardholder

        :raises ValueError: If the cardholder UID is malformed.
        :raises GuardPointUnauthorized: If the request is unauthorized (HTTP 401).
        :raises GuardPointError: If the cardholder is not found (HTTP 404) or
                                 if another error occurs.

        :return: True if the cardholder was successfully deleted.
        :rtype: bool
        """
        if not validators.uuid(cardholder.uid):
            raise ValueError(f'Malformed Cardholder UID {cardholder.uid}')

        url = self.baseurl + "/odata/API_Cardholders"
        url_query_params = "(" + cardholder.uid + ")"

        code, json_body = self.gp_json_query("DELETE", url=(url + url_query_params))
        # Check response body is formatted correctly
        if json_body:
            GuardPointResponse.check_odata_body_structure(json_body)

        if code != 204:  # HTTP NO_CONTENT
            error_msg = GuardPointResponse.extract_error_msg(json_body)

            if code == 401:
                raise GuardPointUnauthorized(f"Unauthorized - ({error_msg})")
            elif code == 404:  # Not Found
                raise GuardPointError(f"Cardholder Not Found")
            else:
                raise GuardPointError(f"{error_msg}")

        return True

    def update_card_holder_area(self, cardholder_uid: str, area: Area):
        """
        Update the area associated with a cardholder.

        This method updates the area (location) information for a given cardholder by their unique identifier (UID).
        It validates the provided UIDs for both the cardholder and the area before performing the update.

        :param cardholder_uid: The unique identifier of the cardholder.
        :type cardholder_uid: str
        :param area: The area object containing the new area UID.
        :type area: Area
        :raises ValueError: If the cardholder UID or area UID is malformed (not a valid UUID).
        :return: The result of the cardholder update operation.
        :rtype: Any
        """
        if not validators.uuid(cardholder_uid):
            raise ValueError(f'Malformed Cardholder UID {cardholder_uid}')

        if not validators.uuid(area.uid):
            raise ValueError(f'Malformed Area UID {area.uid}')

        cardholder = Cardholder()
        cardholder.uid = cardholder_uid
        cardholder.insideAreaUID = area.uid

        return self.update_card_holder(cardholder)

    def update_card_holder(self, cardholder: Cardholder, enroll_face_from_photo=False):
        """
        Update the details of a cardholder in the system.

        This method updates various attributes of a cardholder, including custom fields, personal details, and associated cards.
        It performs validation on the cardholder's UID and the UIDs of associated cards. If any attributes have changed, it sends
        a PATCH request to update the cardholder's information in the system.

        :param cardholder: The cardholder object containing updated information.
        :type cardholder: Cardholder
        :param enroll_face_from_photo: Flag indicating whether to enroll the cardholder's face from a photo, defaults to False.
        :type enroll_face_from_photo: bool, optional
        :raises ValueError: If the cardholder UID is malformed.
        :raises GuardPointUnauthorized: If the request is unauthorized.
        :raises GuardPointError: If the cardholder is not found or another error occurs.
        :return: True if the update is successful, otherwise raises an exception.
        :rtype: bool
        """

        if not validators.uuid(cardholder.uid):
            raise ValueError(f'Malformed Cardholder UID {cardholder.uid}')

        if cardholder.cardholderCustomizedField:
            if len(cardholder.cardholderCustomizedField.changed_attributes) > 0:
                self.update_custom_fields(cardholder.uid, cardholder.cardholderCustomizedField)

        if cardholder.cardholderPersonalDetail:
            if len(cardholder.cardholderPersonalDetail.changed_attributes) > 0:
                self.update_personal_details(cardholder.uid, cardholder.cardholderPersonalDetail)

        if cardholder.cards:
            if isinstance(cardholder.cards, list):
                for card in cardholder.cards:
                    if len(card.changed_attributes) > 0:
                        if validators.uuid(card.uid):
                            self.update_card(card)
                        else:
                            card.cardholderUID = cardholder.uid
                            self.new_card(card)

        ch = cardholder.dict(editable_only=True, changed_only=True)

        if len(ch) < 1:  # Nothing to update
            return True

        url = "/odata/API_Cardholders"
        url_query_params = f"({cardholder.uid})"

        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            # 'IgnoreNonEditable': ''
        }

        if enroll_face_from_photo:
            headers['EnrollFaceFromPhoto'] = ""

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

    def new_card_holder(self, cardholder: Cardholder, changed_only=False, enroll_face_from_photo=False):
        """
        Create a new cardholder in the system.

        This method sends a POST request to the GuardPoint API to create a new cardholder.
        Depending on the `changed_only` flag, it can either send only the changed fields or
        all editable and non-empty fields of the cardholder.

        :param cardholder: The cardholder object to be created.
        :type cardholder: Cardholder
        :param changed_only: If True, only the changed fields of the cardholder will be sent.
                             Otherwise, all editable and non-empty fields will be sent.
        :type changed_only: bool, optional
        :param enroll_face_from_photo: If True, enroll the cardholder's face from a photo.
        :type enroll_face_from_photo: bool, optional

        :return: The newly created cardholder object.
        :rtype: Cardholder

        :raises GuardPointError: If there is an error in the request or response.
        :raises GuardPointUnauthorized: If the request is unauthorized.
        """
        url = "/odata/API_Cardholders"

        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'IgnoreNonEditable': ''
        }

        if enroll_face_from_photo:
            headers['EnrollFaceFromPhoto'] = ""

        if changed_only:
            ch = cardholder.dict(editable_only=True, changed_only=True, non_empty_only=True)
        else:
            ch = cardholder.dict(editable_only=True, non_empty_only=True)

        # Override Site UID
        if self.site_uid is not None:
            ch['ownerSiteUID'] = self.site_uid

        code, json_body = self.gp_json_query("POST", headers=headers, url=url, json_body=ch)

        # Check response body is formatted correctly
        if json_body:
            GuardPointResponse.check_odata_body_structure(json_body)

        if code == 201:  # HTTP CREATED
            new_cardholder = Cardholder(json_body)
            if cardholder.cardholderPersonalDetail:
                self.update_personal_details(cardholder_uid=new_cardholder.uid,
                                             personal_details=cardholder.cardholderPersonalDetail)
            if cardholder.cardholderCustomizedField:
                self.update_custom_fields(cardholder_uid=new_cardholder.uid,
                                          customFields=cardholder.cardholderCustomizedField)
            if cardholder.cards:
                if isinstance(cardholder.cards, list):
                    for card in cardholder.cards:
                        if validators.uuid(card.uid):
                            self.update_card(card)
                        else:
                            card.cardholderUID = new_cardholder.uid
                            self.new_card(card)

            return self._get_card_holder(new_cardholder.uid)

        elif code == 422:  # unprocessable Entity
            if "errorMessages" in json_body:
                raise GuardPointError(
                    f'{json_body["errorMessages"][0]["message"]}-{json_body["errorMessages"][0]["other"]}')
        else:
            error_msg = GuardPointResponse.extract_error_msg(json_body)

            if code == 401:
                raise GuardPointUnauthorized(f"Unauthorized - ({error_msg})")
            elif code == 404:  # Not Found
                raise GuardPointError(f"Cardholder Not Found")
            else:
                raise GuardPointError(f"{error_msg}")

    def get_card_holder(self,
                        uid: str = None,
                        card_code: str = None):
        """
        Retrieve cardholder information based on either a unique identifier (UID) or a card code.

        This method allows you to fetch cardholder details by providing either a `uid` or a `card_code`.
        If a `card_code` is provided, it will use the `get_cardholder_by_card_code` method to retrieve
        the information. Otherwise, it will use the `_get_card_holder` method with the provided `uid`.

        :param uid: The unique identifier of the cardholder. Default is None.
        :type uid: str, optional
        :param card_code: The card code associated with the cardholder. Default is None.
        :type card_code: str, optional
        :return: Instance of Cardholder.
        :rtype: Cardholder
        :raises ValueError: If neither `uid` nor `card_code` is provided.
        """
        if card_code:
            # Part of the Cards_API
            return self.get_cardholder_by_card_code(card_code)
        else:
            return self._get_card_holder(uid)

    def get_card_holder_photo(self, uid):
        """
        Retrieve the photo of a cardholder given their unique identifier (UID).

        This method sends a GET request to the GuardPoint API to fetch the photo of a cardholder.
        The UID must be a valid UUID. If the UID is malformed, a ValueError is raised. If the
        request is unauthorized, a GuardPointUnauthorized exception is raised. If the cardholder
        photo is not found, a GuardPointError is raised.

        :param uid: The unique identifier of the cardholder.
        :type uid: str
        :raises ValueError: If the UID is not a valid UUID.
        :raises GuardPointUnauthorized: If the request is unauthorized.
        :raises GuardPointError: If the cardholder photo is not found or another error occurs.
        :return: The photo of the cardholder.
        :rtype: str
        """
        if not validators.uuid(uid):
            raise ValueError(f'Malformed UID {uid}')

        url = "/odata/API_Cardholders"
        url_query_params = "(" + uid + ")?$select=photo"

        code, json_body = self.gp_json_query("GET", url=(url + url_query_params))

        if code != 200:
            error_msg = GuardPointResponse.extract_error_msg(json_body)

            if code == 401:
                raise GuardPointUnauthorized(f"Unauthorized - ({error_msg})")
            elif code == 404:  # Not Found
                raise GuardPointError(f"Cardholder Photo Not Found")
            else:
                raise GuardPointError(f"{error_msg}")

        return json_body['value'][0]['photo']

    def _get_card_holder(self, uid):
        if not validators.uuid(uid):
            raise ValueError(f'Malformed UID {uid}')

        url = "/odata/API_Cardholders"
        url_query_params = "(" + uid + ")?" \
                                       "$expand=" \
                                       "cardholderType," \
                                       "cards," \
                                       "cardholderCustomizedField," \
                                       "cardholderPersonalDetail," \
                                       "securityGroup," \
                                       "insideArea"

        if self.site_uid is not None:
            match_args = {'ownerSiteUID': self.site_uid}
            filter_str = _compose_filter(exact_match=match_args)
            url_query_params += ("&" + filter_str)

        code, json_body = self.gp_json_query("GET", url=(url + url_query_params))

        if code == 404:  # Not Found
            return None

        if code != 200:
            error_msg = GuardPointResponse.extract_error_msg(json_body)

            if code == 401:
                raise GuardPointUnauthorized(f"Unauthorized - ({error_msg})")
            elif code == 404:  # Not Found
                raise GuardPointError(f"Cardholder Not Found")
            else:
                raise GuardPointError(f"{error_msg}")

        if len(json_body['value']) > 0:
            return Cardholder(json_body['value'][0])
        else:
            return None

    def get_card_holders(self, offset: int = 0, limit: int = 10, search_terms: str = None, areas: list = None,
                         filter_expired: bool = False, cardholder_type_name: str = None,
                         sort_algorithm: SortAlgorithm = SortAlgorithm.SERVER_DEFAULT, threshold: int = 75,
                         count: bool = False, earliest_last_pass: datetime = None,
                         select_ignore_list: list = None, select_include_list: list = None,
                         cardholder_orderby: CardholderOrderBy = CardholderOrderBy.fromDateValid_DESC,
                         **cardholder_kwargs):
        """
        Retrieve a list of cardholders from the system with various filtering and sorting options.

        :param offset: The starting point within the collection of cardholders. Default is 0.
        :type offset: int
        :param limit: The maximum number of cardholders to return. Default is 10.
        :type limit: int
        :param search_terms: Search terms to filter cardholders by name or other attributes. Default is None.
        :type search_terms: str, optional
        :param areas: List of areas to filter cardholders by. Default is None.
        :type areas: list, optional
        :param filter_expired: Whether to filter out expired cardholders. Default is False.
        :type filter_expired: bool
        :param cardholder_type_name: Filter cardholders by type name. Default is None.
        :type cardholder_type_name: str, optional
        :param sort_algorithm: Algorithm to sort the cardholders. Default is SortAlgorithm.SERVER_DEFAULT.
        :type sort_algorithm: SortAlgorithm
        :param threshold: Threshold for fuzzy matching. Default is 75.
        :type threshold: int
        :param count: Whether to return the count of cardholders instead of the list. Default is False.
        :type count: bool
        :param earliest_last_pass: Filter cardholders by the earliest last pass date. Default is None.
        :type earliest_last_pass: datetime, optional
        :param select_ignore_list: List of fields to ignore in the select query. Default is None.
        :type select_ignore_list: list, optional
        :param select_include_list: List of fields to include in the select query. Default is None.
        :type select_include_list: list, optional
        :param cardholder_kwargs: Additional keyword arguments for exact match filtering.
        :type cardholder_kwargs: dict

        :return: A list of cardholders or the count of cardholders based on the `count` parameter.
        :rtype: list[Cardholder] or int

        :raises GuardPointUnauthorized: If the request is unauthorized.
        :raises GuardPointError: If there is an error in retrieving cardholders or if cardholders are not found.
        """
        if limit <= 0:
            return []
        if limit > 50:
            i_offset = offset
            offset = 0
            batch_limit = 50
            card_holders = []
            while len(card_holders) == offset:
                if offset + batch_limit > limit:
                    batch_limit = limit - offset
                if batch_limit > 0:
                    card_holders.extend(
                        self._get_card_holders(offset=offset+i_offset, limit=batch_limit, search_terms=search_terms,
                                               areas=areas,
                                               filter_expired=filter_expired,
                                               cardholder_type_name=cardholder_type_name,
                                               sort_algorithm=sort_algorithm, threshold=threshold,
                                               count=count, earliest_last_pass=earliest_last_pass,
                                               select_ignore_list=select_ignore_list,
                                               select_include_list=select_include_list,
                                               cardholder_orderby=cardholder_orderby,
                                               **cardholder_kwargs))
                if (offset + batch_limit) >= limit:
                    break
                elif len(card_holders) > offset:
                    offset = len(card_holders)
                else:
                    break

            return card_holders
        else:
            return self._get_card_holders(offset=offset, limit=limit, search_terms=search_terms,
                                          areas=areas,
                                          filter_expired=filter_expired,
                                          cardholder_type_name=cardholder_type_name,
                                          sort_algorithm=sort_algorithm, threshold=threshold,
                                          count=count, earliest_last_pass=earliest_last_pass,
                                          select_ignore_list=select_ignore_list,
                                          select_include_list=select_include_list,
                                          cardholder_orderby=cardholder_orderby,
                                          **cardholder_kwargs)

    def _get_card_holders(self, offset: int = 0, limit: int = 10, search_terms: str = None, areas: list = None,
                          filter_expired: bool = False, cardholder_type_name: str = None,
                          sort_algorithm: SortAlgorithm = SortAlgorithm.SERVER_DEFAULT, threshold: int = 75,
                          count: bool = False, earliest_last_pass: datetime = None,
                          select_ignore_list: list = None, select_include_list: list = None,
                          cardholder_orderby: CardholderOrderBy = CardholderOrderBy.fromDateValid_DESC,
                          **cardholder_kwargs):
        if offset is None:
            offset = 0

        # Filter arguments which have to exact match
        match_args = dict()
        for k, v in cardholder_kwargs.items():
            if hasattr(Cardholder, k):
                match_args[k] = v

        # Force site_uid filter if present
        if self.site_uid is not None:
            if 'ownerSiteUID' in match_args:
                log.info(f"ownerSiteUID overridden")
                match_args['ownerSiteUID'] = self.site_uid

        url = "/odata/API_Cardholders"

        filter_str = _compose_filter(search_words=search_terms,
                                     areas=areas,
                                     filter_expired=filter_expired,
                                     cardholder_type_name=cardholder_type_name,
                                     earliest_last_pass=earliest_last_pass,
                                     exact_match=match_args)

        select_str = _compose_select(select_ignore_list, select_include_list)

        expand_str = _compose_expand(select_ignore_list, select_include_list)

        url_query_params = ("?" + select_str + expand_str + filter_str)

        if count:
            url_query_params += "$count=true&$top=0"
        else:
            if cardholder_orderby == CardholderOrderBy.lastPassDate_DESC:
                url_query_params += "$orderby=lastPassDate%20desc&"
            else:
                url_query_params += "$orderby=fromDateValid%20desc&"

            url_query_params += "$top=" + str(limit) + "&$skip=" + str(offset)

        code, json_body = self.gp_json_query("GET", url=(url + url_query_params))
        # Check response body is formatted correctly
        # if json_body:
        #    GuardPointResponse.check_odata_body_structure(json_body)

        if code != 200:
            error_msg = GuardPointResponse.extract_error_msg(json_body)

            if code == 401:
                raise GuardPointUnauthorized(f"Unauthorized - ({error_msg})")
            elif code == 404:  # Not Found
                raise GuardPointError(f"Cardholders Not Found")
            else:
                raise GuardPointError(f"{error_msg}")

        if count:
            return json_body['@odata.count']

        cardholders: list = []
        for x in json_body['value']:
            cardholders.append(Cardholder(x))

        if sort_algorithm == SortAlgorithm.FUZZY_MATCH:
            cardholders = fuzzy_match(search_words=search_terms, cardholders=cardholders, threshold=threshold)

        return cardholders

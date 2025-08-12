import logging
from datetime import datetime
import validators
from .._odata_filter import _compose_filter, _compose_select, _compose_expand
from .._str_match_algo import fuzzy_match
from ..guardpoint_dataclasses import Cardholder, SortAlgorithm, Area, CardholderOrderBy
from ..guardpoint_error import GuardPointError, GuardPointUnauthorized
from ..guardpoint_utils import GuardPointResponse

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

    async def delete_card_holder(self, cardholder: Cardholder):
        if not validators.uuid(cardholder.uid):
            raise ValueError(f'Malformed Cardholder UID {cardholder.uid}')

        url = "/odata/API_Cardholders"
        url_query_params = "(" + cardholder.uid + ")"

        code, json_body = await self.gp_json_query("DELETE", url=(url + url_query_params))
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

    async def update_card_holder_area(self, cardholder_uid: str, area: Area):
        if not validators.uuid(cardholder_uid):
            raise ValueError(f'Malformed Cardholder UID {cardholder_uid}')

        if not validators.uuid(area.uid):
            raise ValueError(f'Malformed Area UID {area.uid}')

        cardholder = Cardholder()
        cardholder.uid = cardholder_uid
        cardholder.insideAreaUID = area.uid

        return await self.update_card_holder(cardholder)

    async def update_card_holder(self, cardholder: Cardholder, enroll_face_from_photo=False):
        if not validators.uuid(cardholder.uid):
            raise ValueError(f'Malformed Cardholder UID {cardholder.uid}')

        if cardholder.cardholderCustomizedField:
            if len(cardholder.cardholderCustomizedField.changed_attributes) > 0:
                await self.update_custom_fields(cardholder.uid, cardholder.cardholderCustomizedField)

        if cardholder.cardholderPersonalDetail:
            if len(cardholder.cardholderPersonalDetail.changed_attributes) > 0:
                await self.update_personal_details(cardholder.uid, cardholder.cardholderPersonalDetail)

        if cardholder.cards:
            if isinstance(cardholder.cards, list):
                for card in cardholder.cards:
                    if len(card.changed_attributes) > 0:
                        if validators.uuid(card.uid):
                            await self.update_card(card)
                        else:
                            card.cardholderUID = cardholder.uid
                            await self.new_card(card)

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

    async def new_card_holder(self, cardholder: Cardholder, changed_only=False, enroll_face_from_photo=False):

        # url = "/odata/API_Cardholders/CreateFullCardholder"
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

        code, json_body = await self.gp_json_query("POST", headers=headers, url=url, json_body=ch)

        # Check response body is formatted correctly
        if json_body:
            GuardPointResponse.check_odata_body_structure(json_body)

        if code == 201:  # HTTP CREATED
            new_cardholder = Cardholder(json_body)
            if cardholder.cardholderPersonalDetail:
                await self.update_personal_details(cardholder_uid=new_cardholder.uid,
                                                   personal_details=cardholder.cardholderPersonalDetail)
            if cardholder.cardholderCustomizedField:
                await self.update_custom_fields(cardholder_uid=new_cardholder.uid,
                                                customFields=cardholder.cardholderCustomizedField)
            if cardholder.cards:
                if isinstance(cardholder.cards, list):
                    for card in cardholder.cards:
                        if validators.uuid(card.uid):
                            await self.update_card(card)
                        else:
                            card.cardholderUID = new_cardholder.uid
                            await self.new_card(card)

            return await self._get_card_holder(new_cardholder.uid)

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

    async def get_card_holder(self,
                              uid: str = None,
                              card_code: str = None):
        if card_code:
            # Part of the Cards_API
            return await self.get_cardholder_by_card_code(card_code)
        else:
            return await self._get_card_holder(uid)

    async def get_card_holder_photo(self, uid):
        if not validators.uuid(uid):
            raise ValueError(f'Malformed UID {uid}')

        url = "/odata/API_Cardholders"
        url_query_params = "(" + uid + ")?$select=photo"

        code, json_body = await self.gp_json_query("GET", url=(url + url_query_params))
        # Check response body is formatted correctly
        # if json_body:
        #    GuardPointResponse.check_odata_body_structure(json_body)

        if code != 200:
            error_msg = GuardPointResponse.extract_error_msg(json_body)

            if code == 401:
                raise GuardPointUnauthorized(f"Unauthorized - ({error_msg})")
            elif code == 404:  # Not Found
                raise GuardPointError(f"Cardholder Photo Not Found")
            else:
                raise GuardPointError(f"{error_msg}")

        return json_body['value'][0]['photo']

    async def _get_card_holder(self, uid):
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

        code, json_body = await self.gp_json_query("GET", url=(url + url_query_params))

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

    async def get_card_holders(self, offset: int = 0, limit: int = 10, search_terms: str = None, areas: list = None,
                               filter_expired: bool = False, cardholder_type_name: str = None,
                               sort_algorithm: SortAlgorithm = SortAlgorithm.SERVER_DEFAULT, threshold: int = 75,
                               count: bool = False, earliest_last_pass: datetime = None,
                               select_ignore_list: list = None, select_include_list: list = None,
                               cardholder_orderby: CardholderOrderBy = CardholderOrderBy.fromDateValid_DESC,
                               **cardholder_kwargs):
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
                    card_holders.extend(await self._get_card_holders(offset=offset+i_offset, limit=batch_limit,
                                                                     search_terms=search_terms,
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
            return await self._get_card_holders(offset=offset, limit=limit, search_terms=search_terms,
                                                areas=areas,
                                                filter_expired=filter_expired,
                                                cardholder_type_name=cardholder_type_name,
                                                sort_algorithm=sort_algorithm, threshold=threshold,
                                                count=count, earliest_last_pass=earliest_last_pass,
                                                select_ignore_list=select_ignore_list,
                                                select_include_list=select_include_list,
                                                cardholder_orderby=cardholder_orderby,
                                                **cardholder_kwargs)

    async def _get_card_holders(self, offset: int = 0, limit: int = 10, search_terms: str = None, areas: list = None,
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

        code, json_body = await self.gp_json_query("GET", url=(url + url_query_params))
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

        cardholders = []
        for x in json_body['value']:
            cardholders.append(Cardholder(x))

        if sort_algorithm == SortAlgorithm.FUZZY_MATCH:
            cardholders = fuzzy_match(search_words=search_terms, cardholders=cardholders, threshold=threshold)

        return cardholders

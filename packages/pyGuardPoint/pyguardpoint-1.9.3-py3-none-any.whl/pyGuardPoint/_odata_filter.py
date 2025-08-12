from datetime import datetime

import validators

from .guardpoint_dataclasses import Area, Cardholder, CardholderPersonalDetail
from urllib.parse import quote


def _compose_expand(ignore_list, include_list):
    expand_attribs = ['cardholderType', 'cards', 'cardholderPersonalDetail', 'cardholderCustomizedField', 'insideArea',
                      'securityGroup']
    expand_str = ""
    if not ignore_list and not include_list:
        expand_str += "$expand="
        expand_str += f"{','.join(expand_attribs)}"
        expand_str += "&"
        return expand_str

    expand_list = []
    if include_list:
        for e in expand_attribs:
            if e in include_list:
                if ignore_list:
                    if e not in ignore_list:
                        expand_list.append(e)
                else:
                    expand_list.append(e)
    else:
        if ignore_list:
            for e in expand_attribs:
                if e not in ignore_list:
                    expand_list.append(e)

    expand_str = ""
    if len(expand_list) > 0:
        expand_str += "$expand="
        expand_str += f"{','.join(expand_list)}"
        expand_str += "&"

    return expand_str


def _compose_select(ignore_list, include_list):
    if not ignore_list and not include_list:
        return "$select=*&"

    ch = Cardholder()
    ch_dict = ch.dict()
    select_properties = []
    if include_list:
        for k in ch_dict:
            if k in include_list:
                if ignore_list:
                    if k not in ignore_list:
                        select_properties.append(k)
                else:
                    select_properties.append(k)
    else:
        if ignore_list:
            for k in ch_dict:
                if k not in ignore_list:
                    select_properties.append(k)

    select_str = ""
    if len(select_properties) > 0:
        select_str += "$select="
        select_str += f"{','.join(select_properties)}"
        select_str += "&"
    else:
        select_str = "$select=*&"

    return select_str


def _compose_filter(search_words=None,
                    areas=None,
                    cardholder_type_name=None,
                    filter_expired=False,
                    earliest_last_pass=None,
                    exact_match=None,
                    greater_than=None):
    filter_phrases = []

    if greater_than:
        if isinstance(greater_than, dict):
            for k, v in greater_than.items():
                if isinstance(v, int):
                    filter_phrases.append(f"({k}%20gt%20{v})")

    if exact_match:
        if isinstance(exact_match, dict):
            for k, v in exact_match.items():
                if isinstance(v, str):
                    v = v.replace("'", "''")
                    if validators.uuid(v):
                        filter_phrases.append(f"({k}%20eq%20{quote(v)})")
                    else:
                        filter_phrases.append(f"({k}%20eq%20'{quote(v)}')")
                if isinstance(v, (bool, int)):
                    filter_phrases.append(f"({k}%20eq%20{quote(v)})")
                if k == "cardholderPersonalDetail" and v.__class__.__name__ == "CardholderPersonalDetail":
                    details = v.dict(changed_only=True)
                    for dk, dv in details.items():
                        if isinstance(dv, str):
                            dv = dv.replace("'", "''")
                        filter_phrases.append(f"(CardholderPersonalDetail/{dk}%20eq%20'{quote(dv)}')")
                if k == "cardholderCustomizedField" and v.__class__.__name__ == "CardholderCustomizedField":
                    details = v.dict(changed_only=True)
                    for dk, dv in details.items():
                        if isinstance(dv, type(None)):
                            filter_phrases.append(f"(CardholderCustomizedField/{dk}%20eq%20{quote('null')})")
                        elif isinstance(dv, (bool, int)):
                            filter_phrases.append(f"(CardholderCustomizedField/{dk}%20eq%20{str(dv).lower()})")
                        elif isinstance(dv, str):
                            dv = dv.replace("'", "''")
                            filter_phrases.append(f"(CardholderCustomizedField/{dk}%20eq%20'{quote(dv)}')")
                        else:
                            filter_phrases.append(f"(CardholderCustomizedField/{dk}%20eq%20'{quote(dv)}')")

    if earliest_last_pass:
        if isinstance(earliest_last_pass, datetime):
            last_pass_date = earliest_last_pass.strftime('%Y-%m-%dT%H:%M:%SZ')
            filter_phrases.append(f'(lastPassDate%20ge%20{last_pass_date}%20or%20lastPassDate%20eq%20null)')

    # Filter out expired cardholders
    if filter_expired:
        # end_of_day = datetime.utcnow().strftime('%Y-%m-%dT23:59:59Z')
        start_of_day = datetime.utcnow().strftime('%Y-%m-%dT00:00:00Z')
        filter_phrases.append(f'(toDateValid%20ge%20{start_of_day})')

    # Filter by Cardholder Type Name
    if cardholder_type_name:
        filter_phrases.append(f"(cardholderType/typeName%20eq%20'{cardholder_type_name}')")

    # Filter by Areas
    if areas:
        if isinstance(areas, Area):
            filter_phrases.append(f"(insideAreaUID%20eq%20{areas.uid})")
        if isinstance(areas, list):
            if len(areas) > 0:
                area_phrases = []
                for area in areas:
                    if isinstance(area, Area):
                        area_phrases.append(f"(insideAreaUID%20eq%20{area.uid})")
                filter_phrases.append(f"({'%20or%20'.join(area_phrases)})")

    # Search filter
    if search_words:
        if isinstance(search_words, str):
            # Split 'search_words' by spaces, remove empty elements, ignore > 5 elements
            words = list(filter(None, search_words.split(" ")))[:5]
            fields = ["firstName", "lastName", "CardholderPersonalDetail/company", "CardholderPersonalDetail/email"]
            search_phrases = []
            for f in fields:
                for v in words:
                    if "'" in v:
                        v = v.replace("'", "''")
                    search_phrases.append(f"contains({f},'{v}')")
            filter_phrases.append(f"({'%20or%20'.join(search_phrases)})")

    # compose filter string
    filter_str = ""
    if len(filter_phrases) > 0:
        filter_str += "$filter="
        filter_str += f"({'%20and%20'.join(filter_phrases)})"
        filter_str += "&"

    return filter_str


if __name__ == "__main__":
    area_list = []
    area_list.append(Area({'uid': '00000000-0000-0000-0000-100000000001', 'area': "Offsite"}))
    print(_compose_filter(search_words="John Owen",
                          areas=area_list,
                          cardholder_type_name="Visitor", filter_expired=True))

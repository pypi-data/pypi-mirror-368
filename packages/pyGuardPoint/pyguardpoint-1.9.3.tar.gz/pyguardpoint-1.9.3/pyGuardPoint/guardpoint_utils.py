import binascii
import time
import base64
from urllib.parse import urlparse
from .guardpoint_error import GuardPointError


def url_parser(url):
    parts = urlparse(url)
    directories = parts.path.strip('/').split('/')
    queries = parts.query.strip('&').split('&')
    host = parts.netloc.strip(':').split(':')[0]

    elements = {
        'scheme': parts.scheme,
        'host': host,
        'path': parts.path,
        'params': parts.params,
        'query': parts.query,
        'port': parts.port,
        'fragment': parts.fragment,
        'directories': directories,
        'queries': queries,
    }

    return elements


class ConvertBase64:

    @staticmethod
    def encode(text: str):
        return base64.b64encode(text.encode('ascii')).decode('ascii')

    @staticmethod
    def decode(text: str):
        try:
            return base64.b64decode(text.encode('ascii')).decode('ascii')
        except binascii.Error:
            return base64.b64decode(text.encode('ascii') + b"==").decode('ascii')


class GuardPointResponse:
    @staticmethod
    def extract_error_msg(response_body):
        error_msg = ""
        if isinstance(response_body, dict):
            if "errorMessages" in response_body:
                if isinstance(response_body["errorMessages"], list):
                    if 'message' in response_body["errorMessages"][0] and 'other' in response_body["errorMessages"][0]:
                        error_msg = f'{response_body["errorMessages"][0]["message"]}-{response_body["errorMessages"][0]["other"]}'
            if 'message' in response_body:
                error_msg = response_body['message']
            if 'error' in response_body:
                error_msg = response_body['error']
            if 'errors' in response_body:
                if isinstance(response_body['errors'], dict):
                    for key in response_body['errors']:
                        if isinstance(response_body['errors'][key], list):
                            error_msg = error_msg + response_body['errors'][key][0] + '\n';
                        elif isinstance(response_body['errors'][key], str):
                            error_msg = error_msg + response_body['errors'][key][0] + '\n';
        return error_msg

    @staticmethod
    def check_odata_body_structure(response_body):
        if not isinstance(response_body, dict):
            raise GuardPointError("Non-JSON Response Body")
        if '@odata.context' not in response_body:
            if 'error' in response_body:
                raise GuardPointError(response_body['error'])
            else:
                raise GuardPointError("Non-ODATA Response Body")
        if not str(response_body['@odata.context']).endswith("$entity"):
            # Non entities seem to always appear to contain 'value'
            check = False
            for item in response_body:
                if item in ['value', 'errorMessages', 'message', 'error']:
                    check = True
            if not check:
                raise GuardPointError("Response Body does not contain either('value', 'errorMessages', 'message', "
                                      "'error')")

        return response_body


class Stopwatch:

    def __init__(self):
        self._time = 0

    def start(self):
        self._time = time.time()
        return self

    def stop(self):
        self._time = time.time() - self._time

    def print(self, unit=None, precision=2, show_unit=1):
        division_table = {'h': 360, 'm': 60, 's': 1, 'ms': 0.001}
        unit_table = {'ms': "milliseconds", 's': "seconds", 'm': "minutes", 'h': "hours"}
        if unit not in division_table:
            for key, val in division_table.items():
                if self._time >= val:
                    unit = key
                    break
            else:
                unit = 'ms'
        unit_text = ""
        if show_unit == 1:
            unit_text = " " + unit
        elif show_unit == 2:
            unit_text = " " + unit_table[unit]
        elif show_unit == 3:
            unit_text = " " + unit_table[unit].capitalize()
        return f"{(self._time / division_table[unit]):.{precision}f}{unit_text}"

    def __str__(self):
        return str(self._time)

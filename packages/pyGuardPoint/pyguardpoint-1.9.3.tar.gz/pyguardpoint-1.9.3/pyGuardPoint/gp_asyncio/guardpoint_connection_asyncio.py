import logging
import json
import os
import ssl
from enum import Enum
from json import JSONDecodeError
from pathlib import Path
from tempfile import NamedTemporaryFile

import aiohttp
from aiohttp import InvalidURL
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.serialization import Encoding, PrivateFormat, BestAvailableEncryption, \
    pkcs12
from ..guardpoint_error import GuardPointUnauthorized
from ..guardpoint_utils import ConvertBase64, GuardPointResponse
import time

default_ca = """-----BEGIN CERTIFICATE-----
MIIELTCCAxWgAwIBAgIURU7qH0JVb8BlRd7S/LdrHi9fBEAwDQYJKoZIhvcNAQEL
BQAwgaUxCzAJBgNVBAYTAkdCMQ8wDQYDVQQIDAZTdXNzZXgxETAPBgNVBAcMCEJy
aWdodG9uMRowGAYDVQQKDBFTZW5zb3IgQWNjZXNzIEx0ZDEMMAoGA1UECwwDVk1T
MR8wHQYDVQQDDBZTZW5zb3IgQWNjZXNzIFZNUyBSb290MScwJQYJKoZIhvcNAQkB
FhhzYWxlc0BzZW5zb3JhY2Nlc3MuY28udWswHhcNMjIwNDIwMDk0NTQ5WhcNMzIw
NDE3MDk0NTQ5WjCBpTELMAkGA1UEBhMCR0IxDzANBgNVBAgMBlN1c3NleDERMA8G
A1UEBwwIQnJpZ2h0b24xGjAYBgNVBAoMEVNlbnNvciBBY2Nlc3MgTHRkMQwwCgYD
VQQLDANWTVMxHzAdBgNVBAMMFlNlbnNvciBBY2Nlc3MgVk1TIFJvb3QxJzAlBgkq
hkiG9w0BCQEWGHNhbGVzQHNlbnNvcmFjY2Vzcy5jby51azCCASIwDQYJKoZIhvcN
AQEBBQADggEPADCCAQoCggEBAKQQYYHRdfuwrvlPQ6qfaijtND2VIpo1KhN5AFnG
U6q79Iu1BerKFlazdSL1TsPEWdmHIvBnpLkzuW7IF4gGRzgRDPSK0v4Wjhl6a1lD
g1qKTOX/Z4Kc9espFIrlbA6B4TrbQsbePMSyca+Ru+qHvO30qqqZUNGR5s7G8wVl
dIhzccUPWGm9C6TyjFfL8lwqBVjYcWDP/iAlDfw1tcPodL1qcEd3EKHkASL8D7iE
nFoLSEcW15VZ68cdCufRPfxCmL7FjddmiQ/itildV2szX5hWxlQik6GRArDrKpnE
Dqigx1vxyE5896fwHmu1z5jMK0kzx6pzgutDKqVpBxodUBUCAwEAAaNTMFEwHQYD
VR0OBBYEFB00pM6wNS3yIFERdLKviHr0l6o2MB8GA1UdIwQYMBaAFB00pM6wNS3y
IFERdLKviHr0l6o2MA8GA1UdEwEB/wQFMAMBAf8wDQYJKoZIhvcNAQELBQADggEB
ACMXKnIGKAR3teHMmsHyu9cwm+T25FWQShRoI+YRGSpVemnnmz6xpetDs6KDRVy4
nEMdq24QO03ME8Z7luCBu0VHaZCdteu4QBrd5obbDSbfkHYnPnhwBhG+FTQt6pc8
hGsHW92XNwnQiAXATKNI/kxeqzsXxoMpKgfbDTT8bnNMLIXL1JxZKpguXsxc6wOd
mx9B6Vfbh9UnNgtnxsQUu9dCO0Ukczfpq902xK0QiKjYslH5kiypBskuhWxcEY3y
+Z0K2OQmT3LfJ1s1GNj799EIlti4HX81GPMZsTi7sjHeff+lyOgj8ezAT+QtnxAP
1MNRXg3aviuwZbDS2Juguf8=
-----END CERTIFICATE-----"""


class GuardPointAuthType(Enum):
    BASIC = 1
    BEARER_TOKEN = 2


log = logging.getLogger(__name__)


class GuardPointConnection:
    auto_renew = False
    session = None

    async def close(self):
        if self.session:
            await self.session.close()

    async def reopen(self):
        conn = aiohttp.TCPConnector(ssl_context=self.ssl_context)
        self.session = aiohttp.ClientSession(connector=conn)
    def open(self, url_components, auth, user, pwd, key, token=None,
             cert_file=None, key_file=None, key_pwd="", ca_file=None, p12_file=None, p12_pwd="", timeout=5):
        self.ssl_context = None
        self.url_components = url_components
        if not isinstance(auth, GuardPointAuthType):
            raise ValueError("Parameter authType must be instance of GuardPointAuthType")
        self.authType = auth
        self.user = user
        self.pwd = pwd
        self.key = key
        if url_components['host'] == '':
            raise ValueError("Invalid Connection URL")
        if url_components['scheme'] == '':
            url_components['scheme'] = 'http'

        self.baseurl = f"{url_components['scheme']}://{url_components['host']}"
        if url_components['port']:
            self.baseurl = self.baseurl + f":{url_components['port']}"

        if token:
            self.set_token(token)
        else:
            self.token = None
            self.token_issued = 0
            self.token_expiry = 0

        log.info(f"GP10 server connection: {self.baseurl}")
        # Loading System Defaults for TLS Client
        self.ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)

        p12_key_file = None
        p12_cert_file = None
        p12_ca_file = None
        if p12_file:
            if os.path.isfile(p12_file):
                # temporary files
                key_pwd = p12_pwd
                p12_key_file, p12_cert_file, p12_ca_file = GuardPointConnection.pfx_to_pems(p12_file, p12_pwd)
                if os.stat(p12_key_file.name).st_size > 0:
                    key_file = p12_key_file.name
                if os.stat(p12_cert_file.name).st_size > 0:
                    cert_file = p12_cert_file.name
                if os.stat(p12_ca_file.name).st_size > 0:
                    ca_file = p12_ca_file.name
                else:
                    # p12_ca_file.seek(0)
                    p12_ca_file.write(default_ca.encode())
                    p12_ca_file.flush()
                    ca_file = p12_ca_file.name
            else:
                raise ValueError(f"{p12_file} is not found.")

        if cert_file and key_file:
            # Loading of client certificate
            self.ssl_context.load_cert_chain(certfile=cert_file, keyfile=key_file, password=key_pwd)

        if ca_file:
            # Loading of CA certificate.
            self.ssl_context.load_verify_locations(cafile=ca_file)

        conn = aiohttp.TCPConnector(ssl_context=self.ssl_context)
        self.session = aiohttp.ClientSession(connector=conn)
        '''self.connection = http.client.HTTPSConnection(
            host=url_components['host'],
            port=url_components['port'],
            context=self.ssl_context)'''

        # Close temporary files
        if p12_key_file:
            p12_key_file.close()
            os.unlink(p12_key_file.name)
        if p12_cert_file:
            p12_cert_file.close()
            os.unlink(p12_cert_file.name)
        if p12_ca_file:
            p12_ca_file.close()
            os.unlink(p12_ca_file.name)

    def get_ssl_context(self):
        return self.ssl_context

    async def get_token(self):
        if not self.token:
            code, body = await self._new_token()
            if int(code) != 200:
                msg = GuardPointResponse.extract_error_msg(body)
                raise GuardPointUnauthorized(msg)
        return self.token

    def set_token(self, gp_token):
        self.token = gp_token
        token_dict = json.loads(ConvertBase64.decode(self.token.split(".")[1]))
        self.token_issued = token_dict['iat']
        self.token_expiry = token_dict['exp']

    async def renew_token(self):
        code, body = await self._renew_token()
        if int(code) != 200:
            msg = GuardPointResponse.extract_error_msg(body)
            raise GuardPointUnauthorized(msg)

    async def gp_json_query(self, method, url, json_body: dict = '', headers=None):
        if self.authType == GuardPointAuthType.BASIC:
            auth_str = "Basic " + ConvertBase64.encode(f"{self.user}:{self.key}")
        elif self.authType == GuardPointAuthType.BEARER_TOKEN:
            if self.token is None:
                code, auth_body = await self._new_token()
                if code != 200:
                    return code, auth_body
            if self.auto_renew:
                if self.token_expiry < (time.time() - (20 * 60)):  # If Token will expire within 20 minutes
                    code, auth_body = await self._renew_token()
                    if code != 200:
                        return code, auth_body
                if self.token_expiry < time.time():
                    code, auth_body = await self._new_token()
                    if code != 200:
                        return code, auth_body

            auth_str = f"Bearer {self.token}"
        else:
            raise NotImplementedError("Selected authentication mechanism not available.")

        return await self._query(method, url, json_body, headers, auth_str)

    async def _query(self, method, url, json_body: dict = None, headers=None, auth_str=None):
        raw_body = ''
        if json_body:
            if not isinstance(json_body, dict):
                raise ValueError("Variable 'json_body' must be of type dict.")
            else:
                raw_body = json.dumps(json_body)

        headers = headers or {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

        if auth_str:
            headers['Authorization'] = auth_str

        log.debug(f"Request data: host={self.baseurl}, {method}, {url}, {headers}, {raw_body}")
        url = self.baseurl + url

        if method.lower() == "get":
            try:
                async with self.session.get(url, headers=headers) as response:
                    body = await response.text()
                    try:
                        json_body = json.loads(body)
                    except JSONDecodeError:
                        json_body = None
                    except Exception as e:
                        log.error(e)
                        json_body = None
            except InvalidURL as e:
                log.error(str(e))
                return
            except Exception as e:
                log.error(str(e))
                return

        elif method.lower() == "post":
            async with self.session.post(url, data=raw_body, headers=headers) as response:
                body = await response.text()
                try:
                    json_body = json.loads(body)
                except JSONDecodeError:
                    json_body = None
                except Exception as e:
                    log.error(e)
                    json_body = None

        elif method.lower() == "patch":
            async with self.session.patch(url, data=raw_body, headers=headers) as response:
                body = await response.text()
                try:
                    json_body = json.loads(body)
                except JSONDecodeError:
                    json_body = None
                except Exception as e:
                    log.error(e)
                    json_body = None

        elif method.lower() == "delete":
            async with self.session.delete(url, data=raw_body, headers=headers) as response:
                body = await response.text()
                try:
                    json_body = json.loads(body)
                except JSONDecodeError:
                    json_body = None
                except Exception as e:
                    log.error(e)
                    json_body = None

        elif method.lower() == "put":
            async with self.session.put(url, data=raw_body, headers=headers) as response:
                body = await response.text()
                try:
                    json_body = json.loads(body)
                except JSONDecodeError:
                    json_body = None
                except Exception as e:
                    log.error(e)
                    json_body = None

        else:
            raise ValueError("Method Not Supported")

        return response.status, json_body

    async def _new_token(self):
        log.info("Requesting new token")
        payload = {"username": self.user,
                   "password": self.pwd}
        url = "/api/Token/"
        return await self._query_token(url, payload)

    async def _renew_token(self):
        log.info("Renewing token")
        payload = {"oldToken": self.token}
        url = "/api/Token/RenewToken"
        return await self._query_token(url, payload)

    async def _query_token(self, url, json_payload):
        if self.token:
            auth_str = f"Bearer {self.token}"
        else:
            auth_str = None
        code, json_body = await self._query("POST", url, json_payload, headers=None, auth_str=auth_str)

        if code == 200:
            try:
                self.token = json_body['token']
                token_dict = json.loads(ConvertBase64.decode(self.token.split(".")[1]))
                self.token_issued = token_dict['iat']
                self.token_expiry = token_dict['exp']
            except JSONDecodeError:
                json_body = None
            except Exception as e:
                log.error(e)
                json_body = None

        return code, json_body

    @staticmethod
    def pfx_to_pems(pfx_path, pfx_password):
        ''' Decrypts the .pfx file to be used with requests. '''
        pfx = Path(pfx_path).read_bytes()
        private_key, main_cert, add_certs = pkcs12.load_key_and_certificates(pfx, pfx_password.encode('utf-8'),
                                                                             default_backend())

        key_file = NamedTemporaryFile(suffix='.pem', delete=False)
        key_file.write(private_key.private_bytes(Encoding.PEM, PrivateFormat.PKCS8,
                                                 BestAvailableEncryption(pfx_password.encode('utf-8'))))
        key_file.flush()

        cert_file = NamedTemporaryFile(suffix='.pem', delete=False)
        cert_file.write(main_cert.public_bytes(Encoding.PEM))
        cert_file.flush()

        ca_file = NamedTemporaryFile(suffix='.pem', delete=False)
        for ca in add_certs:
            ca_file.write(ca.public_bytes(Encoding.PEM))
        ca_file.flush()

        return key_file, cert_file, ca_file

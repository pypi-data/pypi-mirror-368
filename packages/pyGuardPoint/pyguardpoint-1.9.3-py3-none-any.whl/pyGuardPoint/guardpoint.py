import asyncio
import logging

import validators
from pysignalr.client import SignalRClient

from .CustomWebsocketTransport import CustomWebsocketTransport, DEFAULT_PING_INTERVAL, DEFAULT_CONNECTION_TIMEOUT, \
    DEFAULT_MAX_SIZE
from ._guardpoint_alarmstates import AlarmStatesAPI
from ._guardpoint_alarmzones import AlarmZonesAPI
from ._guardpoint_cardholdertypes import CardholderTypesAPI
from ._guardpoint_controllers import ControllersAPI
from ._guardpoint_diagnostic import DiagnosticAPI
from ._guardpoint_departments import DepartmentsAPI
from ._guardpoint_genericinformation import GenericInfoAPI
from ._guardpoint_sites import SitesAPI
from ._guardpoint_events import EventsAPI
from ._guardpoint_ouputs import OutputsAPI
from ._guardpoint_readers import ReadersAPI
from ._guardpoint_scheduledmags import ScheduledMagsAPI
from ._guardpoint_customizedfields import CustomizedFieldsAPI
from ._guardpoint_personaldetails import PersonalDetailsAPI
from ._guardpoint_securitygroups import SecurityGroupsAPI
from ._guardpoint_accessgroups import AccessGroupsAPI
from .guardpoint_connection import GuardPointConnection, GuardPointAuthType
from ._guardpoint_cards import CardsAPI
from ._guardpoint_cardholders import CardholdersAPI
from .guardpoint_error import GuardPointError, GuardPointUnauthorized
from ._guardpoint_areas import AreasAPI
from .guardpoint_utils import url_parser, ConvertBase64

log = logging.getLogger(__name__)


def stop_listening(client: SignalRClient):
    async def stop_signal_client() -> None:
        await client._transport.close()

    asyncio.run(stop_signal_client())


class GuardPoint(GuardPointConnection, CardsAPI, CardholdersAPI, AreasAPI, SecurityGroupsAPI, CustomizedFieldsAPI,
                 PersonalDetailsAPI, ScheduledMagsAPI, CardholderTypesAPI, OutputsAPI, DiagnosticAPI, ReadersAPI,
                 ControllersAPI, AlarmStatesAPI, EventsAPI, DepartmentsAPI, SitesAPI, AccessGroupsAPI, GenericInfoAPI,
                 AlarmZonesAPI):
    """
    A class to interface with the GuardPoint system, providing various APIs for managing cards, cardholders, areas,
    security groups, customized fields, personal details, scheduled mags, cardholder types, outputs, diagnostics,
    readers, controllers, alarms, and events.

    This class inherits from multiple API classes to provide a comprehensive interface for interacting with the
    GuardPoint system.

    Methods
    -------
    __init__(kwargs)
        Initializes the GuardPoint instance with the provided configuration.
    get_cardholder_count()
        Retrieves the total number of cardholders.
    get_signal_client()
        Creates and returns a SignalR client for event listening.
    start_listening(client: SignalRClient)
        Starts the SignalR client for listening to events.
    """

    task = None

    def __init__(self, **kwargs):
        """
        Initialize the connection with the given parameters.

        :param kwargs:
        See below

        :Keyword Arguments:
            * host (str): The hostname or IP address of the server. Defaults to "localhost".
            * port (int): The port number to connect to. Defaults to None.
            * auth (GuardPointAuthType): The authentication type. Defaults to GuardPointAuthType.BEARER_TOKEN.
            * username (str): The username for authentication. Defaults to "admin".
            * pwd (str): The password for authentication. Defaults to "admin".
            * key (str): The key for authentication. Defaults to "00000000-0000-0000-0000-000000000000".
            * token (str): The token for authentication. Defaults to None.
            * cert_file (str): Path to the certificate file. Defaults to None.
            * key_file (str): Path to the key file. Defaults to None.
            * ca_file (str): Path to the CA file. Defaults to None.
            * timeout (int): The timeout duration in seconds. Defaults to 5.
            * p12_file (str): Path to the PKCS#12 file. Defaults to None.
            * p12_pwd (str): Password for the PKCS#12 file. Defaults to an empty string.
            * site_uid (str): The UID of the site. Defaults to None.

        :raises ValueError: If the host is not provided or is invalid.
        """
        # Set default values if not present
        host = kwargs.get('host', "localhost")
        port = kwargs.get('port', None)
        url_components = url_parser(host)
        if url_components['host'] == '':
            url_components['host'] = url_components['path']
            url_components['path'] = ''
        if port:
            url_components['port'] = port
        auth = kwargs.get('auth', GuardPointAuthType.BEARER_TOKEN)
        user = kwargs.get('username', "admin")
        pwd = kwargs.get('pwd', "admin")
        key = kwargs.get('key', "00000000-0000-0000-0000-000000000000")
        token = kwargs.get('token', None)
        certfile = kwargs.get('cert_file', None)
        keyfile = kwargs.get('key_file', None)
        cafile = kwargs.get('ca_file', None)
        timeout = kwargs.get('timeout', 5)
        p12_file = kwargs.get('p12_file', None)
        p12_pwd = kwargs.get('p12_pwd', "")

        self.site_uid = kwargs.get('site_uid', None)
        if self.site_uid is not None:
            if not validators.uuid(self.site_uid):
                raise ValueError(f'Malformed Site UID {self.site_uid}')

        super().__init__(url_components=url_components, auth=auth, user=user, pwd=pwd, key=key, token=token,
                         cert_file=certfile, key_file=keyfile, ca_file=cafile, timeout=timeout,
                         p12_file=p12_file, p12_pwd=p12_pwd)

    def get_cardholder_count(self):
        """
        Retrieve the total count of cardholders from the GuardPoint system.

        This method sends a GET request to the GuardPoint API to fetch the total number of cardholders.
        It handles various error scenarios, including unauthorized access and improperly formatted responses.

        :raises GuardPointUnauthorized: If the API response indicates unauthorized access (HTTP 401).
        :raises GuardPointError: If the API response is not properly formatted or if there is no response body.

        :return: The total number of cardholders.
        :rtype: int
        """
        url = self.baseurl + "/odata/GetCardholdersCount"
        code, json_body = self.gp_json_query("GET", url=url)

        if code != 200:
            error_msg = ""
            if isinstance(json_body, dict):
                if 'error' in json_body:
                    error_msg = json_body['error']

            if code == 401:
                raise GuardPointUnauthorized(f"Unauthorized - ({error_msg})")
            else:
                raise GuardPointError(f"No body - ({code})")

        # Check response body is formatted as expected
        if not isinstance(json_body, dict):
            raise GuardPointError("Badly formatted response.")
        if 'totalItems' not in json_body:
            raise GuardPointError("Badly formatted response.")

        return int(json_body['totalItems'])

    def get_signal_client(self):
        """
        Creates and configures a SignalR client for connecting to the EventsHub.

        This method initializes a `SignalRClient` instance with the appropriate URL and sets up
        the necessary headers for authentication based on the specified authentication type.
        It also configures a custom WebSocket transport for the client with various parameters.

        :returns: Configured `SignalRClient` instance ready for use.
        :rtype: SignalRClient

        :raises ValueError: If the authentication type is not supported.

        Example usage::

            client = self.get_signal_client()
            client.start()

        """
        token_factory = None
        if self.authType == GuardPointAuthType.BEARER_TOKEN:
            def get_bearer():
                return "Bearer " + self.get_token()
            token_factory = get_bearer
        else:
            def get_basic():
                return "Basic " + ConvertBase64.encode(f"{self.user}:{self.key}")
            token_factory = get_basic

        client = SignalRClient(url=self.baseurl + "/Hub/EventsHub",
                               access_token_factory=token_factory,
                               ssl=self.get_ssl_context())

        client._transport = CustomWebsocketTransport(
            url=client._url,
            protocol=client._protocol,
            callback=client._on_message,
            headers=client._headers,
            access_token_factory=client._access_token_factory,
            ssl=client._ssl,
        )

        return client

    def start_listening(self, client: SignalRClient):
        """
        Start listening to the SignalR client by running it in an asynchronous task.

        This method creates and runs an asynchronous task to execute the `run` method of the provided
        `SignalRClient` instance. The task is named "sigR_task" for identification purposes. If the task
        is cancelled, a message indicating the cancellation is printed.

        :param client: An instance of `SignalRClient` that will be run in an asynchronous task.
        :type client: SignalRClient

        :raises asyncio.CancelledError: If the asynchronous task is cancelled.
        """

        async def run_signal_client() -> None:
            self.task = asyncio.create_task(client.run(), name="sigR_task")
            await self.task

        try:
            asyncio.run(run_signal_client())
        except asyncio.CancelledError:
            print(f"{self.task.get_name()} cancelled")

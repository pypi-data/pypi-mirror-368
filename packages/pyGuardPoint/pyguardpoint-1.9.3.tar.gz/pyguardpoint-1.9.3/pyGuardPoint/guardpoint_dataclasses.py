import logging
from collections import defaultdict
from dataclasses import dataclass, asdict, field
from enum import Enum

log = logging.getLogger(__name__)


class AlarmZoneOption(Enum):
    ReturnAlarmZoneToWeeklyProgram = 1


class EventOrder(Enum):
    DATETIME_ASC = 1
    DATETIME_DESC = 2
    LOG_ID_ASC = 3
    LOG_ID_DESC = 4


class Observable:
    # A set of all attributes which get changed
    changed_attributes = set()

    def __init__(self):
        self.observed = defaultdict(list)

    def __setattr__(self, name, value):
        super().__setattr__(name, value)

        for observer in self.observed.get(name, []):
            observer(name)

    def add_observer(self, name):
        self.observed[name].append(lambda name: self.changed_attributes.add(name))


def sanitise_args(obj: Observable, args, kwargs):
    kwarg_dict = dict()
    obj.changed_attributes = set()

    for arg in args:
        if isinstance(arg, dict):
            kwarg_dict.update(arg)

    for k, v in kwargs.items():
        if hasattr(type(obj), k):
            kwarg_dict[k] = v
            obj.changed_attributes.add(k)
        else:
            log.debug(f"{obj.__class__.__name__}.{k} - attribute ignored.")
            # raise ValueError(f"No such attribute: {k}")

    return kwarg_dict


class SortAlgorithm(Enum):
    SERVER_DEFAULT = 0,
    FUZZY_MATCH = 1


class CardholderOrderBy(Enum):
    fromDateValid_DESC = 0,
    lastPassDate_DESC = 1


@dataclass
class AlarmState:
    acknowledgedDate: any = None
    acknowledgedUserUID: any = None
    alarmType: str = ""
    controllerUID: str = ""
    endAlarmDate: str = ""
    input: any = None
    inputUID: str = ""
    isAcknowledged: bool = False
    isDelayed: bool = False
    isInputAlarm: bool = False
    isPastEvent: bool = False
    startAlarmDate: str = ""
    technicalAlarmType: any = None
    uid: str = ""

    def __init__(self, *args, **kwargs):
        super().__init__()
        alarm_state_dict = sanitise_args(self, args, kwargs)

        for property_name in alarm_state_dict:
            if isinstance(alarm_state_dict[property_name], (str, type(None), bool, int, dict)):
                setattr(self, property_name, alarm_state_dict[property_name])

    def dict(self):
        alarm_state_dict = {}
        for k, v in asdict(self).items():
            if isinstance(v, (list, dict, bool, int)):
                alarm_state_dict[k] = v
            elif isinstance(v, type(None)):
                alarm_state_dict[k] = None
            else:
                alarm_state_dict[k] = str(v)


@dataclass
class AlarmZone:
    alarmStatus: str = ""
    description: any = None
    galaxyAlarmState: int = 0
    galaxyControllerUID: any = None
    galaxyGroupNum: any = None
    galaxyState: int = 0
    isGalaxy: bool = False
    isRealTimeStatusArm: bool = False
    iswpStatusArm: bool = False
    lastAlarmActionDate: str = ""
    lastOperationDateTime: str = ""
    manualActionDurationMinutes: any = None
    manualActionDurationSeconds: any = None
    manualActionType: int = 0
    manualActionUserUID: any = None
    name: str = ""
    preAlarmDelay: int = 0
    preAlarmProcessUID: any = None
    uid: str = ""
    wasPastConstantArm: any = None
    wasWPArmWhenManualDefined: bool = False
    weeklyProgramUID: str = ""

    def __init__(self, *args, **kwargs):
        super().__init__()
        alarm_zone_dict = sanitise_args(self, args, kwargs)

        for property_name in alarm_zone_dict:
            if isinstance(alarm_zone_dict[property_name], (str, type(None), bool, int)):
                setattr(self, property_name, alarm_zone_dict[property_name])

    def dict(self):
        alarm_zone_dict = {}
        for k, v in asdict(self).items():
            if isinstance(v, (list, dict, bool, int)):
                alarm_zone_dict[k] = v
            elif isinstance(v, type(None)):
                alarm_zone_dict[k] = None
            else:
                alarm_zone_dict[k] = str(v)

        return alarm_zone_dict


@dataclass
class Site:
    apiKey: any = None
    baudrate: int = 9600
    defaultCardholderDagUIDs: str = ""
    defaultCardholderLagUIDs: str = ""
    defaultCardholderMagUID: str = ""
    description: any = None
    firstWorkDayInWeek: any = None
    hasSpecialDays: bool = False
    isPolling: bool = False
    name: str = ""
    uid: str = ""

    def __init__(self, *args, **kwargs):
        super().__init__()
        site_dict = sanitise_args(self, args, kwargs)

        for property_name in site_dict:
            if isinstance(site_dict[property_name], (str, type(None), bool, int)):
                setattr(self, property_name, site_dict[property_name])

    def dict(self):
        site_dict = {}
        for k, v in asdict(self).items():
            if isinstance(v, (list, dict, bool, int)):
                site_dict[k] = v
            elif isinstance(v, type(None)):
                site_dict[k] = None
            else:
                site_dict[k] = str(v)

        return site_dict


@dataclass
class Department:
    defaultMultipleAccessGroupUID: any = None
    description: any = None
    name: str = ""
    parentUID: str = ""
    uid: str = ""

    def __init__(self, *args, **kwargs):
        super().__init__()
        department_dict = sanitise_args(self, args, kwargs)

        for property_name in department_dict:
            if isinstance(department_dict[property_name], (str, type(None), bool, int)):
                setattr(self, property_name, department_dict[property_name])

    def dict(self):
        department_dict = {}
        for k, v in asdict(self).items():
            if isinstance(v, (list, dict, bool, int)):
                department_dict[k] = v
            elif isinstance(v, type(None)):
                department_dict[k] = None
            else:
                department_dict[k] = str(v)

        return department_dict


@dataclass
class AuditEvent:
    uid: str = ""
    dateTime: str = ""
    userUID: str = ""
    objectName: any = None
    type: any = None
    userFirstName: any = None
    operationName: any = None
    userLastName: any = None
    journalUpdateDateTime: str = ""
    data: str = ""
    userName: any = None
    ownerSiteUID: str = ""
    additionalSites: any = None
    ownerSiteName: str = ""
    additionalSitesNames: any = None

    def __init__(self, *args, **kwargs):
        super().__init__()
        audit_event_dict = sanitise_args(self, args, kwargs)

        for property_name in audit_event_dict:
            if isinstance(audit_event_dict[property_name], (str, type(None), bool, int)):
                setattr(self, property_name, audit_event_dict[property_name])

    def dict(self):
        audit_event_dict = {}
        for k, v in asdict(self).items():
            if isinstance(v, (list, dict, bool, int)):
                audit_event_dict[k] = v
            elif isinstance(v, type(None)):
                audit_event_dict[k] = None
            else:
                audit_event_dict[k] = str(v)

        return audit_event_dict


@dataclass
class AlarmEvent:
    additionalSites: any = None
    additionalSitesNames: any = None
    alarmUID: str = ""
    confirmationComments: any = None
    dateTime: str = ""
    inputName: str = ""
    inputUID: str = ""
    isAcknowledged: bool = False
    isConfirmed: bool = False
    isPastEvent: bool = False
    journalUpdateDateTime: str = ""
    ownerSiteName: str = ""
    ownerSiteUID: str = ""
    type: str = ""
    uid: str = ""
    userFirstName: any = None
    userLastName: any = None
    userName: any = None
    userUID: any = None

    def __init__(self, *args, **kwargs):
        super().__init__()
        alarm_event_dict = sanitise_args(self, args, kwargs)

        for property_name in alarm_event_dict:
            if isinstance(alarm_event_dict[property_name], (str, type(None), bool, int)):
                setattr(self, property_name, alarm_event_dict[property_name])

    def dict(self):
        alarm_event_dict = {}
        for k, v in asdict(self).items():
            if isinstance(v, (list, dict, bool, int)):
                alarm_event_dict[k] = v
            elif isinstance(v, type(None)):
                alarm_event_dict[k] = None
            else:
                alarm_event_dict[k] = str(v)

        return alarm_event_dict


@dataclass
class AccessEvent:
    """
    Represents an access event with various attributes related to cardholder and access details.

    :param accessDeniedCode: Code indicating the reason for access denial.
    :type accessDeniedCode: str
    :param cardCode: Code of the card used for access.
    :type cardCode: str
    :param cardholderFirstName: First name of the cardholder.
    :type cardholderFirstName: any
    :param cardholderIdNumber: Identification number of the cardholder.
    :type cardholderIdNumber: any
    :param cardholderLastName: Last name of the cardholder.
    :type cardholderLastName: any
    :param cardholderTypeName: Type name of the cardholder.
    :type cardholderTypeName: any
    :param cardholderTypeUID: Unique identifier for the cardholder type.
    :type cardholderTypeUID: any
    :param cardholderUID: Unique identifier for the cardholder.
    :type cardholderUID: str
    :param carRegistrationNum: Car registration number associated with the cardholder.
    :type carRegistrationNum: any
    :param dateTime: Date and time of the access event.
    :type dateTime: str
    :param escortCardCode: Code of the escort's card.
    :type escortCardCode: any
    :param escortFirstName: First name of the escort.
    :type escortFirstName: any
    :param escortLastName: Last name of the escort.
    :type escortLastName: any
    :param escortUID: Unique identifier for the escort.
    :type escortUID: any
    :param inOutType: Type of access (in or out).
    :type inOutType: any
    :param isEscort: Indicates if the cardholder is an escort.
    :type isEscort: bool
    :param isPastEvent: Indicates if the event is a past event.
    :type isPastEvent: bool
    :param isSlave: Indicates if the event is a slave event.
    :type isSlave: bool
    :param journalUpdateDateTime: Date and time when the journal was last updated.
    :type journalUpdateDateTime: str
    :param logID: Log identifier for the access event.
    :type logID: int
    :param readerFunctionCodes: List of function codes for the reader.
    :type readerFunctionCodes: list
    :param readerName: Name of the reader.
    :type readerName: str
    :param readerUID: Unique identifier for the reader.
    :type readerUID: str
    :param transactionCode: Code representing the transaction type.
    :type transactionCode: int
    :param type: Type of the access event.
    :type type: str
    :param uid: Unique identifier for the access event.
    :type uid: str
    :param ownerSiteUID: Unique identifier for the owner site.
    :type ownerSiteUID: str
    :param additionalSites: Additional sites associated with the event.
    :type additionalSites: any
    :param ownerSiteName: Name of the owner site.
    :type ownerSiteName: str
    :param additionalSitesNames: Names of additional sites associated with the event.
    :type additionalSitesNames: any
    :param additionalInfo: Additional information related to the access event.
    :type additionalInfo: any

    :ivar accessDeniedCode: Code indicating the reason for access denial.
    :ivar cardCode: Code of the card used for access.
    :ivar cardholderFirstName: First name of the cardholder.
    :ivar cardholderIdNumber: Identification number of the cardholder.
    :ivar cardholderLastName: Last name of the cardholder.
    :ivar cardholderTypeName: Type name of the cardholder.
    :ivar cardholderTypeUID: Unique identifier for the cardholder type.
    :ivar cardholderUID: Unique identifier for the cardholder.
    :ivar carRegistrationNum: Car registration number associated with the cardholder.
    :ivar dateTime: Date and time of the access event.
    :ivar escortCardCode: Code of the escort's card.
    :ivar escortFirstName: First name of the escort.
    :ivar escortLastName: Last name of the escort.
    :ivar escortUID: Unique identifier for the escort.
    :ivar inOutType: Type of access (in or out).
    :ivar isEscort: Indicates if the cardholder is an escort.
    :ivar isPastEvent: Indicates if the event is a past event.
    :ivar isSlave: Indicates if the event is a slave event.
    :ivar journalUpdateDateTime: Date and time when the journal was last updated.
    :ivar logID: Log identifier for the access event.
    :ivar readerFunctionCodes: List of function codes for the reader.
    :ivar readerName: Name of the reader.
    :ivar readerUID: Unique identifier for the reader.
    :ivar transactionCode: Code representing the transaction type.
    :ivar type: Type of the access event.
    :ivar uid: Unique identifier for the access event.
    :ivar ownerSiteUID: Unique identifier for the owner site.
    :ivar additionalSites: Additional sites associated with the event.
    :ivar ownerSiteName: Name of the owner site.
    :ivar additionalSitesNames: Names of additional sites associated with the event.
    :ivar additionalInfo: Additional information related to the access event.

    :raises ValueError: If any of the provided arguments are invalid.

    :example:
    >>> event = AccessEvent(cardCode="12345", dateTime="2023-10-01T12:00:00Z")
    >>> event.dict()
    {'accessDeniedCode': '', 'cardCode': '12345', 'cardholderFirstName': None, ...}

    Methods
    -------
    __init__(*args, kwargs)
        Initializes an AccessEvent instance with the provided arguments.
    dict()
        Converts the AccessEvent instance to a dictionary representation.
    """
    accessDeniedCode: str = ""
    cardCode: str = ""
    cardholderFirstName: any = None
    cardholderIdNumber: any = None
    cardholderLastName: any = None
    cardholderTypeName: any = None
    cardholderTypeUID: any = None
    cardholderUID: str = ""
    carRegistrationNum: any = None
    dateTime: str = ""
    escortCardCode: any = None
    escortFirstName: any = None
    escortLastName: any = None
    escortUID: any = None
    inOutType: any = None
    isEscort: bool = False
    isPastEvent: bool = False
    isSlave: bool = False
    journalUpdateDateTime: str = ""
    logID: int = 0
    readerFunctionCodes: list = None
    readerName: str = ""
    readerUID: str = ""
    transactionCode: int = 0
    type: str = ""
    uid: str = ""
    ownerSiteUID: str = ""
    additionalSites: any = None
    ownerSiteName: str = ""
    additionalSitesNames: any = None
    additionalInfo: any = None

    def __init__(self, *args, **kwargs):
        super().__init__()
        access_event_dict = sanitise_args(self, args, kwargs)

        for property_name in access_event_dict:
            if isinstance(access_event_dict[property_name], (str, type(None), bool, int)):
                setattr(self, property_name, access_event_dict[property_name])

    def dict(self):
        access_event_dict = {}
        for k, v in asdict(self).items():
            if isinstance(v, (list, dict, bool, int)):
                access_event_dict[k] = v
            elif isinstance(v, type(None)):
                access_event_dict[k] = None
            else:
                access_event_dict[k] = str(v)

        return access_event_dict


@dataclass
class Controller:
    isActivated: any = None
    uid: str = ""
    address: int = 0
    networkUID: str = ""
    name: str = ""
    isPooling: any = None
    status: str = ""
    purpose: str = ""
    isConnected: any = None
    disconnectTime: str = ""
    description: any = None
    script: str = ""
    firmwareVersion: str = ""
    hardwareVersion: str = ""
    apiKey: any = None

    def __init__(self, *args, **kwargs):
        super().__init__()
        controller_dict = sanitise_args(self, args, kwargs)

        for property_name in controller_dict:
            if isinstance(controller_dict[property_name], (str, type(None), bool, int)):
                setattr(self, property_name, controller_dict[property_name])

    def dict(self):
        controller_dict = {}
        for k, v in asdict(self).items():
            if isinstance(v, (list, dict, bool, int)):
                controller_dict[k] = v
            elif isinstance(v, type(None)):
                controller_dict[k] = None
            else:
                controller_dict[k] = str(v)

        return controller_dict


@dataclass
class Reader:
    uid: str = ""
    name: str = ""
    description: any = None
    number: int = 0
    controllerUID: str = ""
    firstOutputUID: any = None
    secondOutputUID: any = None
    weeklyProgramUID: any = None
    readerFunctionIDs: any = None
    apiKey: any = None
    doorAlarmInputUID: str = ""
    doorControlInput1UID: any = None
    doorControlInput2UID: any = None
    doorRemoteInputUID: str = ""
    motorizedReaderInputUID: any = None

    def __init__(self, *args, **kwargs):
        super().__init__()
        reader_dict = sanitise_args(self, args, kwargs)

        for property_name in reader_dict:
            if isinstance(reader_dict[property_name], (str, type(None), bool, int)):
                setattr(self, property_name, reader_dict[property_name])

    def dict(self):
        reader_dict = {}
        for k, v in asdict(self).items():
            if isinstance(v, (list, dict, bool, int)):
                reader_dict[k] = v
            elif isinstance(v, type(None)):
                reader_dict[k] = None
            else:
                reader_dict[k] = str(v)

        return reader_dict


@dataclass
class Relay(Observable):
    digitalOutputStatus: str = ""
    uid: str = ""
    number: int = 0
    name: str = ""
    description: any = None
    weeklyProgramUID: any = None
    controllerUID: str = ""
    liftReaderUID: any = None
    constantState: str = ""
    apiKey: any = None

    def __init__(self, *args, **kwargs):
        super().__init__()
        relay_dict = sanitise_args(self, args, kwargs)

        for property_name in relay_dict:
            if isinstance(relay_dict[property_name], (str, type(None), bool, int)):
                setattr(self, property_name, relay_dict[property_name])

        # Monitor Changes
        for k, v in asdict(self).items():
            if isinstance(v, (str, type(None), bool, int)):
                self.add_observer(k)

    def _remove_non_changed(self, relay_dict: dict):
        for key, value in list(relay_dict.items()):
            if key not in self.changed_attributes:
                relay_dict.pop(key)
        return relay_dict

    def dict(self, editable_only=False, changed_only=False):
        relay_dict = {}
        for k, v in asdict(self).items():
            if isinstance(v, (list, dict, bool, int)):
                relay_dict[k] = v
            elif isinstance(v, type(None)):
                relay_dict[k] = None
            else:
                relay_dict[k] = str(v)

        if editable_only:
            if 'uid' in relay_dict:
                relay_dict.pop('uid')

        if changed_only:
            relay_dict = self._remove_non_changed(relay_dict)

        return relay_dict


@dataclass
class Card(Observable):
    technologyType: int = 0
    description: str = ""
    cardCode: str = ""
    status: str = "Free"
    cardholderUID: any = None
    cardType: str = "Magnetic"
    readerFunctionUID: any = None
    uid: str = ""

    def __init__(self, *args, **kwargs):
        super().__init__()
        card_dict = sanitise_args(self, args, kwargs)

        for property_name in card_dict:
            if isinstance(card_dict[property_name], (str, type(None), bool, int)):
                setattr(self, property_name, card_dict[property_name])

        # Monitor Changes
        for k, v in asdict(self).items():
            if isinstance(v, (str, type(None), bool, int)):
                self.add_observer(k)

    def _remove_non_changed(self, ch: dict):
        for key, value in list(ch.items()):
            if key not in self.changed_attributes:
                ch.pop(key)
        return ch

    def dict(self, editable_only=False, changed_only=False):
        c = {}
        for k, v in asdict(self).items():
            if isinstance(v, (list, dict, bool, int)):
                c[k] = v
            elif isinstance(v, type(None)):
                c[k] = None
            else:
                c[k] = str(v)

        if editable_only:
            if 'uid' in c:
                c.pop('uid')
            if 'readerFunctionUID' in c:
                c.pop('readerFunctionUID')

        if changed_only:
            c = self._remove_non_changed(c)

        return c


@dataclass
class Area:
    uid: str = ""
    name: str = ""

    def __init__(self, area_dict: dict):
        for property_name in area_dict:
            if isinstance(area_dict[property_name], (str, type(None), bool, int)):
                setattr(self, property_name, area_dict[property_name])

    def dict(self):
        return {k: str(v) for k, v in asdict(self).items()}


@dataclass
class AccessGroup:
    accessGroupType: str = ""
    uid: str = ""
    name: str = ""
    apiKey: any = ""
    description: str = ""
    ownerSiteUID: str = ""

    def __init__(self, access_group_dict: dict):
        for property_name in access_group_dict:
            if isinstance(access_group_dict[property_name], (str, type(None), bool, int)):
                setattr(self, property_name, access_group_dict[property_name])

    def dict(self):
        return {k: str(v) for k, v in asdict(self).items()}


@dataclass
class SecurityGroup:
    ownerSiteUID: str = ""
    uid: str = ""
    name: str = ""
    apiKey: any = ""
    description: str = ""
    isAppliedToVisitor: bool = False

    def __init__(self, security_group_dict: dict):
        for property_name in security_group_dict:
            if isinstance(security_group_dict[property_name], (str, type(None), bool, int)):
                setattr(self, property_name, security_group_dict[property_name])

    def dict(self):
        return {k: str(v) for k, v in asdict(self).items()}


@dataclass
class ScheduledMag(Observable):
    uid: str = ""
    securityGroupAPIKey: str = ""
    scheduledSecurityGroupUID: str = ""
    cardholderUID: str = ""
    toDateValid: str = ""
    fromDateValid: str = ""
    status: str = ""

    def __init__(self, *args, **kwargs):
        super().__init__()
        scheduled_mags_dict = sanitise_args(self, args, kwargs)

        # Initialise clss attributes from dictionary
        for property_name in scheduled_mags_dict:
            if isinstance(scheduled_mags_dict[property_name], (str, type(None), bool, int)):
                setattr(self, property_name, scheduled_mags_dict[property_name])
                self.add_observer(property_name)

    def dict(self, editable_only=False):
        c = {}
        for k, v in asdict(self).items():
            if isinstance(v, (list, dict, bool, int)):
                c[k] = v
            elif isinstance(v, type(None)):
                c[k] = None
            else:
                c[k] = str(v)

        if editable_only:
            if 'uid' in c:
                c.pop('uid')
            if 'status' in c:
                c.pop('status')

        return c


@dataclass
class CardholderCustomizedField(Observable):
    uid: str = ""
    cF_BoolField_1: bool = False,
    cF_BoolField_2: bool = False
    cF_BoolField_3: bool = False
    cF_BoolField_4: bool = False
    cF_BoolField_5: bool = False
    cF_IntField_1: int = 0
    cF_IntField_2: int = 0
    cF_IntField_3: int = 0
    cF_IntField_4: int = 0
    cF_IntField_5: int = 0
    cF_DateTimeField_1: any = None
    cF_DateTimeField_2: any = None
    cF_DateTimeField_3: any = None
    cF_DateTimeField_4: any = None
    cF_DateTimeField_5: any = None
    cF_StringField_1: str = ""
    cF_StringField_2: str = ""
    cF_StringField_3: str = ""
    cF_StringField_4: str = ""
    cF_StringField_5: str = ""
    cF_StringField_6: str = ""
    cF_StringField_7: str = ""
    cF_StringField_8: str = ""
    cF_StringField_9: str = ""
    cF_StringField_10: str = ""
    cF_StringField_11: str = ""
    cF_StringField_12: str = ""
    cF_StringField_13: str = ""
    cF_StringField_14: str = ""
    cF_StringField_15: str = ""
    cF_StringField_16: str = ""
    cF_StringField_17: str = ""
    cF_StringField_18: str = ""
    cF_StringField_19: str = ""
    cF_StringField_20: str = ""

    def __init__(self, *args, **kwargs):
        super().__init__()
        custom_fields_dict = sanitise_args(self, args, kwargs)

        for property_name in custom_fields_dict:
            if isinstance(custom_fields_dict[property_name], (str, type(None), bool, int)):
                setattr(self, property_name, custom_fields_dict[property_name])

        # Monitor Changes
        for k, v in asdict(self).items():
            if isinstance(v, (str, type(None), bool, int)):
                self.add_observer(k)

    def dict(self, changed_only=False):
        c = dict()
        for k, v in asdict(self).items():
            if isinstance(v, (bool, int)):
                c[k] = v
            elif isinstance(v, int):
                c[k] = v
            elif isinstance(v, type(None)):
                c[k] = None
            else:
                c[k] = str(v)

        if changed_only:
            c = self._remove_non_changed(c)

        return c

    def _remove_non_changed(self, ch: dict):
        for key, value in list(ch.items()):
            if key not in self.changed_attributes:
                ch.pop(key)
        return ch


@dataclass
class CardholderPersonalDetail(Observable):
    uid: str = ""
    officePhone: str = ""
    cityOrDistrict: str = ""
    streetOrApartment: str = ""
    postCode: str = ""
    privatePhoneOrFax: str = ""
    mobile: str = ""
    email: str = ""
    carRegistrationNum: str = ""
    company: str = ""
    idFreeText: str = ""
    idType: str = "IdentityCard"

    def __init__(self, *args, **kwargs):
        super().__init__()
        person_details_dict = sanitise_args(self, args, kwargs)

        for property_name in person_details_dict:
            if isinstance(person_details_dict[property_name], (str, type(None), bool, int)):
                setattr(self, property_name, person_details_dict[property_name])

        # Monitor Changes
        for k, v in asdict(self).items():
            if isinstance(v, (str, type(None), bool, int)):
                self.add_observer(k)

    def dict(self, editable_only=False, changed_only=False, non_empty_only=False):
        ch = dict()

        for k, v in asdict(self).items():
            if isinstance(v, (list, dict, bool, int)):
                ch[k] = v
            elif isinstance(v, type(None)):
                pass
                # ch[k] = None
            elif isinstance(v, str):
                if non_empty_only:
                    if len(v) > 0:
                        ch[k] = str(v)
                else:
                    ch[k] = str(v)
            else:
                pass

        if changed_only:
            ch = self._remove_non_changed(ch)

        if editable_only:
            ch = self._remove_non_editable(ch)

        return ch

    def _remove_non_changed(self, ch: dict):
        for key, value in list(ch.items()):
            if key not in self.changed_attributes:
                ch.pop(key)
        return ch

    @staticmethod
    def _remove_non_editable(ch: dict):
        if 'uid' in ch:
            ch.pop('uid')
        return ch


@dataclass
class CardholderType:
    uid: str = ""
    typeName: str = ""
    defaultBPTemplate: str = ""

    def __init__(self, cardholder_type_dict: dict):
        for property_name in cardholder_type_dict:
            if isinstance(cardholder_type_dict[property_name], (str, type(None), bool, int)):
                setattr(self, property_name, cardholder_type_dict[property_name])

    def dict(self):
        return {k: str(v) for k, v in asdict(self).items()}


@dataclass
class Cardholder(Observable):
    """
    Represents a cardholder with various attributes and methods to manage and
    observe changes in the cardholder's data.

    Attributes
    ----------
    uid : str
        Unique identifier for the cardholder.
    lastName : str
        Last name of the cardholder.
    firstName : str
        First name of the cardholder.
    cardholderIdNumber : any
        Identification number of the cardholder.
    status : any
        Status of the cardholder.
    fromDateValid : any
        Start date of the cardholder's validity.
    isFromDateActive : any
        Indicates if the start date is active.
    toDateValid : any
        End date of the cardholder's validity.
    isToDateActive : any
        Indicates if the end date is active.
    photo : any
        Photo of the cardholder.
    cardholderType : CardholderType
        Type of the cardholder.
    securityGroup : SecurityGroup
        Security group associated with the cardholder.
    cardholderPersonalDetail : CardholderPersonalDetail
        Personal details of the cardholder.
    cardholderCustomizedField : CardholderCustomizedField
        Customized fields for the cardholder.
    insideArea : Area
        Area where the cardholder is currently located.
    ownerSiteUID : str
        Unique identifier for the owner site.
    securityGroupApiKey : any
        API key for the security group.
    ownerSiteApiKey : any
        API key for the owner site.
    accessGroupApiKeys : any
        API keys for access groups.
    liftAccessGroupApiKeys : any
        API keys for lift access groups.
    cardholderTypeUID : str
        Unique identifier for the cardholder type.
    departmentUID : any
        Unique identifier for the department.
    description : str
        Description of the cardholder.
    grantAccessForSupervisor : any
        Indicates if access is granted for the supervisor.
    isSupervisor : any
        Indicates if the cardholder is a supervisor.
    needEscort : any
        Indicates if the cardholder needs an escort.
    personalWeeklyProgramUID : any
        Unique identifier for the personal weekly program.
    pinCode : str
        PIN code of the cardholder.
    sharedStatus : str
        Shared status of the cardholder.
    securityGroupUID : str
        Unique identifier for the security group.
    accessGroupUIDs : any
        Unique identifiers for access groups.
    liftAccessGroupUIDs : any
        Unique identifiers for lift access groups.
    lastDownloadTime : any
        Last download time of the cardholder's data.
    lastInOutArea : str
        Last in/out area of the cardholder.
    lastInOutReaderUID : any
        Unique identifier for the last in/out reader.
    lastInOutDate : any
        Last in/out date of the cardholder.
    lastAreaReaderDate : any
        Last area reader date of the cardholder.
    lastAreaReaderUID : any
        Unique identifier for the last area reader.
    lastPassDate : any
        Last pass date of the cardholder.
    lastReaderPassUID : any
        Unique identifier for the last reader pass.
    insideAreaUID : str
        Unique identifier for the inside area.
    cards : list
        List of cards associated with the cardholder.

    Methods
    -------
    __init__(*args, kwargs)
        Initializes a new instance of the Cardholder class.
    to_search_pattern()
        Generates a search pattern string based on the cardholder's details.
    pretty_print(obj: object = None)
        Prints the cardholder's attributes in a readable format.
    dict(editable_only=False, changed_only=False, non_empty_only=False)
        Returns a dictionary representation of the cardholder's attributes.
    _remove_non_changed(ch: dict)
        Removes attributes that have not changed from the dictionary.
    _remove_non_editable(ch: dict)
        Removes non-editable attributes from the dictionary.
    """
    uid: str = ""
    lastName: str = ""
    firstName: str = ""
    cardholderIdNumber: any = None
    status: any = None
    fromDateValid: any = None
    isFromDateActive: any = None
    toDateValid: any = None
    isToDateActive: any = None
    photo: any = None
    cardholderType: CardholderType = None
    securityGroup: SecurityGroup = None
    cardholderPersonalDetail: CardholderPersonalDetail = None
    cardholderCustomizedField: CardholderCustomizedField = None
    insideArea: Area = None
    ownerSiteUID: str = ""
    securityGroupApiKey: any = None
    ownerSiteApiKey: any = None
    accessGroupApiKeys: any = None
    liftAccessGroupApiKeys: any = None
    cardholderTypeUID: str = ""
    departmentUID: any = None
    description: str = ""
    grantAccessForSupervisor: any = None
    isSupervisor: any = None
    needEscort: any = None
    personalWeeklyProgramUID: any = None
    pinCode: str = ""
    sharedStatus: str = ""
    securityGroupUID: str = ""
    accessGroupUIDs: any = None
    liftAccessGroupUIDs: any = None
    lastDownloadTime: any = None
    lastInOutArea: str = ""
    lastInOutReaderUID: any = None
    lastInOutDate: any = None
    lastAreaReaderDate: any = None
    lastAreaReaderUID: any = None
    lastPassDate: any = None
    lastReaderPassUID: any = None
    insideAreaUID: str = ""
    cards: list = None

    def __init__(self, *args, **kwargs):
        super().__init__()
        cardholder_dict = sanitise_args(self, args, kwargs)

        for property_name in cardholder_dict:
            if isinstance(cardholder_dict[property_name], list):
                if property_name == "accessGroupUIDs":
                    setattr(self, property_name, ";".join(cardholder_dict[property_name]))
                elif property_name == "cards":
                    setattr(self, property_name, [])
                    for card_entry in cardholder_dict[property_name]:
                        if isinstance(card_entry, Card):
                            self.cards.append(card_entry)
                        else:
                            self.cards.append(Card(card_entry))
                else:
                    setattr(self, property_name, cardholder_dict[property_name])

            if property_name == "cardholderPersonalDetail":
                if isinstance(cardholder_dict[property_name], CardholderPersonalDetail):
                    self.cardholderPersonalDetail = cardholder_dict[property_name]

            if property_name == "cardholderCustomizedField":
                if isinstance(cardholder_dict[property_name], CardholderCustomizedField):
                    self.cardholderCustomizedField = cardholder_dict[property_name]

            if isinstance(cardholder_dict[property_name], dict):
                if property_name == "insideArea":
                    self.insideArea = Area(cardholder_dict[property_name])
                if property_name == "securityGroup":
                    self.securityGroup = SecurityGroup(cardholder_dict[property_name])
                if property_name == "cardholderType":
                    self.cardholderType = CardholderType(cardholder_dict[property_name])
                if property_name == "cardholderPersonalDetail":
                    self.cardholderPersonalDetail = CardholderPersonalDetail(cardholder_dict[property_name])
                if property_name == "cardholderCustomizedField":
                    self.cardholderCustomizedField = CardholderCustomizedField(cardholder_dict[property_name])

            if isinstance(cardholder_dict[property_name], (str, type(None), bool, int)):
                setattr(self, property_name, cardholder_dict[property_name])

        # Monitor Changes
        for k, v in asdict(self).items():
            if isinstance(v, (str, type(None), bool, int)):
                self.add_observer(k)

    def to_search_pattern(self):
        pattern = ""
        if self.firstName:
            pattern += self.firstName + " "
        if self.lastName:
            pattern += self.lastName + " "
        if self.cardholderPersonalDetail:
            if self.cardholderPersonalDetail.company:
                pattern += self.cardholderPersonalDetail.company + " "
            if self.cardholderPersonalDetail.email:
                pattern += self.cardholderPersonalDetail.email
        return pattern

    def pretty_print(self, obj: object = None):
        if obj is None:
            obj = self
        for attribute_name in obj.__dict__:
            if attribute_name != 'observed':
                attribute = getattr(obj, attribute_name)
                if isinstance(attribute, list):
                    print(f"{attribute_name}:")
                    print(f"\t{str(attribute)}")
                elif hasattr(attribute, '__dict__'):
                    print(f"{attribute_name}:")
                    obj.pretty_print(attribute)
                else:
                    print(f"\t{attribute_name:<25}" + str(attribute))

    def dict(self, editable_only=False, changed_only=False, non_empty_only=False):
        ch = dict()

        for k, v in asdict(self).items():
            if isinstance(v, (list, dict, bool, int)):

                ch[k] = v
            elif isinstance(v, type(None)):
                if not non_empty_only:
                    ch[k] = None
            elif isinstance(v, str):
                if non_empty_only:
                    if len(v) > 0:
                        ch[k] = str(v)
                else:
                    ch[k] = str(v)
            else:
                pass

        if changed_only:
            ch = self._remove_non_changed(ch)

        if editable_only:
            ch = self._remove_non_editable(ch)

        return ch

    def _remove_non_changed(self, ch: dict):
        for key, value in list(ch.items()):
            if key not in self.changed_attributes:
                ch.pop(key)
        return ch

    @staticmethod
    def _remove_non_editable(ch: dict):
        if 'uid' in ch:
            ch.pop('uid')
        if 'ownerSiteUID' in ch:
            ch.pop('ownerSiteUID')
        if 'lastDownloadTime' in ch:
            ch.pop('lastDownloadTime')
        if 'lastInOutArea' in ch:
            ch.pop('lastInOutArea')
        if 'lastInOutReaderUID' in ch:
            ch.pop('lastInOutReaderUID')
        if 'lastInOutDate' in ch:
            ch.pop('lastInOutDate')
        if 'lastAreaReaderDate' in ch:
            ch.pop('lastAreaReaderDate')
        if 'lastAreaReaderUID' in ch:
            ch.pop('lastAreaReaderUID')
        if 'lastPassDate' in ch:
            ch.pop('lastPassDate')
        if 'lastReaderPassUID' in ch:
            ch.pop('lastReaderPassUID')
        if 'status' in ch:
            ch.pop('status')
        if 'insideArea' in ch:
            ch.pop('insideArea')
        if 'cardholderPersonalDetail' in ch:
            ch.pop('cardholderPersonalDetail')
        if 'cardholderCustomizedField' in ch:
            ch.pop('cardholderCustomizedField')
        if 'cardholderType' in ch:
            ch.pop('cardholderType')
        if 'securityGroup' in ch:
            ch.pop('securityGroup')
        if 'cards' in ch:
            ch.pop('cards')
        #if 'accessGroupUIDs' in ch:
        #ch.pop('accessGroupUIDs')
        if 'liftAccessGroupUIDs' in ch:
            ch.pop('liftAccessGroupUIDs')

        return ch

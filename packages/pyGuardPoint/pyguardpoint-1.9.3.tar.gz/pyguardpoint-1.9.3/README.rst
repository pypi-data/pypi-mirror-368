pyGuardPoint
===============

pyGuardPoint is a Python wrapper for the GuardPoint 10 API, which allows developers to easily integrate with the GuardPoint 10 physical access control system (ACS).

pyGuardPoint aims to provide a pythonic OOP style programming interface to the WebAPI of GuardPoint 10 (GP10), perfect for quickly building proof-of-concepts.
GuardPoint 10 controls and monitors doors,lifts,readers etc. pyGuardPoint currently focuses more on the management of Cardholders over the monitoring and setup of the physical infrastructure.

At the time of writing the current version of GuardPoint 10 is Version 1.90.3.
Learn more about the GuardPoint 10 ACS here https://www.sensoraccess.co.uk/guardpoint10/

pyGuardPoint is not compatible with the legacy ACS GuardPoint Pro.

What is it good for?
------------------
Rapid development of applications and scripts using the GuardPoint ACS.
pyGuardPoint manages your authenticated connection to GuardPoint 10, so there is know need to construct complex OData URLs.
The Python object Cardholder represents a user/person on the system.
Modify your Cardholder's attributes and update them with just a couple of lines of code.

Examples
------------------
Firstly you will always need to import the module:

    from pyGuardPoint import GuardPoint, Cardholder, Card

It is recommended to use a mutually authenticated secure connection to the GuardPoint server in production environments.

To establish a secure connection with a PKCS#12(*.p12) credential file:

    gp = GuardPoint(host="https://sensoraccess.duckdns.org", pwd="admin",
                        p12_file="MobileGuardDefault.p12",
                        p12_pwd="test")

pyGuardPoint also has built-in support for asynchronous connections, under-the-hood it uses the Python module aiohttp.
The example below demonstrates settings up a AsyncIO connection:

    from pyGuardPoint import GuardPointAsyncIO
    gp = GuardPointAsyncIO(host="https://sensoraccess.duckdns.org", pwd="admin",
                        p12_file="MobileGuardDefault.p12",
                        p12_pwd="test")

To retrieve a list of cardholders:

    gp = GuardPoint(host="10.0.0.1", pwd="password")
    cardholders = gp.get_card_holders(search_terms="Jeff Buckley")
    for cardholder in cardholders:
        print(cardholder.lastName)

To create a new cardholder:

    gp = GuardPoint(host="10.0.0.1", pwd="password")
    cardholder_pd = CardholderPersonalDetail(email="jeff.buckley@test.com")
    cardholder = Cardholder(firstName="Jeff", lastName="Buckley",
                            cardholderPersonalDetail=cardholder_pd)
    cardholder = gp.new_card_holder(cardholder)

To create a card for the cardholder - A card can represent an assortment of Identity tokens(magnetic-card, smartcard, QRCode , vehicle number plate etc) - as long as it contains a unique card-code:

    from pyGuardPoint import GuardPoint, Card

    gp = GuardPoint(host="sensoraccess.duckdns.org", pwd="password")

    cardholders = gp.get_card_holders(firstName="Jeff", lastName="Buckley")
    if len(cardholders) < 1:
        exit()

    card = Card(cardType="Magnetic", cardCode="1A1B1123")
    cardholders[0].cards.append(card)
    if gp.update_card_holder(cardholders[0]):
        updated_cardholder = gp.get_card_holder(uid=cardholders[0].uid)
        print(f"Cardholder {updated_cardholder.firstName} {updated_cardholder.lastName} Updated")
        print(f"\tEmail: {updated_cardholder.cardholderPersonalDetail.email}")
        print(f"\tCards: {updated_cardholder.cards}")

The get_card_holders method can be used with a whole host of flags for filtering:

    cardholders = gp.get_card_holders(search_terms="Frank Smith Countermac",
                                          cardholder_type_name='Visitor',
                                          filter_expired=True,
                                          select_ignore_list=['cardholderCustomizedField',
                                                              'cardholderPersonalDetail',
                                                              'securityGroup',
                                                              'cards',
                                                              'photo'],
                                          select_include_list=['uid', 'lastName', 'firstName', 'lastPassDate',
                                                               'insideArea', 'fromDateTime'],
                                          sort_algorithm=SortAlgorithm.FUZZY_MATCH,
                                          threshold=10)

The class Cardholder has a couple of convenience functions:

    cardholder.dict(non_empty_only=True)) # Convert to python dictionary
    cardholder.pretty_print()   # Print nicely in the terminal window

To get a list of areas/zones, and count the number of cardholders in each:

    gp = GuardPoint(host="sensoraccess.duckdns.org", pwd="password")

    areas = gp.get_areas()
    for area in areas:
        cardholder_count = gp.get_card_holders(count=True, areas=area)
        print(f"Cardholders in {area.name} = {str(cardholder_count)}")

To get a list of security groups:

    sec_groups = gp.get_security_groups()
    for sec_group in sec_groups:
        print(sec_group)

Scheduling the membership of an Access Group to a Cardholder:

    # Get a cardholder
    cardholder = gp.get_card_holder(card_code='1B1A1B1C')

    # Add and associate schedule access group to cardholder
    fromDateValid = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
    toDateValid = (datetime.now() + timedelta(hours=1)).strftime('%Y-%m-%dT%H:%M:%SZ')
    sm = ScheduledMag(scheduledSecurityGroupUID=sec_groups[0].uid,
                      cardholderUID=cardholder.uid,
                      fromDateValid=fromDateValid,
                      toDateValid=toDateValid)
    gp.add_scheduled_mag(sm)

    scheduled_mags = gp.get_scheduled_mags()
    for scheduled_mag in scheduled_mags:
        print(scheduled_mag)

Complete example script using GuardPointAsyncIO to get Access followed by Alarm Events:

    from pyGuardPoint_Build.pyGuardPoint import GuardPointAsyncIO, GuardPointError, GuardPointUnauthorized

    # GuardPoint
    GP_HOST = 'https://sensoraccess.duckdns.org'
    # GP_HOST = 'http://localhost/'
    GP_USER = 'admin'
    GP_PASS = 'admin'
    # TLS/SSL secure connection
    TLS_P12 = "/Users/johnowen/Downloads/MobileGuardDefault.p12"
    #TLS_P12 = "C:\\Users\\john_\\OneDrive\\Desktop\\MobGuardDefault\\MobileGuardDefault.p12"
    TLS_P12_PWD = "test"

    if __name__ == "__main__":
        py_gp_version = version("pyGuardPoint")
        print("pyGuardPoint Version:" + py_gp_version)
        py_gp_version_int = int(py_gp_version.replace('.', ''))
        if py_gp_version_int < 138:
            print("Please Update pyGuardPoint")
            print("\t (Within a Terminal Window) Run > 'pip install pyGuardPoint --upgrade'")
            exit()

        logging.basicConfig(level=logging.DEBUG)

        async def main():
            gp = GuardPointAsyncIO(host=GP_HOST,
                                   username=GP_USER,
                                   pwd=GP_PASS,
                                   p12_file=TLS_P12,
                                   p12_pwd=TLS_P12_PWD)

            print(f"\n********* Get Access Events **********")
            access_events = await gp.get_access_events(limit=3, offset=0)

            for access_event in access_events:
                print(f"\nAccessEvent:")
                print(f"\tType: {access_event.type}")
                print(f"\tjournalUpdateDateTime: {access_event.journalUpdateDateTime}")
                print(f"\tdateTime: {access_event.dateTime}")
                print(f"\taccessDeniedCode: {access_event.accessDeniedCode}")
                print(f"\tisPastEvent: {access_event.isPastEvent}")

            print(f"\n\n********* Get Alarm Events **********")
            alarm_events = await gp.get_alarm_events(limit=3, offset=0)

            for alarm_event in alarm_events:
                print(f"\nAlarmEvent:")
                print(f"\tType: {alarm_event.type}")
                print(f"\tjournalUpdateDateTime: {alarm_event.journalUpdateDateTime}")
                print(f"\tdateTime: {alarm_event.dateTime}")

            await gp.close()

        try:
            asyncio.run(main())
        except GuardPointError as e:
            print(f"GuardPointError: {e}")
        except GuardPointUnauthorized as e:
            print(f"GuardPointUnauthorized: {e}")
        except Exception as e:
            print(f"Exception: {e}")



GuardPoint servers can be setup with a Signal-R service enabled.
Once enabled the server will broadcast events to clients listening to events.

    try:
        gp = GuardPoint(host=GP_HOST,
                        username=GP_USER,
                        pwd=GP_PASS,
                        p12_file=TLS_P12,
                        p12_pwd=TLS_P12_PWD)

        signal_client = gp.get_signal_client()

        signal_client.on_open(on_open)
        signal_client.on_close(on_close)
        signal_client.on_error(on_error)
        signal_client.on('AccessEventArrived', on_message)
        signal_client.on("AlarmEventArrived", on_message)
        signal_client.on("AuditEventArrived", on_message)
        signal_client.on("CommEventArrived", on_message)
        signal_client.on("GeneralEventArrived", on_message)
        signal_client.on("IOEventArrived", on_message)
        signal_client.on("StatusUpdate", on_message)
        signal_client.on("TechnicalEventArrived", on_message)

        async def run_signal_client() -> None:
            task = asyncio.create_task(signal_client.run(), name = "sigR_task")
            await task


        loop = asyncio.get_event_loop()
        asyncio.run_coroutine_threadsafe(run_signal_client(), loop)

        gp.start_listening(signal_client)

    except GuardPointError as e:
        print(f"GuardPointError: {e}")
    except AuthorizationError as e:
        print(f"SignalR AuthorizationError")
    except Exception as e:
        print(f"Exception: {str(e)}")

More
------------------
Complete API documentation can be found at ReadTheDocs here https://pyguardpoint.readthedocs.io/en/latest/
The code and further examples can be found at https://github.com/SensorAccess/pyGuardPoint
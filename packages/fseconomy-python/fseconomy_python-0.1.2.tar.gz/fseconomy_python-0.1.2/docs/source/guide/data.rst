.. _datadoc:

Data Feeds
==========

To access the different data feeds provided by `fseconomy`, you can use the
`fseconomy.data` module.

.. note::
    Since most data feeds require authentication, you
    will need to set a valid user key, group key, or service key using the
    functions :py:func:`fseconomy.set_user_key`, :py:func:`fseconomy.set_access_key`, and
    :py:func:`fseconomy.set_service_key` prior to accessing the data feeds.


General Information
-------------------

Data feeds can be accessed using the `fseconomy.data` module. The public functions all return
a :py:class:`fseconomy.response.Response` object, which contains the raw data as well as a parsed
representation of the data (if possible).

Aircraft Data Feeds
-------------------

* :py:func:`fseconomy.data.aircraft_status_by_registration` - Aircraft Status by Registration
* :py:func:`fseconomy.data.aircraft_configs` - Aircraft Configs
* :py:func:`fseconomy.data.aircraft_aliases` - Aircraft Aliases
* :py:func:`fseconomy.data.aircraft_for_sale` - Aircraft For Sale
* :py:func:`fseconomy.data.aircraft_by_makemodel` - Aircraft by Make/Model
* :py:func:`fseconomy.data.aircraft_by_ownername` - Aircraft by Owner Name
* :py:func:`fseconomy.data.aircraft_by_registration` - Aircraft by Registration
* :py:func:`fseconomy.data.aircraft_by_id` - Aircraft by ID
* :py:func:`fseconomy.data.aircraft_by_key` - Aircraft by Key

Assignment Data Feeds
---------------------

* :py:func:`fseconomy.data.assignments_by_key` - Assignments by Key

Commodity Data Feeds
--------------------

* :py:func:`fseconomy.data.commodities_by_key` - Commodities by Key

FBO Data Feeds
--------------

* :py:func:`fseconomy.data.facilities_by_key` - Facilities by Key
* :py:func:`fseconomy.data.fbos_by_key` - FBOs by Key
* :py:func:`fseconomy.data.fbos_for_sale` - FBOs For Sale
* :py:func:`fseconomy.data.fbo_monthly_summary_by_icao` - FBO Monthly Summary by ICAO

Flight Log Data Feeds
---------------------

* :py:func:`fseconomy.data.flight_logs_by_key_month_year` - Flight Logs by Key, Month, Year
* :py:func:`fseconomy.data.flight_logs_by_reg_month_year` - Flight Logs by Registration, Month, Year
* :py:func:`fseconomy.data.flight_logs_by_serialnumber_month_year` - Flight Logs by Serial Number, Month, Year
* :py:func:`fseconomy.data.flight_logs_by_key_from_id` - Flight Logs by Key, from ID (500 max)
* :py:func:`fseconomy.data.flight_logs_by_key_from_id_for_all_group_aircraft` - Flight Logs by Key, from ID (500 max) for ALL group aircraft
* :py:func:`fseconomy.data.flight_logs_by_reg_from_id` - Flight Logs by Registration, from ID (500 max)
* :py:func:`fseconomy.data.flight_logs_by_serialnumber_from_id` - Flight Logs by Serial Number, from ID (500 max)

Group Data Feeds
----------------

* :py:func:`fseconomy.data.group_members` - Group Members

Airport Data Feeds
------------------

* :py:func:`fseconomy.data.fse_icao_data` - Airports available in FSEconomy
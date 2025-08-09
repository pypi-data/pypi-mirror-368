.. _core:

Core
====

.. module:: fseconomy.core

.. warning::
   The functionality provided by the :mod:`fseconomy.core` module
   is reserved for internal purposes. It does not constitute an API
   intended for public use. This documentation is solely provided
   for the sake of completeness, and to support developers contributing
   to the :mod:`fseconomy` package.

API
---

.. module:: fseconomy.core.api

.. autodata:: API_VERSIONS
.. autodata:: MAINTENANCE
.. autodata:: DATA_FEEDS

Fetch Data Feed
---------------

.. module:: fseconomy.core.fetch

.. autofunction:: fetch

Keys
----

.. module:: fseconomy.core.keys

.. autodata:: ACCESS_KEY
.. autodata:: SERVICE_KEY
.. autodata:: USER_KEY

.. autofunction:: validate_key

.. autofunction:: get_data_keys

Data Decoders
-------------

.. module:: fseconomy.core.data

Collection of data decoding functions to convert the raw XML data received
from the FSEconomy server into standard Python data types

Aircraft Status
~~~~~~~~~~~~~~~

.. autofunction:: fseconomy.core.data.status.decode
.. autofunction:: fseconomy.core.data.status.__decode_status

Aircraft Configuration
~~~~~~~~~~~~~~~~~~~~~~

.. autofunction:: fseconomy.core.data.config.decode
.. autofunction:: fseconomy.core.data.config.__decode_config

Aircraft Aliases
~~~~~~~~~~~~~~~~

.. autofunction:: fseconomy.core.data.aliases.decode
.. autofunction:: fseconomy.core.data.aliases.__decode_aliases

Aircraft
~~~~~~~~

.. autofunction:: fseconomy.core.data.aircraft.decode
.. autofunction:: fseconomy.core.data.aircraft.__decode_aircraft

Assignments
~~~~~~~~~~~

.. autofunction:: fseconomy.core.data.assignment.decode
.. autofunction:: fseconomy.core.data.assignment.__decode_assignment

Commodities
~~~~~~~~~~~

.. autofunction:: fseconomy.core.data.commodity.decode
.. autofunction:: fseconomy.core.data.commodity.__decode_commodity

Facilities
~~~~~~~~~~

.. autofunction:: fseconomy.core.data.facility.decode
.. autofunction:: fseconomy.core.data.facility.__decode_facility

FBOs
~~~~

.. autofunction:: fseconomy.core.data.fbo.decode
.. autofunction:: fseconomy.core.data.fbo.__decode_fbo

FBO Summary
~~~~~~~~~~~

.. autofunction:: fseconomy.core.data.summary.decode
.. autofunction:: fseconomy.core.data.summary.__decode_summary

Flights
~~~~~~~

.. autofunction:: fseconomy.core.data.flight.decode
.. autofunction:: fseconomy.core.data.flight.__decode_flight

Group Members
~~~~~~~~~~~~~

.. autofunction:: fseconomy.core.data.member.decode
.. autofunction:: fseconomy.core.data.member.__decode_member

Airports
~~~~~~~~

.. autofunction:: fseconomy.core.data.airport.decode
.. autofunction:: fseconomy.core.data.airport.__decode_airport

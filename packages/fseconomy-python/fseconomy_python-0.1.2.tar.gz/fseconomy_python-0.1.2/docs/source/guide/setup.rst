.. _setupdoc:

Setup
=====

In order to use `fseconomy` you either need to have a valid FSEconomy User key
(plus a group key if accessing group resources), or a valid FSEconomy service key.
Please consult the `FSEconomy Operations Guide <https://sites.google.com/site/fseoperationsguide/data-feeds>`__
for further information.

If you have a FSEconomy User key, you can set it using the :py:func:`~fseconomy.set_user_key` function:

.. code-block:: python

    import fseconomy
    fseconomy.set_user_key('YOUR-USER-KEY')

If you want to use a group key, you can set it using the :py:func:`~fseconomy.set_access_key` function:

.. code-block:: python

    import fseconomy
    fseconomy.set_access_key('YOUR-ACCESS-KEY')



If you have a FSEconomy service key, you can set it using the :py:func:`~fseconomy.set_service_key` function:

.. code-block:: python

    import fseconomy
    fseconomy.set_service_key('YOUR-SERVICE-KEY')

.. note::
    * If available, the service key is preferred over the (personal) user key.
    * If no access key has been defined, the user key is used as default.
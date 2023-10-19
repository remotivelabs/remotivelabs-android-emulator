Setup
===========================================================================================


**Make sure you have installed all dependencies with:**

.. code-block:: console

    $ pip install -r requirements.txt

Emulator
---------------------------------------------------------------------------------------------

Remotive Labs Broker
---------------------------------------------------------------------------------------------
#. Go to `Remotive Labs Broker Demo <https://demo.remotivelabs.com/orgs/remotidemo>`_.
#. Select Start Demo.
#. Choose a Recording Session.
#. Select **configuration_android** in Broker configuration.
#. Click on Play and go to the broker.
#. Add the desired signal visualisations:
    * LONGITUDE and LATITUDE for sending location fixes to the emulator.
    * Other relevant signals for VHAL properties and/or sensors.
#. Copy the url, API key, namespace, and signals from "Examples to subscribe to signals from an external application".
#. Use those as arguments to the scripts.

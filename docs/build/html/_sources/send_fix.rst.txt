Send Location to AAOS Emulator
===========================================================================================

In order to use the script *br_location_to_emu.py*, make sure you completed the steps from the setup page.

Then, check the instructions below:

Send Location on Maps
---------------------------------------------------------------------------------------------
1. Make sure you have a recording running on Remotive Labs Broker.
2. Run the emulator.
3. Enable location on the emulator.
4. Run on terminal:

.. code-block:: console

    $ python3 br_location_to_emu.py --url $URL --x_api_key $KEY --signal LATITUDE --signal LONGITUDE

5. Open up an AAOS emulator.

.. note::

   For this you do not need to use an userdebug build. For VHAL properties, however, that is mandatory as of now.

Check the location changing
---------------------------------------------------------------------------------------------
There are two simple ways to check the AAOS emulator changing its position according to a broker's data.

First is collecting logs from the device.

The second, and fun way, is by opening Google Maps (if available) and comparing to the map showed on Remotive Labs demo platform.
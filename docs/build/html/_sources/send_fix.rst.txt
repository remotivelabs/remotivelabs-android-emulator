Send Location to AAOS Emulator
===========================================================================================

In order to use the script to send geo location data to the emulator, make sure you completed the steps from the setup page.

Then, check the instructions below:

Send Location on Maps
---------------------------------------------------------------------------------------------
1. Make sure you have a recording running on Remotive Labs Broker.
2. Run the emulator.
3. Enable location on the emulator.
4. Run on terminal:

.. code-block:: console

    $ python3 -m android_bridge \
      --url $URL \
      --api-key $KEY \
      --with-location

.. note::
   You can use different names for the longitude and latitude signals by supplying the arguments `--longitude-signal-name` and `--latitude-signal-name`.  

5. Open up an AAOS emulator.

.. note::
   For this you do not need to use an userdebug build. For VHAL properties, however, that is mandatory as of now.  
.. note::
   The geo location data is send to the emulator using the `emu geo fix` command which is specific to android emulators and would not work for other ADB devices.

Check the location changing
---------------------------------------------------------------------------------------------
There are two simple ways to check the AAOS emulator changing its position according to a broker's data.

First is collecting logs from the device.

The second, and fun way, is by opening Google Maps (if available) and comparing to the map showed on Remotive Labs demo platform.

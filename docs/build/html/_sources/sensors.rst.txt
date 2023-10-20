Send Sensors Data to AAOS Emulator
===========================================================================================
.. _sensors:

You can send sensors data to AAOS using the following command:

.. code-block:: console

    $ adb emu sensors #sensor_name #data

This can be done through {$PROJECT_ROOT}/libs/adb/device.py:

.. code-block:: python

    def send_sensor_data(self, sensor_name, data):
        # Sensor data is in string with format data0:data1:data2
        return self._simple_call(['emu', 'sensor', sensor_name, data])


You can list the available sensors using:

.. code-block:: console

    $ adb emu sensors status

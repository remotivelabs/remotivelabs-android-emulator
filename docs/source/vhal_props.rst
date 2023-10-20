Modify VHAL Properties (Under development)
===========================================================================================

In order to set properties in AAOS, the project currently uses the library provided by AOSP. It can be found in
`android/platform/packages/services/Car/tools/emulator/
<https://android.googlesource.com/platform/packages/services/Car/+/master/tools/emulator/vhal_emulator.py>`_

That code has not been update in the latest Android versions. It creates a socket connection directly to a hard coded
port in the Car emulator:

.. code-block:: python

    def openSocket(self, device=None):
        """
            Connects to an Android Auto device running a Vehicle HAL with simulator.
        """
        # Hard-coded socket port needs to match the one in DefaultVehicleHal
        remotePortNumber = 33452
        extraArgs = '' if device is None else '-s %s' % device
        adbCmd = 'adb %s forward tcp:0 tcp:%d' % (extraArgs, remotePortNumber)

Execute the script
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. warning::
    Userdebug build and permissive mode are mandatory for this.

In order to get it working the build **MUST BE** userdebug. Also, you need to run the emulator in permissive
mode. If those two requirements are not satisfied, SELinux will not allow AAOS emulator to open its own socket and listen
to any connections from your host machine.

You can check the build type (userdebug, user, eng) with:

.. code-block:: console

    $ adb shell getprop | grep build

The simplest way to execute the emulator in permissive mode is through the terminal:

.. code-block:: console

    $ emulator @$avd_name -selinux permissive -no-snapshot

Refer to https://developer.android.com/studio/run/emulator-commandline if this is your first time executing this way.
Here we are assuming that emulator is on your $PATH.

The flag *-no-snapshot* triggers a cold boot to make sure that the socket communication was opened.

You can see the AVDs by using:

.. code-block:: console

    $ emulator -list-avds

Once you start the emulator, you can check if the socket was open from AAOS side with:

.. code-block:: console

    $ adb logcat | grep SocketComm

Example:

.. code-block:: console

    10-20 10:05:11.656 31226 31226 I VehicleEmulator_v2_0: Starting SocketComm
    10-20 10:05:11.656 31226 31226 I SocketComm: listen: Listening for connections on port 33452
    10-20 10:05:14.356 31226 31233 D SocketComm: accept: Incoming connection received from 127.0.0.1:63905

Then, run the script with parameters from Remotive Labs broker:

.. code-block:: console

    $ python3 br_props_to_aaos.py --url $URL --x_api_key $KEY --signal $SIGNAL


Issues with protobuf
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Depending on the protobuf you are using you can face issues when executing the script.

These are options you can try to solve it:

* Use **PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=python** before calling the script:

.. code-block:: console

    $ PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=python python3 br_props_to_aaos.py --url $URL --x_api_key $KEY --signal $SIGNAL


* Generate the protobuf file from hardware/interfaces/automotive/vehicle/2.0/default/impl/vhal_v2_0
    * It is recommended to use the protoc provided in: prebuilts/tools/common/m2/repository/com/google/protobuf/protoc/3.0.0 or a later version, in order to provide Python 3 compatibility

.. code-block:: console

    $ protoc -I=proto --python_out=proto proto/VehicleHalProto.proto


* For the script
    * protobuf with old version
    * Script uses localhost address to create socket connection. On WSL, there are some issues with that. - Put link to it.

Testing Vhal_emulator
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
* You can run *hal_emulator_test.py*.
* Install KitchenSink.
    #. You can build the application from */platform/packages/services/Car//tests/EmbeddedKitchenSinkApp*.
    #. From https://android.googlesource.com/platform/packages/services/Car/+/main/tests/EmbeddedKitchenSinkApp:

.. code-block:: console

    $ m -j EmbeddedKitchenSinkApp
    $ adb root
    $ adb install -r -d $ANDROID_PRODUCT_OUT/system/priv-app/EmbeddedKitchenSinkApp/EmbeddedKitchenSinkApp.apk

* In the future it would be nice to test the script with an userdebug with GAS. Unfortunately, those are not provided publicly.

Insights
===========================================================================================

This page covers lessons learned during the development, as well as proposes future implementations
to the project.

Consider using QEMU
------------------------------------------------------------------------------------------

The easiest and quickest way to manipulate VHAL properties on Android emulator is by using the
scripts in https://android.googlesource.com/platform/packages/services/Car/+/refs/heads/main/tools/emulator.

However, those scripts have not been supported for a while, so it faces several issues:

* AAOS images MUST be userdebug.
* SELinux MUST be set to permissive.
* Google has provided an userdebug emulator image, but it does not contain Google Automotive Services.

Google implemented on the Car emulator side a socket server that only works with the conditions mentioned above.
If those are not satisfied, SELinux disallows the process to listen to the scripts.

In recent version, Google has implemented QEMU pipes as an alternative for interacting with VHAL:
https://cs.android.com/android/platform/superproject/main/+/main:device/generic/car/emulator/vhal_aidl/VehicleEmulator/VehicleEmulator.cpp

It would be interesting to check if implementing a solution with QEMU is worthwhile.

Android Automotive VHAL Emulator is unreliable
------------------------------------------------------------------------------------------

Even when using the mentioned scripts, the interface on Android OS side is flaky.

For instance, it is possible to monitor VHAL properties by using the KitchenSink app:

/packages/services/Car/tests/EmbeddedKitchenSinkApp/
https://cs.android.com/android/platform/superproject/main/+/main:packages/services/Car/tests/EmbeddedKitchenSinkApp

Still, the app crashes constantly on the emulator, even when it is built locally with the latest code.

Another way for testing is using a Pixel device:
https://github.com/remotivelabs/remotivelabs-android-vhal

.. note::
    In case you want to use a Pixel device, make sure you call adb.get_device() on br_props_to_aaos.py.

That method seemed unreliable as well, as the app also stops responding sometimes, and from AAOS logs
VHAL may die during the tests.

All the mentioned points considered, it is necessary to work on stabilisation and defining of an
interface in the emulator images side. As of now, documentation from Android side is missing, and
there is no established way for testing this scenario.

Virtualization can be of great benefit to the Android Automotive OS development, but it is necessary
to find a common ground between OEMs, Google and Remotive Labs.

In summary, define a proper set of methods to exchange data to AAOS emulator, and validate the properties.

Expand Remotive Labs Broker Android Data
------------------------------------------------------------------------------------------

It is possible to set sensors data. Check :ref:`sensors` out.

In the future, the broker should provide relevant sensor data to be routed to the emulator.

Also, VHAL properties have its own vehicle area
https://cs.android.com/android/platform/superproject/main/+/main:hardware/interfaces/automotive/vehicle/aidl_property/android/hardware/automotive/vehicle/VehicleArea.aidl;l=25?q=vehiclearea&sq=&ss=android%2Fplatform%2Fsuperproject%2Fmain

The scripts in the project are using VehicleArea.GLOBAL, since there are no signals with different areas
for Android yet. In the future, this should be changed accordingly. Refer to https://source.android.com/docs/automotive/vhal/special-properties#hvac
about a more detailed explanation.

Test on Android userdebug builds with GAS
------------------------------------------------------------------------------------------

As mentioned, the only userdebug emulator image available now does not contain GAS.
For a more user-like testing, it would be nice to set VHAL properties by using Google Maps, for example.

OEMs have access to those builds since they apply for Google's AOSP certification.
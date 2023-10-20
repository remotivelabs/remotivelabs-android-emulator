Setup
===========================================================================================

**Make sure you have installed all dependencies with:**

.. code-block:: console

    $ pip install -r requirements.txt

Emulator
---------------------------------------------------------------------------------------------

Use Android Studio Preview Version: https://developer.android.com/studio/preview

.. warning::
    The official version from https://developer.android.com/studio does not provide Automotive emulator images!

Download the images
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
https://developer.android.com/training/cars/testing/emulator

#. In Android Studio, select Tools > SDK Manager.
#. Click the SDK Platforms tab.
#. Click Show Package Details.
#. Select which image(s) to download (see the preceding table for details)
#. Click Apply, then click OK.

It is recommended that you download the following images:

* Android Automotive 13 "Tiramisu" with Google APIs ARM 64 v8a System Image
    * It does not contain GAS, but it is userdebug (for setting VHAL)
* Android Automotive 12L with Play Store ARM 64 v8a System Image
    * If your machine is **ARM** based. It is an user build with GAS.
* Android Automotive 12L with Play Store Intel x86 Atom_64 System Image
    * If your machine is **x86** based. It is an user build with GAS.

Create a car AVD and run the emulator
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
https://developer.android.com/studio/run/managing-avds

#. In Android Studio, select Tools > AVD Manager.
#. Click Create Virtual Device.
#. From the Select Hardware dialog, select Automotive, and then select a device. Click Next.
#. Select a system image that targets Automotive, such as Android 12L (Automotive with Play Store), and click Next.
#. Name your AVD and select any other options that you want to customize, then click Finish.
#. From the tool window bar, select your Android Automotive OS AVD as your deployment target.
#. Click Run icon.

.. warning::
    For setting VHAL properties the emulator must be run in SELinux permissive mode. Go to :doc:`VHAL <vhal_props>`.


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

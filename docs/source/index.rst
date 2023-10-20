.. Remotive Labs Android Emulator documentation master file, created by
   sphinx-quickstart on Wed Oct 18 16:49:22 2023.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Remotive Labs Android Emulator's documentation!
==========================================================

This project aims to implement scripts that work as the bridge between a `Remotive Labs <https://remotivelabs.com/>`_
broker and an `AAOS <https://source.android.com/docs/automotive>`_ emulator.

.. image:: example.gif
   :alt: Example gif
   :align: center

.. note::

   There are some important steps regarding the setup before running the script.
   Please make sure to check the setup page beforehand!

Pages
----------------------------------------------------------
* **Setup**
   * Describes the essential requirements for executing the scripts in this project.
* **Send Location to AAOS Emulator**
   * How to use a script that redirects longitude and latitude from a broker to an emulator.
* **Modify VHAL Properties**
   * Explains how VHAL properties can be modified in AAOS, and how to execute a script for that purpose.
* **Insights**
   * Compilation of lessons learned and potential implementations/improvements on the project.
* **Send Sensors Data to AAOS Emulator**
   * Describe how sensors data can be set and get from emulators.

Table of contents
----------------------------------------------------------

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   setup
   send_fix
   vhal_props
   insights
   sensors

#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2016 The Android Open Source Project
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
"""
This module provides a vhal class which sends and receives messages to the vehicle HAL module
on an Android Auto device.  It uses port forwarding via ADB to communicate with the Android
device.
Example Usage:
    import vhal_consts_2_0 as c
    from vhal_emulator import Vhal
    # Create an instance of vhal class.  Need to pass the vhal_types constants.
    v = Vhal(c.vhal_types_2_0)
    # Get the property config (if desired)
    v.get_config(c.VEHICLEPROPERTY_HVAC_TEMPERATURE_SET)
    # Get the response message to get_config()
    reply = v.rx_msg()
    print(reply)
    # Set left temperature to 70 degrees
    v.set_property(c.VEHICLEPROPERTY_HVAC_TEMPERATURE_SET, c.VEHICLEAREAZONE_ROW_1_LEFT, 70)
    # Get the response message to set_property()
    reply = v.rx_msg()
    print(reply)
    # Get the left temperature value
    v.get_property(c.VEHICLEPROPERTY_HVAC_TEMPERATURE_SET, c.VEHICLEAREAZONE_ROW_1_LEFT)
    # Get the response message to get_property()
    reply = v.rx_msg()
    print(reply)
NOTE:  The rx_msg() is a blocking call, so it may be desirable to set up a separate RX thread
        to handle any asynchronous messages coming from the device.
Example for creating RX thread (assumes vhal has already been instantiated):
    from threading import Thread
    # Define a simple thread that receives messages from a vhal object (v) and prints them
    def rxThread(v):
        while(1):
            print(v.rx_msg())
    rx = Thread(target=rxThread, args=(v,))
    rx.start()
Protocol Buffer:
    This module relies on VehicleHalProto_pb2.py being in sync with the protobuf in the VHAL.
    If the VehicleHalProto.proto file has changed, re-generate the python version using:
        protoc -I=<proto_dir> --python_out=<out_dir> <proto_dir>/VehicleHalProto.proto
"""

from __future__ import print_function

# Suppress .pyc files
import sys
import socket
import struct
import subprocess
from . import vhal_prop_consts_2_0 as vhal_props

from threading import Thread

# Generate the protobuf file from hardware/interfaces/automotive/vehicle/2.0/default/impl/vhal_v2_0
# It is recommended to use the protoc provided in: prebuilts/tools/common/m2/repository/com/google/protobuf/protoc/3.0.0
# or a later version, in order to provide Python 3 compatibility
#   protoc -I=proto --python_out=proto proto/VehicleHalProto.proto
from . import VehicleHalProto_pb2 as VehicleHalProto_pb2

sys.dont_write_bytecode = True


# If container is a dictionary, retrieve the value for key item;
# Otherwise, get the attribute named item out of container
def get_by_attribute_or_key(container, item, default=None):
    if isinstance(container, dict):
        try:
            return container[item]
        except KeyError:
            return default
    try:
        return getattr(container, item)
    except AttributeError:
        return default


def print_hex(data):
    """
    For debugging, print the protobuf message string in hex.
    """
    print(
        "len = ", len(data), "str = ", ":".join("{:02x}".format(ord(d)) for d in data)
    )


class Vhal:
    """
    Dictionary of prop_id to value_type.  Used by set_property() to properly format data.
    """

    _propToType = {}

    # Private Functions
    def _tx_cmd(self, cmd):
        """
        Transmits a protobuf to Android Auto device.  Should not be called externally.
        """
        # Serialize the protobuf into a string
        msgStr = cmd.SerializeToString()
        msgLen = len(msgStr)
        # Convert the message length into int32 byte array
        msgHdr = struct.pack("!I", msgLen)
        # Send the message length first
        self.sock.sendall(msgHdr)
        # Then send the protobuf
        self.sock.sendall(msgStr)

    def open_socket(self, device=None):
        """
        Connects to an Android Auto device running a Vehicle HAL with simulator.
        """
        # Hard-coded socket needs to match the one in DefaultVehicleHal
        portNumber = 33452
        print(
            "Connecting to vhal emulator on port %s on %s"
            % (
                portNumber,
                "default device" if device is None else "device %s" % device,
            )
        )
        # Open the socket and connect
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect(("localhost", portNumber))
        print("Connected to vhal emulator")

    def rx_msg(self):
        """
        Receive a message over the socket.  This function blocks if a message is not available.
          May want to wrap this function inside of an rx thread to also collect asynchronous
          messages generated by the device.
        """
        # Receive the message length (int32) first
        b = self.sock.recv(4)
        if len(b) == 4:
            (msgLen,) = struct.unpack("!I", b)
            if msgLen > 0:
                # Receive the actual message
                b = self.sock.recv(msgLen)
                if len(b) == msgLen:
                    # Unpack the protobuf
                    msg = VehicleHalProto_pb2.EmulatorMessage()
                    msg.ParseFromString(b)
                    # print("Received and unpacked proto message:", msg)
                    return msg
                else:
                    print("Ignored message fragment")

    def get_config(self, prop):
        """
        Sends a get_config message for the specified property.
        """
        cmd = VehicleHalProto_pb2.EmulatorMessage()
        cmd.msg_type = VehicleHalProto_pb2.GET_CONFIG_CMD
        propGet = cmd.prop.add()
        propGet.prop = prop
        self._tx_cmd(cmd)

    def get_config_all(self):
        """
        Sends a get_config_all message to the host.  This will return all configs available.
        """
        cmd = VehicleHalProto_pb2.EmulatorMessage()
        cmd.msg_type = VehicleHalProto_pb2.GET_CONFIG_ALL_CMD
        self._tx_cmd(cmd)

    def get_property(self, prop, area_id):
        """
        Sends a get_property command for the specified property ID and area ID.
        """
        cmd = VehicleHalProto_pb2.EmulatorMessage()
        cmd.msg_type = VehicleHalProto_pb2.GET_PROPERTY_CMD
        propGet = cmd.prop.add()
        propGet.prop = prop
        propGet.area_id = area_id
        self._tx_cmd(cmd)

    def get_property_all(self):
        """
        Sends a get_property_all message to the host.  This will return all properties available.
        """
        cmd = VehicleHalProto_pb2.EmulatorMessage()
        cmd.msg_type = VehicleHalProto_pb2.GET_PROPERTY_ALL_CMD
        self._tx_cmd(cmd)

    def set_property(self, prop, area_id, value, status=VehicleHalProto_pb2.AVAILABLE):
        """
        Sends a set_property command for the specified property ID, area ID, value and status.
          If Status is not specified, automatically send AVAILABLE as the default.
          This function chooses the proper value field to populate based on the config for the
          property.  It is the caller's responsibility to ensure the value data is the proper
          type.
        """
        cmd = VehicleHalProto_pb2.EmulatorMessage()
        cmd.msg_type = VehicleHalProto_pb2.SET_PROPERTY_CMD
        propValue = cmd.value.add()
        propValue.prop = prop
        # Insert value into the proper area
        propValue.area_id = area_id
        propValue.status = status
        # Determine the value_type and populate the correct value field in
        # protoBuf
        try:
            valType = self._propToType[prop]
        except KeyError:
            raise ValueError("propId is invalid:", prop)

        propValue.value_type = valType
        if valType == self._types.TYPE_STRING:
            propValue.string_value = value
        elif valType == self._types.TYPE_BYTES:
            propValue.bytes_value = value
        elif valType == self._types.TYPE_BOOLEAN:
            propValue.int32_values.append(bool(value))
        elif valType == self._types.TYPE_INT32:
            propValue.int32_values.append(value)
        elif valType == self._types.TYPE_INT64:
            propValue.int64_values.append(value)
        elif valType == self._types.TYPE_FLOAT:
            propValue.float_values.append(value)
        elif valType == self._types.TYPE_MIXED:
            propValue.string_value = get_by_attribute_or_key(value, "string_value", "")
            propValue.bytes_value = get_by_attribute_or_key(value, "bytes_value", "")
            for newValue in get_by_attribute_or_key(value, "int32_values", []):
                propValue.int32_values.append(newValue)
            for newValue in get_by_attribute_or_key(value, "int64_values", []):
                propValue.int64_values.append(newValue)
            for newValue in get_by_attribute_or_key(value, "float_values", []):
                propValue.float_values.append(newValue)
        else:
            raise ValueError("value type not recognized:", valType)

        self._tx_cmd(cmd)

    def __init__(self, device=None):
        # Save the list of types constants
        self.sock = None
        self._types = vhal_props.vhal_types
        # Open the socket
        self.open_socket(device)
        # Get the list of configs
        self.get_config_all()
        msg = self.rx_msg()
        if msg is None:
            raise RuntimeError(
                "No config message received from Vehicle HAL emulator, make sure android image comes with vhal and is booted in permissive mode"
            )

        # Parse the list of configs to generate a dictionary of prop_id to type
        for cfg in msg.config:
            self._propToType[cfg.prop] = cfg.value_type

        self.callback = None  # Add a callback attribute

    def set_callback(self, callback):
        """
        Set a callback function to be triggered when a message is received.
        """
        self.callback = callback

    def rxThread(self):
        """
        Thread that receives messages from the VHAL and triggers the callback.
        """
        while True:
            msg = self.rx_msg()  # Blocking call to receive a message
            if msg and self.callback:
                self.callback(msg)  # Trigger the callback with the received message

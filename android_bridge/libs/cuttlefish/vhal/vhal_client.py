import asyncio
from enum import IntEnum
from typing import Union

from google.protobuf import empty_pb2
from grpc.aio import insecure_channel

from .VehicleServer_pb2 import (
    VehiclePropValue,
    VehiclePropValueRequest,
    VehiclePropValueRequests,
)
from .VehicleServer_pb2_grpc import VehicleServerStub


class VhalClient:
    def __init__(
        self,
        cuttlefish_vhal_url: str,
        on_vhal_prop_change=None,
        property_ids_to_subscribe: list[int] = [],
    ):
        print("Connecting to vhal server on %s" % cuttlefish_vhal_url)
        channel = insecure_channel(cuttlefish_vhal_url)
        self.stub = VehicleServerStub(channel)
        print("Connected to vhal server")
        self.on_vhal_prop_change = on_vhal_prop_change
        self.property_ids_to_subscribe = property_ids_to_subscribe
        if self.on_vhal_prop_change is not None:
            try:
                loop = asyncio.get_running_loop()
                loop.create_task(self._consume_vhal_properties())
            except RuntimeError:
                asyncio.run(self._consume_vhal_properties())

    async def _consume_vhal_properties(self):
        stream = self.stub.StartPropertyValuesStream(empty_pb2.Empty())
        async for message in stream:
            for value in message.values:
                if (
                    self.on_vhal_prop_change is not None
                    and value.prop in self.property_ids_to_subscribe
                ):
                    self.on_vhal_prop_change(
                        value.area_id, value.prop, self._get_property_value(value)
                    )

    def set_property(
        self, area_id: int, prop: int, value: Union[int, float, bytes, str]
    ):
        requests = self._create_property_requests(
            area_id=area_id, prop=prop, value=value
        )
        self.stub.SetValues(requests)

    def _get_property_value(
        self, prop_value: VehiclePropValue
    ) -> Union[int, float, bytes, str]:
        """
        Extracts and returns the value from a VehiclePropValue instance based on its property type.

        Raises:
            ValueError: If the property type is MIXED or unknown.
        """
        prop_type = prop_value.prop & PROP_TYPE_MASK
        if prop_type == VehiclePropertyType.BOOLEAN:
            return prop_value.int32_values[0]
        elif prop_type == VehiclePropertyType.INT32:
            return prop_value.int32_values[0]
        elif prop_type == VehiclePropertyType.INT32_VEC:
            return prop_value.int32_values[0]
        elif prop_type == VehiclePropertyType.INT64:
            return prop_value.int64_values[0]
        elif prop_type == VehiclePropertyType.INT64_VEC:
            return prop_value.int64_values[0]
        elif prop_type == VehiclePropertyType.FLOAT:
            return prop_value.float_values[0]
        elif prop_type == VehiclePropertyType.FLOAT_VEC:
            return prop_value.float_values[0]
        elif prop_type == VehiclePropertyType.BYTES:
            return prop_value.byte_values
        elif prop_type == VehiclePropertyType.STRING:
            return prop_value.string_value
        elif prop_type == VehiclePropertyType.MIXED:
            raise ValueError("Property type MIXED is not supported")
        else:
            raise ValueError("Unknown property type")

    def _create_property_requests(
        self, area_id: int, prop: int, value: Union[int, float, bytes, str]
    ) -> VehiclePropValueRequests:
        """
        Creates a VehiclePropValueRequests object for the given property and signal value.

        Raises:
            ValueError: If the property type is MIXED or unknown.
        """
        prop_type = prop & PROP_TYPE_MASK
        int32_values = None
        int64_values = None
        float_values = None
        byte_values = None
        string_value = None

        if prop_type == VehiclePropertyType.BOOLEAN:
            int32_values = [bool(value)]
        elif prop_type == VehiclePropertyType.INT32:
            int32_values = [int(value)]
        elif prop_type == VehiclePropertyType.INT32_VEC:
            int32_values = [int(value)]
        elif prop_type == VehiclePropertyType.INT64:
            int64_values = [int(value)]
        elif prop_type == VehiclePropertyType.INT64_VEC:
            int64_values = [int(value)]
        elif prop_type == VehiclePropertyType.FLOAT:
            float_values = [float(value)]
        elif prop_type == VehiclePropertyType.FLOAT_VEC:
            float_values = [float(value)]
        elif prop_type == VehiclePropertyType.BYTES and isinstance(value, bytes):
            byte_values = bytes(value)
        elif prop_type == VehiclePropertyType.STRING:
            string_value = str(value)
        elif prop_type == VehiclePropertyType.MIXED:
            raise ValueError("Property type MIXED is not supported")
        else:
            raise ValueError("Unknown property type")

        prop_value = VehiclePropValue(
            area_id=area_id,
            prop=prop,
            int32_values=int32_values,
            int64_values=int64_values,
            float_values=float_values,
            byte_values=byte_values,
            string_value=string_value,
        )
        return VehiclePropValueRequests(
            requests=[VehiclePropValueRequest(value=prop_value)]
        )


# Which part of the property id that mask the value type
PROP_TYPE_MASK = 0x00FF0000


# fmt:off
class VehiclePropertyType(IntEnum):
    STRING    = 0x00100000
    BOOLEAN   = 0x00200000
    INT32     = 0x00400000
    INT32_VEC = 0x00410000
    INT64     = 0x00500000
    INT64_VEC = 0x00510000
    FLOAT     = 0x00600000
    FLOAT_VEC = 0x00610000
    BYTES     = 0x00700000
    MIXED     = 0x00E00000
# fmt:on

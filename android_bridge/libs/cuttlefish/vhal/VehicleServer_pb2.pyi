from google.protobuf import empty_pb2 as _empty_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class StatusCode(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    OK: _ClassVar[StatusCode]
    TRY_AGAIN: _ClassVar[StatusCode]
    INVALID_ARG: _ClassVar[StatusCode]
    NOT_AVAILABLE: _ClassVar[StatusCode]
    ACCESS_DENIED: _ClassVar[StatusCode]
    INTERNAL_ERROR: _ClassVar[StatusCode]
    NOT_AVAILABLE_DISABLED: _ClassVar[StatusCode]
    NOT_AVAILABLE_SPEED_LOW: _ClassVar[StatusCode]
    NOT_AVAILABLE_SPEED_HIGH: _ClassVar[StatusCode]
    NOT_AVAILABLE_POOR_VISIBILITY: _ClassVar[StatusCode]
    NOT_AVAILABLE_SAFETY: _ClassVar[StatusCode]

class VehiclePropertyAccess(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    NONE: _ClassVar[VehiclePropertyAccess]
    READ: _ClassVar[VehiclePropertyAccess]
    WRITE: _ClassVar[VehiclePropertyAccess]
    READ_WRITE: _ClassVar[VehiclePropertyAccess]

class VehiclePropertyChangeMode(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    STATIC: _ClassVar[VehiclePropertyChangeMode]
    ON_CHANGE: _ClassVar[VehiclePropertyChangeMode]
    CONTINUOUS: _ClassVar[VehiclePropertyChangeMode]

class VehiclePropertyStatus(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    AVAILABLE: _ClassVar[VehiclePropertyStatus]
    UNAVAILABLE: _ClassVar[VehiclePropertyStatus]
    ERROR: _ClassVar[VehiclePropertyStatus]
OK: StatusCode
TRY_AGAIN: StatusCode
INVALID_ARG: StatusCode
NOT_AVAILABLE: StatusCode
ACCESS_DENIED: StatusCode
INTERNAL_ERROR: StatusCode
NOT_AVAILABLE_DISABLED: StatusCode
NOT_AVAILABLE_SPEED_LOW: StatusCode
NOT_AVAILABLE_SPEED_HIGH: StatusCode
NOT_AVAILABLE_POOR_VISIBILITY: StatusCode
NOT_AVAILABLE_SAFETY: StatusCode
NONE: VehiclePropertyAccess
READ: VehiclePropertyAccess
WRITE: VehiclePropertyAccess
READ_WRITE: VehiclePropertyAccess
STATIC: VehiclePropertyChangeMode
ON_CHANGE: VehiclePropertyChangeMode
CONTINUOUS: VehiclePropertyChangeMode
AVAILABLE: VehiclePropertyStatus
UNAVAILABLE: VehiclePropertyStatus
ERROR: VehiclePropertyStatus

class DumpOptions(_message.Message):
    __slots__ = ("options",)
    OPTIONS_FIELD_NUMBER: _ClassVar[int]
    options: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, options: _Optional[_Iterable[str]] = ...) -> None: ...

class DumpResult(_message.Message):
    __slots__ = ("caller_should_dump_state", "buffer", "refresh_property_configs")
    CALLER_SHOULD_DUMP_STATE_FIELD_NUMBER: _ClassVar[int]
    BUFFER_FIELD_NUMBER: _ClassVar[int]
    REFRESH_PROPERTY_CONFIGS_FIELD_NUMBER: _ClassVar[int]
    caller_should_dump_state: bool
    buffer: str
    refresh_property_configs: bool
    def __init__(self, caller_should_dump_state: bool = ..., buffer: _Optional[str] = ..., refresh_property_configs: bool = ...) -> None: ...

class VehicleHalCallStatus(_message.Message):
    __slots__ = ("status_code",)
    STATUS_CODE_FIELD_NUMBER: _ClassVar[int]
    status_code: StatusCode
    def __init__(self, status_code: _Optional[_Union[StatusCode, str]] = ...) -> None: ...

class SubscribeOptions(_message.Message):
    __slots__ = ("prop_id", "area_ids", "sample_rate", "resolution", "enable_variable_update_rate")
    PROP_ID_FIELD_NUMBER: _ClassVar[int]
    AREA_IDS_FIELD_NUMBER: _ClassVar[int]
    SAMPLE_RATE_FIELD_NUMBER: _ClassVar[int]
    RESOLUTION_FIELD_NUMBER: _ClassVar[int]
    ENABLE_VARIABLE_UPDATE_RATE_FIELD_NUMBER: _ClassVar[int]
    prop_id: int
    area_ids: _containers.RepeatedScalarFieldContainer[int]
    sample_rate: float
    resolution: float
    enable_variable_update_rate: bool
    def __init__(self, prop_id: _Optional[int] = ..., area_ids: _Optional[_Iterable[int]] = ..., sample_rate: _Optional[float] = ..., resolution: _Optional[float] = ..., enable_variable_update_rate: bool = ...) -> None: ...

class SubscribeRequest(_message.Message):
    __slots__ = ("options",)
    OPTIONS_FIELD_NUMBER: _ClassVar[int]
    options: SubscribeOptions
    def __init__(self, options: _Optional[_Union[SubscribeOptions, _Mapping]] = ...) -> None: ...

class UnsubscribeRequest(_message.Message):
    __slots__ = ("prop_id", "area_id")
    PROP_ID_FIELD_NUMBER: _ClassVar[int]
    AREA_ID_FIELD_NUMBER: _ClassVar[int]
    prop_id: int
    area_id: int
    def __init__(self, prop_id: _Optional[int] = ..., area_id: _Optional[int] = ...) -> None: ...

class VehicleAreaConfig(_message.Message):
    __slots__ = ("area_id", "min_int32_value", "max_int32_value", "min_int64_value", "max_int64_value", "min_float_value", "max_float_value", "supported_enum_values", "access", "support_variable_update_rate")
    AREA_ID_FIELD_NUMBER: _ClassVar[int]
    MIN_INT32_VALUE_FIELD_NUMBER: _ClassVar[int]
    MAX_INT32_VALUE_FIELD_NUMBER: _ClassVar[int]
    MIN_INT64_VALUE_FIELD_NUMBER: _ClassVar[int]
    MAX_INT64_VALUE_FIELD_NUMBER: _ClassVar[int]
    MIN_FLOAT_VALUE_FIELD_NUMBER: _ClassVar[int]
    MAX_FLOAT_VALUE_FIELD_NUMBER: _ClassVar[int]
    SUPPORTED_ENUM_VALUES_FIELD_NUMBER: _ClassVar[int]
    ACCESS_FIELD_NUMBER: _ClassVar[int]
    SUPPORT_VARIABLE_UPDATE_RATE_FIELD_NUMBER: _ClassVar[int]
    area_id: int
    min_int32_value: int
    max_int32_value: int
    min_int64_value: int
    max_int64_value: int
    min_float_value: float
    max_float_value: float
    supported_enum_values: _containers.RepeatedScalarFieldContainer[int]
    access: VehiclePropertyAccess
    support_variable_update_rate: bool
    def __init__(self, area_id: _Optional[int] = ..., min_int32_value: _Optional[int] = ..., max_int32_value: _Optional[int] = ..., min_int64_value: _Optional[int] = ..., max_int64_value: _Optional[int] = ..., min_float_value: _Optional[float] = ..., max_float_value: _Optional[float] = ..., supported_enum_values: _Optional[_Iterable[int]] = ..., access: _Optional[_Union[VehiclePropertyAccess, str]] = ..., support_variable_update_rate: bool = ...) -> None: ...

class VehiclePropConfig(_message.Message):
    __slots__ = ("prop", "access", "change_mode", "area_configs", "config_array", "config_string", "min_sample_rate", "max_sample_rate")
    PROP_FIELD_NUMBER: _ClassVar[int]
    ACCESS_FIELD_NUMBER: _ClassVar[int]
    CHANGE_MODE_FIELD_NUMBER: _ClassVar[int]
    AREA_CONFIGS_FIELD_NUMBER: _ClassVar[int]
    CONFIG_ARRAY_FIELD_NUMBER: _ClassVar[int]
    CONFIG_STRING_FIELD_NUMBER: _ClassVar[int]
    MIN_SAMPLE_RATE_FIELD_NUMBER: _ClassVar[int]
    MAX_SAMPLE_RATE_FIELD_NUMBER: _ClassVar[int]
    prop: int
    access: VehiclePropertyAccess
    change_mode: VehiclePropertyChangeMode
    area_configs: _containers.RepeatedCompositeFieldContainer[VehicleAreaConfig]
    config_array: _containers.RepeatedScalarFieldContainer[int]
    config_string: bytes
    min_sample_rate: float
    max_sample_rate: float
    def __init__(self, prop: _Optional[int] = ..., access: _Optional[_Union[VehiclePropertyAccess, str]] = ..., change_mode: _Optional[_Union[VehiclePropertyChangeMode, str]] = ..., area_configs: _Optional[_Iterable[_Union[VehicleAreaConfig, _Mapping]]] = ..., config_array: _Optional[_Iterable[int]] = ..., config_string: _Optional[bytes] = ..., min_sample_rate: _Optional[float] = ..., max_sample_rate: _Optional[float] = ...) -> None: ...

class VehiclePropValue(_message.Message):
    __slots__ = ("timestamp", "area_id", "prop", "status", "int32_values", "float_values", "int64_values", "byte_values", "string_value")
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    AREA_ID_FIELD_NUMBER: _ClassVar[int]
    PROP_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    INT32_VALUES_FIELD_NUMBER: _ClassVar[int]
    FLOAT_VALUES_FIELD_NUMBER: _ClassVar[int]
    INT64_VALUES_FIELD_NUMBER: _ClassVar[int]
    BYTE_VALUES_FIELD_NUMBER: _ClassVar[int]
    STRING_VALUE_FIELD_NUMBER: _ClassVar[int]
    timestamp: int
    area_id: int
    prop: int
    status: VehiclePropertyStatus
    int32_values: _containers.RepeatedScalarFieldContainer[int]
    float_values: _containers.RepeatedScalarFieldContainer[float]
    int64_values: _containers.RepeatedScalarFieldContainer[int]
    byte_values: bytes
    string_value: str

    def __init__(self, timestamp: _Optional[int] = ..., area_id: _Optional[int] = ..., prop: _Optional[int] = ..., status: _Optional[_Union[VehiclePropertyStatus, str]] = ..., int32_values: _Optional[_Iterable[int]] = ..., float_values: _Optional[_Iterable[float]] = ..., int64_values: _Optional[_Iterable[int]] = ..., byte_values: _Optional[bytes] = ..., string_value: _Optional[str] = ...) -> None: ...

class VehiclePropValues(_message.Message):
    __slots__ = ("values",)
    VALUES_FIELD_NUMBER: _ClassVar[int]
    values: _containers.RepeatedCompositeFieldContainer[VehiclePropValue]
    def __init__(self, values: _Optional[_Iterable[_Union[VehiclePropValue, _Mapping]]] = ...) -> None: ...

class VehiclePropValueRequest(_message.Message):
    __slots__ = ("request_id", "value")
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    request_id: int
    value: VehiclePropValue
    def __init__(self, request_id: _Optional[int] = ..., value: _Optional[_Union[VehiclePropValue, _Mapping]] = ...) -> None: ...

class UpdateSampleRateRequest(_message.Message):
    __slots__ = ("prop", "area_id", "sample_rate")
    PROP_FIELD_NUMBER: _ClassVar[int]
    AREA_ID_FIELD_NUMBER: _ClassVar[int]
    SAMPLE_RATE_FIELD_NUMBER: _ClassVar[int]
    prop: int
    area_id: int
    sample_rate: float
    def __init__(self, prop: _Optional[int] = ..., area_id: _Optional[int] = ..., sample_rate: _Optional[float] = ...) -> None: ...

class SetValueResult(_message.Message):
    __slots__ = ("request_id", "status")
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    request_id: int
    status: StatusCode
    def __init__(self, request_id: _Optional[int] = ..., status: _Optional[_Union[StatusCode, str]] = ...) -> None: ...

class GetValueResult(_message.Message):
    __slots__ = ("request_id", "status", "value")
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    request_id: int
    status: StatusCode
    value: VehiclePropValue
    def __init__(self, request_id: _Optional[int] = ..., status: _Optional[_Union[StatusCode, str]] = ..., value: _Optional[_Union[VehiclePropValue, _Mapping]] = ...) -> None: ...

class VehiclePropValueRequests(_message.Message):
    __slots__ = ("requests",)
    REQUESTS_FIELD_NUMBER: _ClassVar[int]
    requests: _containers.RepeatedCompositeFieldContainer[VehiclePropValueRequest]
    def __init__(self, requests: _Optional[_Iterable[_Union[VehiclePropValueRequest, _Mapping]]] = ...) -> None: ...

class SetValueResults(_message.Message):
    __slots__ = ("results",)
    RESULTS_FIELD_NUMBER: _ClassVar[int]
    results: _containers.RepeatedCompositeFieldContainer[SetValueResult]
    def __init__(self, results: _Optional[_Iterable[_Union[SetValueResult, _Mapping]]] = ...) -> None: ...

class GetValueResults(_message.Message):
    __slots__ = ("results",)
    RESULTS_FIELD_NUMBER: _ClassVar[int]
    results: _containers.RepeatedCompositeFieldContainer[GetValueResult]
    def __init__(self, results: _Optional[_Iterable[_Union[GetValueResult, _Mapping]]] = ...) -> None: ...

from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union
DESCRIPTOR: _descriptor.FileDescriptor

class VehicleMotion(_message.Message):
    __slots__ = ('time_stamp', 'session_timestamp', 'acceleration_x', 'acceleration_y', 'acceleration_z', 'speed', 'wheel_speed_fr', 'wheel_speed_fl', 'wheel_speed_rr', 'wheel_speed_rl', 'steering_angle', 'steering_angle_normalized', 'gas_pedal_normalized', 'brake_pedal_normalized', 'instructor_pedals_used', 'gear', 'speed_dashboard', 'mileage', 'speed_limiter_enabled', 'speed_limiter_target', 'cruise_control_enabled', 'cruise_control_target')

    class Gear(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        P: _ClassVar[VehicleMotion.Gear]
        R: _ClassVar[VehicleMotion.Gear]
        N: _ClassVar[VehicleMotion.Gear]
        D: _ClassVar[VehicleMotion.Gear]
        B: _ClassVar[VehicleMotion.Gear]
    P: VehicleMotion.Gear
    R: VehicleMotion.Gear
    N: VehicleMotion.Gear
    D: VehicleMotion.Gear
    B: VehicleMotion.Gear
    TIME_STAMP_FIELD_NUMBER: _ClassVar[int]
    SESSION_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    ACCELERATION_X_FIELD_NUMBER: _ClassVar[int]
    ACCELERATION_Y_FIELD_NUMBER: _ClassVar[int]
    ACCELERATION_Z_FIELD_NUMBER: _ClassVar[int]
    SPEED_FIELD_NUMBER: _ClassVar[int]
    WHEEL_SPEED_FR_FIELD_NUMBER: _ClassVar[int]
    WHEEL_SPEED_FL_FIELD_NUMBER: _ClassVar[int]
    WHEEL_SPEED_RR_FIELD_NUMBER: _ClassVar[int]
    WHEEL_SPEED_RL_FIELD_NUMBER: _ClassVar[int]
    STEERING_ANGLE_FIELD_NUMBER: _ClassVar[int]
    STEERING_ANGLE_NORMALIZED_FIELD_NUMBER: _ClassVar[int]
    GAS_PEDAL_NORMALIZED_FIELD_NUMBER: _ClassVar[int]
    BRAKE_PEDAL_NORMALIZED_FIELD_NUMBER: _ClassVar[int]
    INSTRUCTOR_PEDALS_USED_FIELD_NUMBER: _ClassVar[int]
    GEAR_FIELD_NUMBER: _ClassVar[int]
    SPEED_DASHBOARD_FIELD_NUMBER: _ClassVar[int]
    MILEAGE_FIELD_NUMBER: _ClassVar[int]
    SPEED_LIMITER_ENABLED_FIELD_NUMBER: _ClassVar[int]
    SPEED_LIMITER_TARGET_FIELD_NUMBER: _ClassVar[int]
    CRUISE_CONTROL_ENABLED_FIELD_NUMBER: _ClassVar[int]
    CRUISE_CONTROL_TARGET_FIELD_NUMBER: _ClassVar[int]
    time_stamp: _timestamp_pb2.Timestamp
    session_timestamp: int
    acceleration_x: float
    acceleration_y: float
    acceleration_z: float
    speed: float
    wheel_speed_fr: float
    wheel_speed_fl: float
    wheel_speed_rr: float
    wheel_speed_rl: float
    steering_angle: float
    steering_angle_normalized: float
    gas_pedal_normalized: float
    brake_pedal_normalized: float
    instructor_pedals_used: bool
    gear: VehicleMotion.Gear
    speed_dashboard: float
    mileage: float
    speed_limiter_enabled: bool
    speed_limiter_target: int
    cruise_control_enabled: bool
    cruise_control_target: int

    def __init__(self, time_stamp: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]]=..., session_timestamp: _Optional[int]=..., acceleration_x: _Optional[float]=..., acceleration_y: _Optional[float]=..., acceleration_z: _Optional[float]=..., speed: _Optional[float]=..., wheel_speed_fr: _Optional[float]=..., wheel_speed_fl: _Optional[float]=..., wheel_speed_rr: _Optional[float]=..., wheel_speed_rl: _Optional[float]=..., steering_angle: _Optional[float]=..., steering_angle_normalized: _Optional[float]=..., gas_pedal_normalized: _Optional[float]=..., brake_pedal_normalized: _Optional[float]=..., instructor_pedals_used: bool=..., gear: _Optional[_Union[VehicleMotion.Gear, str]]=..., speed_dashboard: _Optional[float]=..., mileage: _Optional[float]=..., speed_limiter_enabled: bool=..., speed_limiter_target: _Optional[int]=..., cruise_control_enabled: bool=..., cruise_control_target: _Optional[int]=...) -> None:
        ...

class VehicleState(_message.Message):
    __slots__ = ('time_stamp', 'session_timestamp', 'door_closed_fl', 'door_closed_fr', 'door_closed_rl', 'door_closed_rr', 'driver_seatbelt_on', 'passenger_seatbelt_on', 'headlight_high_beam_on', 'turn_signal', 'wipers_mode', 'wipers_rain_detect_sensitivity', 'wipers_parked')

    class TurnSignal(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        OFF: _ClassVar[VehicleState.TurnSignal]
        LEFT: _ClassVar[VehicleState.TurnSignal]
        RIGHT: _ClassVar[VehicleState.TurnSignal]
    OFF: VehicleState.TurnSignal
    LEFT: VehicleState.TurnSignal
    RIGHT: VehicleState.TurnSignal

    class WiperMode(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        DISABLED: _ClassVar[VehicleState.WiperMode]
        AUTO: _ClassVar[VehicleState.WiperMode]
        SLOW: _ClassVar[VehicleState.WiperMode]
        FAST: _ClassVar[VehicleState.WiperMode]
    DISABLED: VehicleState.WiperMode
    AUTO: VehicleState.WiperMode
    SLOW: VehicleState.WiperMode
    FAST: VehicleState.WiperMode
    TIME_STAMP_FIELD_NUMBER: _ClassVar[int]
    SESSION_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    DOOR_CLOSED_FL_FIELD_NUMBER: _ClassVar[int]
    DOOR_CLOSED_FR_FIELD_NUMBER: _ClassVar[int]
    DOOR_CLOSED_RL_FIELD_NUMBER: _ClassVar[int]
    DOOR_CLOSED_RR_FIELD_NUMBER: _ClassVar[int]
    DRIVER_SEATBELT_ON_FIELD_NUMBER: _ClassVar[int]
    PASSENGER_SEATBELT_ON_FIELD_NUMBER: _ClassVar[int]
    HEADLIGHT_HIGH_BEAM_ON_FIELD_NUMBER: _ClassVar[int]
    TURN_SIGNAL_FIELD_NUMBER: _ClassVar[int]
    WIPERS_MODE_FIELD_NUMBER: _ClassVar[int]
    WIPERS_RAIN_DETECT_SENSITIVITY_FIELD_NUMBER: _ClassVar[int]
    WIPERS_PARKED_FIELD_NUMBER: _ClassVar[int]
    time_stamp: _timestamp_pb2.Timestamp
    session_timestamp: int
    door_closed_fl: bool
    door_closed_fr: bool
    door_closed_rl: bool
    door_closed_rr: bool
    driver_seatbelt_on: bool
    passenger_seatbelt_on: bool
    headlight_high_beam_on: bool
    turn_signal: VehicleState.TurnSignal
    wipers_mode: VehicleState.WiperMode
    wipers_rain_detect_sensitivity: int
    wipers_parked: bool

    def __init__(self, time_stamp: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]]=..., session_timestamp: _Optional[int]=..., door_closed_fl: bool=..., door_closed_fr: bool=..., door_closed_rl: bool=..., door_closed_rr: bool=..., driver_seatbelt_on: bool=..., passenger_seatbelt_on: bool=..., headlight_high_beam_on: bool=..., turn_signal: _Optional[_Union[VehicleState.TurnSignal, str]]=..., wipers_mode: _Optional[_Union[VehicleState.WiperMode, str]]=..., wipers_rain_detect_sensitivity: _Optional[int]=..., wipers_parked: bool=...) -> None:
        ...
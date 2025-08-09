from google.protobuf import empty_pb2 as _empty_pb2
from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union
DESCRIPTOR: _descriptor.FileDescriptor

class StartRecordingRequest(_message.Message):
    __slots__ = ('bitrate_kbps', 'maxlength_mins')
    BITRATE_KBPS_FIELD_NUMBER: _ClassVar[int]
    MAXLENGTH_MINS_FIELD_NUMBER: _ClassVar[int]
    bitrate_kbps: int
    maxlength_mins: int

    def __init__(self, bitrate_kbps: _Optional[int]=..., maxlength_mins: _Optional[int]=...) -> None:
        ...

class StartRecordingRequestV2(_message.Message):
    __slots__ = ('bitrate_bps', 'maxlength_mins')
    BITRATE_BPS_FIELD_NUMBER: _ClassVar[int]
    MAXLENGTH_MINS_FIELD_NUMBER: _ClassVar[int]
    bitrate_bps: int
    maxlength_mins: int

    def __init__(self, bitrate_bps: _Optional[int]=..., maxlength_mins: _Optional[int]=...) -> None:
        ...

class SessionStatus(_message.Message):
    __slots__ = ('time_stamp', 'is_recording', 'drive_name')
    TIME_STAMP_FIELD_NUMBER: _ClassVar[int]
    IS_RECORDING_FIELD_NUMBER: _ClassVar[int]
    DRIVE_NAME_FIELD_NUMBER: _ClassVar[int]
    time_stamp: _timestamp_pb2.Timestamp
    is_recording: bool
    drive_name: str

    def __init__(self, time_stamp: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]]=..., is_recording: bool=..., drive_name: _Optional[str]=...) -> None:
        ...

class Incident(_message.Message):
    __slots__ = ('drive_name', 'incident_id', 'start_time_ns', 'end_time_ns')
    DRIVE_NAME_FIELD_NUMBER: _ClassVar[int]
    INCIDENT_ID_FIELD_NUMBER: _ClassVar[int]
    START_TIME_NS_FIELD_NUMBER: _ClassVar[int]
    END_TIME_NS_FIELD_NUMBER: _ClassVar[int]
    drive_name: str
    incident_id: str
    start_time_ns: int
    end_time_ns: int

    def __init__(self, drive_name: _Optional[str]=..., incident_id: _Optional[str]=..., start_time_ns: _Optional[int]=..., end_time_ns: _Optional[int]=...) -> None:
        ...

class IncidentResponse(_message.Message):
    __slots__ = ('error',)
    ERROR_FIELD_NUMBER: _ClassVar[int]
    error: str

    def __init__(self, error: _Optional[str]=...) -> None:
        ...

class DriveSessionInfo(_message.Message):
    __slots__ = ('time_stamp', 'drive_name', 'version')
    TIME_STAMP_FIELD_NUMBER: _ClassVar[int]
    DRIVE_NAME_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    time_stamp: _timestamp_pb2.Timestamp
    drive_name: str
    version: int

    def __init__(self, time_stamp: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]]=..., drive_name: _Optional[str]=..., version: _Optional[int]=...) -> None:
        ...

class Gnss(_message.Message):
    __slots__ = ('time_stamp', 'session_timestamp', 'status', 'service', 'latitude', 'longitude', 'altitude', 'heading', 'heading_error', 'speed', 'speed_error', 'has_highprecision_loc', 'hp_loc_latitude', 'hp_loc_longitude', 'hp_loc_altitude', 'position_covariance', 'position_covariance_type')

    class NavSatStatus(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        STATUS_FIX: _ClassVar[Gnss.NavSatStatus]
        STATUS_SBAS_FIX: _ClassVar[Gnss.NavSatStatus]
        STATUS_GBAS_FIX: _ClassVar[Gnss.NavSatStatus]
        STATUS_NO_FIX: _ClassVar[Gnss.NavSatStatus]
    STATUS_FIX: Gnss.NavSatStatus
    STATUS_SBAS_FIX: Gnss.NavSatStatus
    STATUS_GBAS_FIX: Gnss.NavSatStatus
    STATUS_NO_FIX: Gnss.NavSatStatus

    class NavService(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        SERVICE_NONE: _ClassVar[Gnss.NavService]
        SERVICE_GPS: _ClassVar[Gnss.NavService]
        SERVICE_GLOSNASS: _ClassVar[Gnss.NavService]
        SERVICE_COMPASS: _ClassVar[Gnss.NavService]
        SERVICE_GALILEO: _ClassVar[Gnss.NavService]
    SERVICE_NONE: Gnss.NavService
    SERVICE_GPS: Gnss.NavService
    SERVICE_GLOSNASS: Gnss.NavService
    SERVICE_COMPASS: Gnss.NavService
    SERVICE_GALILEO: Gnss.NavService

    class NavSatFix(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        COVARIANCE_TYPE_UNKNOWN: _ClassVar[Gnss.NavSatFix]
        COVARIANCE_TYPE_APPROXIMATED: _ClassVar[Gnss.NavSatFix]
        COVARIANCE_TYPE_DIAGONAL_KNOWN: _ClassVar[Gnss.NavSatFix]
        COVARIANCE_TYPE_KNOWN: _ClassVar[Gnss.NavSatFix]
    COVARIANCE_TYPE_UNKNOWN: Gnss.NavSatFix
    COVARIANCE_TYPE_APPROXIMATED: Gnss.NavSatFix
    COVARIANCE_TYPE_DIAGONAL_KNOWN: Gnss.NavSatFix
    COVARIANCE_TYPE_KNOWN: Gnss.NavSatFix
    TIME_STAMP_FIELD_NUMBER: _ClassVar[int]
    SESSION_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    SERVICE_FIELD_NUMBER: _ClassVar[int]
    LATITUDE_FIELD_NUMBER: _ClassVar[int]
    LONGITUDE_FIELD_NUMBER: _ClassVar[int]
    ALTITUDE_FIELD_NUMBER: _ClassVar[int]
    HEADING_FIELD_NUMBER: _ClassVar[int]
    HEADING_ERROR_FIELD_NUMBER: _ClassVar[int]
    SPEED_FIELD_NUMBER: _ClassVar[int]
    SPEED_ERROR_FIELD_NUMBER: _ClassVar[int]
    HAS_HIGHPRECISION_LOC_FIELD_NUMBER: _ClassVar[int]
    HP_LOC_LATITUDE_FIELD_NUMBER: _ClassVar[int]
    HP_LOC_LONGITUDE_FIELD_NUMBER: _ClassVar[int]
    HP_LOC_ALTITUDE_FIELD_NUMBER: _ClassVar[int]
    POSITION_COVARIANCE_FIELD_NUMBER: _ClassVar[int]
    POSITION_COVARIANCE_TYPE_FIELD_NUMBER: _ClassVar[int]
    time_stamp: _timestamp_pb2.Timestamp
    session_timestamp: int
    status: Gnss.NavSatStatus
    service: Gnss.NavService
    latitude: float
    longitude: float
    altitude: float
    heading: float
    heading_error: float
    speed: float
    speed_error: float
    has_highprecision_loc: bool
    hp_loc_latitude: float
    hp_loc_longitude: float
    hp_loc_altitude: float
    position_covariance: _containers.RepeatedScalarFieldContainer[float]
    position_covariance_type: Gnss.NavSatFix

    def __init__(self, time_stamp: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]]=..., session_timestamp: _Optional[int]=..., status: _Optional[_Union[Gnss.NavSatStatus, str]]=..., service: _Optional[_Union[Gnss.NavService, str]]=..., latitude: _Optional[float]=..., longitude: _Optional[float]=..., altitude: _Optional[float]=..., heading: _Optional[float]=..., heading_error: _Optional[float]=..., speed: _Optional[float]=..., speed_error: _Optional[float]=..., has_highprecision_loc: bool=..., hp_loc_latitude: _Optional[float]=..., hp_loc_longitude: _Optional[float]=..., hp_loc_altitude: _Optional[float]=..., position_covariance: _Optional[_Iterable[float]]=..., position_covariance_type: _Optional[_Union[Gnss.NavSatFix, str]]=...) -> None:
        ...

class ImageMetadata(_message.Message):
    __slots__ = ('time_stamp', 'session_timestamp', 'camera_name', 'encoding', 'exposure_time', 'frame_idx', 'gain_level_db', 'gain_level_digital', 'height', 'width', 'scene_lux', 'sensor_iso')
    TIME_STAMP_FIELD_NUMBER: _ClassVar[int]
    SESSION_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    CAMERA_NAME_FIELD_NUMBER: _ClassVar[int]
    ENCODING_FIELD_NUMBER: _ClassVar[int]
    EXPOSURE_TIME_FIELD_NUMBER: _ClassVar[int]
    FRAME_IDX_FIELD_NUMBER: _ClassVar[int]
    GAIN_LEVEL_DB_FIELD_NUMBER: _ClassVar[int]
    GAIN_LEVEL_DIGITAL_FIELD_NUMBER: _ClassVar[int]
    HEIGHT_FIELD_NUMBER: _ClassVar[int]
    WIDTH_FIELD_NUMBER: _ClassVar[int]
    SCENE_LUX_FIELD_NUMBER: _ClassVar[int]
    SENSOR_ISO_FIELD_NUMBER: _ClassVar[int]
    time_stamp: _timestamp_pb2.Timestamp
    session_timestamp: int
    camera_name: str
    encoding: str
    exposure_time: float
    frame_idx: int
    gain_level_db: float
    gain_level_digital: float
    height: int
    width: int
    scene_lux: float
    sensor_iso: int

    def __init__(self, time_stamp: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]]=..., session_timestamp: _Optional[int]=..., camera_name: _Optional[str]=..., encoding: _Optional[str]=..., exposure_time: _Optional[float]=..., frame_idx: _Optional[int]=..., gain_level_db: _Optional[float]=..., gain_level_digital: _Optional[float]=..., height: _Optional[int]=..., width: _Optional[int]=..., scene_lux: _Optional[float]=..., sensor_iso: _Optional[int]=...) -> None:
        ...
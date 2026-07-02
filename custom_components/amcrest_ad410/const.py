"""Constants for the Amcrest AD410 integration."""

from __future__ import annotations

DOMAIN = "amcrest_ad410"
MANUFACTURER = "Amcrest"

PLATFORMS: list[str] = [
    "binary_sensor",
    "camera",
    "event",
    "media_player",
]

CONF_RTSP_PORT = "rtsp_port"
CONF_USE_SSL = "use_ssl"
CONF_VERIFY_SSL = "verify_ssl"
CONF_STREAM_SUBTYPE = "stream_subtype"
CONF_DOORBELL_CODES = "doorbell_codes"
CONF_MOTION_CODES = "motion_codes"
CONF_HUMAN_CODES = "human_codes"
CONF_SPEAKER_ENDPOINT = "speaker_endpoint"
CONF_SPEAKER_CONTENT_TYPE = "speaker_content_type"
CONF_FFMPEG_BINARY = "ffmpeg_binary"
CONF_MAX_AUDIO_SECONDS = "max_audio_seconds"
CONF_CAMERA_STREAMS = "camera_streams"

DEFAULT_NAME = "Amcrest AD410"
DEFAULT_PORT = 80
DEFAULT_RTSP_PORT = 554
DEFAULT_STREAM_SUBTYPE = 0
DEFAULT_CAMERA_STREAMS = ["0"]
DEFAULT_FFMPEG_BINARY = "ffmpeg"
DEFAULT_MAX_AUDIO_SECONDS = 30

DEFAULT_DOORBELL_CODES = [
    "CallNoAnswered",
    "DoorBell",
    "AlarmLocal",
    "VTOCall",
    "BackKeyLight",
]
DEFAULT_MOTION_CODES = ["VideoMotion"]
DEFAULT_HUMAN_CODES = [
    "SmartMotionHuman",
    "HumanDetect",
    "HumanBodyDetection",
    "CrossRegionDetection",
    "CrossLineDetection",
]
DEFAULT_EVENT_CODES = sorted(
    set(DEFAULT_DOORBELL_CODES + DEFAULT_MOTION_CODES + DEFAULT_HUMAN_CODES)
)

DEFAULT_SPEAKER_ENDPOINT = (
    "/cgi-bin/audio.cgi?action=postAudio&httptype=singlepart&channel=1"
)
DEFAULT_SPEAKER_CONTENT_TYPE = "Audio/G.711Mu"

EVENT_AD410 = f"{DOMAIN}_event"
SIGNAL_EVENT = f"{DOMAIN}_event"
SIGNAL_STATE = f"{DOMAIN}_state"

ATTR_ACTION = "action"
ATTR_CODE = "code"
ATTR_DEVICE_ID = "device_id"
ATTR_INDEX = "index"
ATTR_RAW = "raw"
ATTR_TYPE = "type"
ATTR_SOURCE = "source"

EVENT_DOORBELL_PRESSED = "doorbell_pressed"
EVENT_MOTION_DETECTED = "motion_detected"
EVENT_MOTION_CLEARED = "motion_cleared"
EVENT_HUMAN_DETECTED = "human_detected"
EVENT_HUMAN_CLEARED = "human_cleared"

TRIGGER_TYPES = {
    EVENT_DOORBELL_PRESSED,
    EVENT_MOTION_DETECTED,
    EVENT_MOTION_CLEARED,
    EVENT_HUMAN_DETECTED,
    EVENT_HUMAN_CLEARED,
}

START_ACTIONS = {"start", "pulse", "active", "true", "on"}
STOP_ACTIONS = {"stop", "inactive", "false", "off"}

SERVICE_PLAY_MICROPHONE_STREAM = "play_microphone_stream"
SERVICE_PLAY_AUDIO_ON_DOORBELL = "play_audio_on_doorbell"

FIELD_MEDIA_PLAYER_ENTITY_ID = "media_player_entity_id"
FIELD_MEDIA_CONTENT_ID = "media_content_id"
FIELD_MEDIA_CONTENT_TYPE = "media_content_type"
FIELD_SUBTYPE = "subtype"
FIELD_DEVICE_ID = "device_id"
FIELD_ENTRY_ID = "entry_id"
FIELD_DURATION = "duration"

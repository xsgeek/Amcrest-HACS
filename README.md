# Amcrest AD410 Doorbell for Home Assistant

Custom HACS integration for the Amcrest AD410 video doorbell.

## Features

- Local config flow using the AD410 HTTP CGI API with digest authentication.
- Doorbell, motion, and optional human-detection event entities.
- Device automation triggers for:
  - `doorbell_pressed`
  - `motion_detected`
  - `motion_cleared`
  - `human_detected`
  - `human_cleared`
- Binary sensors for the latest known motion and human-detection state.
- Camera entity with RTSP stream source and HTTP snapshot support.
- Service to send the doorbell microphone/camera RTSP stream to a Home Assistant media player.
- Best-effort speaker media player/service that converts media to raw G.711 mu-law and posts it to a configurable Dahua/Amcrest audio CGI endpoint.

## Installation

### HACS custom repository

1. Add this repository to HACS as an integration repository.
2. Install **Amcrest AD410 Doorbell**.
3. Restart Home Assistant.
4. Go to **Settings > Devices & services > Add integration** and search for **Amcrest AD410 Doorbell**.

### Manual

Copy `custom_components/amcrest_ad410` into your Home Assistant `custom_components` directory, then restart Home Assistant.

## AD410 setup notes

Enable local access, RTSP, and the AD410 account you want Home Assistant to use from the Amcrest app or the device web UI. The integration uses local LAN access only.

The event stream is based on Dahua-style:

```text
/cgi-bin/eventManager.cgi?action=attach&codes=[VideoMotion,CallNoAnswered,...]
```

Firmware revisions differ on event names. The defaults are intentionally broad:

- Doorbell: `CallNoAnswered`, `DoorBell`, `AlarmLocal`, `VTOCall`, `BackKeyLight`
- Motion: `VideoMotion`
- Human: `SmartMotionHuman`, `HumanDetect`, `HumanBodyDetection`

If human detection is not emitted by your firmware, the human event entity and binary sensor will remain idle. Open the integration options to adjust event code lists.

## Services

### `amcrest_ad410.play_microphone_stream`

Sends the doorbell RTSP stream to another Home Assistant media player.

```yaml
service: amcrest_ad410.play_microphone_stream
data:
  media_player_entity_id: media_player.kitchen_display
```

Many media players do not support RTSP directly. For those devices, use the camera entity or a player that can consume RTSP streams.

### `amcrest_ad410.play_audio_on_doorbell`

Converts a media source, URL, or local path to raw G.711 mu-law and posts it to the configured doorbell speaker endpoint.

```yaml
service: amcrest_ad410.play_audio_on_doorbell
data:
  media_content_id: media-source://media_source/local/chime.wav
  duration: 10
```

Two-way audio/talkback is the least standardized part of AD410 firmware. The default endpoint is:

```text
/cgi-bin/audio.cgi?action=postAudio&httptype=singlepart&channel=1
```

If your firmware expects a different endpoint or content type, change `speaker_endpoint` and `speaker_content_type` in the integration options.

## Automation examples

Doorbell pressed:

```yaml
trigger:
  - platform: device
    domain: amcrest_ad410
    device_id: YOUR_DEVICE_ID
    type: doorbell_pressed
action:
  - service: notify.mobile_app_phone
    data:
      message: Doorbell pressed
```

Motion starts and stops:

```yaml
trigger:
  - platform: device
    domain: amcrest_ad410
    device_id: YOUR_DEVICE_ID
    type: motion_detected
  - platform: device
    domain: amcrest_ad410
    device_id: YOUR_DEVICE_ID
    type: motion_cleared
```

Raw domain event:

```yaml
trigger:
  - platform: event
    event_type: amcrest_ad410_event
    event_data:
      type: doorbell_pressed
```

## Development

This repo is laid out as a HACS custom integration:

```text
custom_components/amcrest_ad410/
```

Useful local checks:

```powershell
python -m compileall custom_components tests
python -m pytest
```

Install Home Assistant and development tooling in your VS Code Python environment if you want full IntelliSense for Home Assistant imports.

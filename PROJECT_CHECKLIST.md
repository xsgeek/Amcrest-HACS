# Amcrest AD410 HACS Project Checklist

Last updated: 2026-07-02

This checklist tracks the original goals from the "Add Amcrest AD410 HACS module" chat plus new goals added as the project evolves.

## Status Legend

- Backlog: agreed goal, not designed or implemented yet.
- Candidate implemented: code exists in the integration and local checks pass, but still needs live Home Assistant testing.
- Verified: tested against the live AD410/Home Assistant environment and accepted.
- Blocked: waiting on missing API support, device behavior, credentials, or a design decision.

## Goals

| ID | Goal | Desired Home Assistant result | Current status | Test status | Notes / next checks |
| --- | --- | --- | --- | --- | --- |
| AD410-001 | Raise a doorbell pressed event that can be used in automations and scripts as a trigger. | Device automation trigger and/or domain event fires when the AD410 button is pressed. | Verified | Done. Live AD410 button press fired the `Front Door Bell Pressed` automation. | Fixed the HA 2026.2 device-trigger import path on branch `AD410-001`. Backend verification on 2026-07-02 shows `doorbell_pressed` is returned for the Main Portal device. The active `Front Door Bell Pressed` automation was manually wired to the Main Portal `doorbell_pressed` device trigger; synthetic and real doorbell-press tests both fired the automation successfully. After the manual wiring, the trigger also appears correctly in the HA UI. |
| AD410-002 | Raise an event when the motion sensor detects movement, and when movement ceases. | Separate triggerable events for motion start and motion clear. | Candidate implemented | Device triggers are available in active HA; needs live motion start/stop test. | Backend verification on 2026-07-02 shows `motion_detected` and `motion_cleared` are returned for the Main Portal device. Confirm `VideoMotion` or configured motion codes map cleanly to those triggers; verify binary sensor state changes match event timing. |
| AD410-003 | If available through the AD410 API, raise Human Detected as its own event for automations and scripts. | Separate triggerable human detected and human cleared events, independent from generic motion. | Candidate implemented, API support confirmed | Device triggers are available in active HA; needs live human-trigger event capture. | Backend verification on 2026-07-02 shows `human_detected` and `human_cleared` are returned for the Main Portal device. Live AD410 reports `VideoAnalyseRule[0][0].Enable=true`, `Type=CrossRegionDetection`, and `ObjectTypes[0]=Human`; `SmartMotionDetect` returned `400 Error`. Passive event-stream attach succeeded for `CrossRegionDetection`, `CrossLineDetection`, `SmartMotionHuman`, `VideoMotion`, and `VideoMotionInfo`, but no event occurred during the 20-second listen window. |
| AD410-004 | Stream the microphone input from the doorbell to a registered media device in Home Assistant. | Service can send the AD410 camera/microphone stream to a target `media_player` entity. | Candidate implemented | Installed and configured in active HA; needs media-player compatibility test. | Confirm the RTSP stream includes usable audio and identify which HA media players can consume it directly. |
| AD410-005 | Allow input from a registered sound source device in Home Assistant and play the sound on the doorbell speaker. | Service and/or media player entity can play HA media through the AD410 speaker. | Candidate implemented | Installed and configured in active HA; needs endpoint, codec, and playback test. | The talkback/speaker CGI endpoint may be firmware-specific. Verify G.711 mu-law conversion, content type, maximum duration, and whether the AD410 accepts streamed or single-part audio. |
| AD410-006 | Using the `rroller/dahua` repository as a reference, create an option to stream the camera output to a window hosted in the HA dashboard and other cards. | Camera output is available in Lovelace/dashboard camera cards and other HA cards with a user-selectable stream option where appropriate. | Verified | Done. Main Portal Camera can be added as a HA dashboard badge. | Verified on 2026-07-02 after HA restart/browser refresh: stale `front_portal` entries were gone from the badge picker, and `camera.main_portal` / Main Portal Camera was available and addable as a badge. Optional Main/Sub stream refinements may be added later. |

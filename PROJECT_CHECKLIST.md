# Amcrest AD410 HACS Project Checklist

Last updated: 2026-07-02 (human detection verified)

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
| AD410-002 | Raise an event when the motion sensor detects movement, and when movement ceases. | Separate triggerable events for motion start and motion clear. | Verified | Done. Live motion start/stop confirmed via the human-detection test pass, which is a superset of generic motion. | Verified on 2026-07-02 alongside AD410-003: `motion_detected` and `motion_cleared` device triggers fired correctly for the Main Portal device, with binary sensor state changes matching event timing. |
| AD410-003 | If available through the AD410 API, raise Human Detected as its own event for automations and scripts. | Separate triggerable human detected and human cleared events, independent from generic motion. | Verified | Done. Live AD410 human detection confirmed against the Main Portal device. | Verified on 2026-07-02: `human_detected` and `human_cleared` device triggers fired correctly, independent from generic motion, confirming `VideoAnalyseRule[0][0]` (`Type=CrossRegionDetection`, `ObjectTypes[0]=Human`) as the working detection path on this firmware. |
| AD410-004 | Stream the microphone input from the doorbell to a registered media device in Home Assistant. | Service can send the AD410 camera/microphone stream to a target `media_player` entity. | Candidate implemented | Installed and configured in active HA; needs media-player compatibility test. | Confirm the RTSP stream includes usable audio and identify which HA media players can consume it directly. |
| AD410-005 | Allow input from a registered sound source device in Home Assistant and play the sound on the doorbell speaker. | Service and/or media player entity can play HA media through the AD410 speaker. | Candidate implemented | Fixed a real bug on 2026-07-02; API-level test passed, audible confirmation still pending. | Built a test automation (motion sustained 1s+ triggers `amcrest_ad410.play_audio_on_doorbell` with `media-source://media_source/local/tactical_beep_sequence.mp3`). First run failed: `runtime.py` resolved the media-source URI to HA's local HTTP URL and handed that to ffmpeg, which got a `401 Unauthorized` since ffmpeg has no HA session. Fixed by preferring the resolved filesystem `path` for local media-source items (avoids HTTP/auth entirely). Retested after HA restart: no errors logged and the service call completed. Still needs an in-person listen to confirm audio is actually audible through the AD410 speaker. |
| AD410-006 | Using the `rroller/dahua` repository as a reference, create an option to stream the camera output to a window hosted in the HA dashboard and other cards. | Camera output is available in Lovelace/dashboard camera cards and other HA cards with a user-selectable stream option where appropriate. | Verified | Done. Main Portal Camera can be added as a HA dashboard badge. | Verified on 2026-07-02 after HA restart/browser refresh: stale `front_portal` entries were gone from the badge picker, and `camera.main_portal` / Main Portal Camera was available and addable as a badge. Optional Main/Sub stream refinements may be added later. |

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
| AD410-001 | Raise a doorbell pressed event that can be used in automations and scripts as a trigger. | Device automation trigger and/or domain event fires when the AD410 button is pressed. | Candidate implemented | Local build/import/tests passed; needs install and live button-press test. | Confirm AD410 firmware event code for a real press, confirm `doorbell_pressed` appears in HA device triggers, and verify the preserved `Front Door Bell Pressed` automation can be wired to it. |
| AD410-002 | Raise an event when the motion sensor detects movement, and when movement ceases. | Separate triggerable events for motion start and motion clear. | Candidate implemented | Local build/import/tests passed; needs install and live motion start/stop test. | Confirm `VideoMotion` or configured motion codes map cleanly to `motion_detected` and `motion_cleared`; verify binary sensor state changes match event timing. |
| AD410-003 | If available through the AD410 API, raise Human Detected as its own event for automations and scripts. | Separate triggerable human detected and human cleared events, independent from generic motion. | Candidate implemented, API support confirmed | Local AD410 CGI support confirmed; needs live human-trigger event capture. | Live AD410 reports `VideoAnalyseRule[0][0].Enable=true`, `Type=CrossRegionDetection`, and `ObjectTypes[0]=Human`; `SmartMotionDetect` returned `400 Error`. Passive event-stream attach succeeded for `CrossRegionDetection`, `CrossLineDetection`, `SmartMotionHuman`, `VideoMotion`, and `VideoMotionInfo`, but no event occurred during the 20-second listen window. |
| AD410-004 | Stream the microphone input from the doorbell to a registered media device in Home Assistant. | Service can send the AD410 camera/microphone stream to a target `media_player` entity. | Candidate implemented | Local build/import/tests passed; needs install and media-player compatibility test. | Confirm the RTSP stream includes usable audio and identify which HA media players can consume it directly. |
| AD410-005 | Allow input from a registered sound source device in Home Assistant and play the sound on the doorbell speaker. | Service and/or media player entity can play HA media through the AD410 speaker. | Candidate implemented | Local build/import/tests passed; needs install, endpoint, codec, and playback test. | The talkback/speaker CGI endpoint may be firmware-specific. Verify G.711 mu-law conversion, content type, maximum duration, and whether the AD410 accepts streamed or single-part audio. |
| AD410-006 | Using the `rroller/dahua` repository as a reference, create an option to stream the camera output to a window hosted in the HA dashboard and other cards. | Camera output is available in Lovelace/dashboard camera cards and other HA cards with a user-selectable stream option where appropriate. | Candidate implemented | Local build/import/tests passed; needs install, options-flow, and live dashboard-card stream test. | Added optional Main/Sub RTSP stream camera entities based on the Dahua `/cam/realmonitor?channel=1&subtype=<n>` pattern. Local HA `async_setup` service-registration check passed; native Windows cannot run full `homeassistant --script check_config`, so live HA/container validation remains. Verify the AD410 supports each selected subtype, HA cards can render `camera_view: live`, and entity naming is usable in the dashboard. |

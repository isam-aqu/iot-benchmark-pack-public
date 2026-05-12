# Firmware Versioning

This repo uses a shared semantic firmware version for all sketches in `firmware/`.

## Current Version

- `0.5.0`

## Source Of Truth

- Update `firmware/firmware_version.h`

The version is defined by:

- `IOT_FIRMWARE_VERSION_MAJOR`
- `IOT_FIRMWARE_VERSION_MINOR`
- `IOT_FIRMWARE_VERSION_PATCH`

All benchmark sketches include this header and print the shared version to the serial console during boot.

## Bump Rules

- Patch: bug fixes, logging fixes, wiring-safe refactors, or internal cleanup that does not change intended firmware behavior or operator workflow.
- Minor: backward-compatible feature additions or behavior changes, such as new measurement options, new supported nodes, or new configuration controls that do not break existing setups.
- Major: breaking changes, such as payload format changes, topic changes, pin assignment changes, or workflow changes that require coordinated updates in loggers, analysis scripts, or experiment procedures.

## Release Workflow

1. Update the version numbers in `firmware/firmware_version.h`.
2. Reflash any devices that should move to the new version.
3. Record the firmware version in run notes or experiment logs.
4. Update `CURRENT_STATE.md` if the active flashed baseline changed.

## Scope

- Shared version across:
  - `firmware/wifi_node/wifi_node.ino`
  - `firmware/ble_beacon_node/ble_beacon_node.ino`
  - `firmware/power_node_ina226/power_node_ina226.ino`
  - `firmware/power_node_ina231/power_node_ina231.ino`

- Embedded into MQTT payloads as `fw_version` for Wi-Fi power-node event and power messages.
- Not embedded into BLE advertisement payloads.
- Also exposed through serial boot logs and repository documentation.

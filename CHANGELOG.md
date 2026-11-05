# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.2.1] - 2026-11-05

### Added

- German user guide `docs/ANLEITUNG.md`, linked from the README.
- `PLAYHEAD_SET_COLOUR`, `PLAYHEAD_SET_ALT_COLOUR` and `PLAYHEAD_EMPTY_COLOUR` in `config.py`.

### Fixed

- Steps pad layer: the playhead no longer hides whether the step under it is set. It is white over a set step
  (yellow for white / grey channels) and blue over an empty step; set steps keep the channel colour, empty steps
  stay off / dim-white beat grid. Grey channels' set steps are lit white so they differ from the beat grid.

## [0.2.0] - 2026-11-04

### Added

- Pad layers in the Session layout, cycled with Scene Launch (LED shows the layer):
  - Steps: step sequencer of the selected channel in its colour, beat grid, step pages, moving playhead;
  - Patterns: select and create patterns in their colours, current one pulsing;
  - Channels: select channels, Shift + pad mutes;
  - Mixer: select / mute / solo the bank's tracks (for the 25 / 37 without faders).
- Scene ▲ ▼ navigation per layer (channels, step pages, patterns, banks) with LEDs.
- Drum layout feedback: FPC pad colours or the channel colour, held pads white; notes pass through to FL Studio.
- Device mode: plugin parameters on the pots (and faders in Device fader mode), named parameters in pages of eight,
  Track ◀ ▶ paging, soft takeover, names and values on the screen.
- Device Select: tap opens the plugin window, hold turns the pads into a channel / effect-slot picker,
  Shift + Device Select toggles the pots' Device mode. Device Lock pins the device.
- README feature map of every control, configuration table, model notes and known limitations.

### Changed

- The screen's second row shows the pad page with a compact transport state (`S1-16 PLAY PAT C`).
- Pot and fader moves no longer recompute every LED.

### Fixed

- A Device Select tap opens the plugin window regardless of when the keyboard reports its pad layout change.

## [0.1.0] - 2026-11-04

### Added

- FL Studio device script `Novation Launchkey MK3 (Full)` bound to the Launchkey's DAW port.
- Launchkey MK3 DAW-mode protocol (handshake, mode report/select, pads, pots, faders, buttons, LED palette, LCD).
- Model detection by Device Inquiry (25 / 37 / 49 / 61 / 88) and a `MODEL` override.
- Transport: Play, Stop, Record, Loop, Click, Undo with Shift combos (restart, rewind, step edit, loop record,
  count-in, redo); Capture MIDI (score log) and Quantise.
- Mixer: pots for volume / pan / send A / send B, faders for volume / send A / send B, master fader, banks of eight
  with Track ◀ ▶, fader buttons for mute / solo / select / arm, Arm/Select and Stop/Solo/Mute.
- Soft takeover for pots and faders.
- LED feedback for fader buttons, Arm/Select, Stop/Solo/Mute and Track ◀ ▶; LCD rows, messages and pot / fader labels.
- FL Studio API mock and pytest suite; CI with ruff and pytest on Python 3.9 and 3.12.

[Unreleased]: https://github.com/Sciddie/launchkey-mk3-fl/compare/v0.2.1...HEAD
[0.2.1]: https://github.com/Sciddie/launchkey-mk3-fl/compare/v0.2.0...v0.2.1
[0.2.0]: https://github.com/Sciddie/launchkey-mk3-fl/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/Sciddie/launchkey-mk3-fl/releases/tag/v0.1.0

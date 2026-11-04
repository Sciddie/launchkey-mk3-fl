# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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

[Unreleased]: https://github.com/Sciddie/launchkey-mk3-fl/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/Sciddie/launchkey-mk3-fl/releases/tag/v0.1.0

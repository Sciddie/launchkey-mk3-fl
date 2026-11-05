# Novation Launchkey MK3 — full FL Studio integration

[![CI](https://github.com/Sciddie/launchkey-mk3-fl/actions/workflows/ci.yml/badge.svg)](https://github.com/Sciddie/launchkey-mk3-fl/actions/workflows/ci.yml)

An FL Studio MIDI controller script for the **Novation Launchkey MK3** — made for the **49**, also works with the
25 / 37 / 61 / 88. FL Studio's built-in *Novation Launchkey MK3* support covers transport, mixer volume / pan and drum
pads; this script maps **every control** on the keyboard and keeps LEDs and the screen in sync with FL Studio:
step sequencer with playhead and channel colours, pattern / channel / mixer pads, plugin parameters on the pots with
soft takeover, mute / solo / arm / select on the fader buttons, and names and values on the screen.

> **Status:** feature-complete, tested against a mock of FL Studio's API (see [Testing](#testing)). Not yet tested on
> real hardware in FL Studio — please report anything that behaves differently.

*Deutsch, kurz:* Ordner `src/LaunchkeyMK3Full` nach `Dokumente/Image-Line/FL Studio/Settings/Hardware/` kopieren, in
FL Studio unter *Optionen > MIDI-Einstellungen* den **DAW-Port** (Windows: `MIDIIN2`/`MIDIOUT2`) mit dem Controller-Typ
**Novation Launchkey MK3 (Full)** und gleicher Port-Nummer für Ein- und Ausgang belegen, Easy Start am Keyboard
ausschalten. Die komplette deutsche Bedienungsanleitung steht in **[docs/ANLEITUNG.md](docs/ANLEITUNG.md)**.

## Contents

- [Install](#install) · [Set up in FL Studio](#set-up-in-fl-studio) · [Feature map](#feature-map) ·
  [Feedback](#led-and-screen-feedback) · [Configuration](#configuration) · [Models](#models) ·
  [Known limitations](#known-limitations) · [Testing](#testing) · [Development](#development)

## Install

Requires **FL Studio 20.9.2 or newer** (send levels need 21.2+, see [limitations](#known-limitations)).

1. Download the repository (green *Code* button > *Download ZIP*) or the `LaunchkeyMK3Full` artifact of a CI run, and
   unpack it.
2. Copy the folder **`src/LaunchkeyMK3Full`** — the folder itself, not only its contents — to FL Studio's hardware
   folder:
   - **Windows:** `Documents\Image-Line\FL Studio\Settings\Hardware\`
   - **macOS:** `~/Documents/Image-Line/FL Studio/Settings/Hardware/`

   You should end up with `.../Settings/Hardware/LaunchkeyMK3Full/device_LaunchkeyMK3Full.py` and
   `.../LaunchkeyMK3Full/lkmk3fl/`.
3. Start FL Studio, or in *Options > MIDI settings* click *Update MIDI scripts*.

To update, replace the folder (keep a copy of your `lkmk3fl/config.py` if you changed it).

## Set up in FL Studio

Turn **Easy Start off** on the keyboard first: in Easy Start mode the Launchkey shows up as a USB drive and its DAW
port is not usable. Novation's user guide describes the setting (settings menu, or Novation Components); you only do
this once.

Then open *Options > MIDI settings* (F10). The Launchkey has two USB MIDI ports:

| Port | Windows name | macOS name | Controller type | Port number |
|---|---|---|---|---|
| **DAW port** (input *and* output) | `MIDIIN2 (LKMK3 MIDI)` / `MIDIOUT2 (LKMK3 MIDI)` | `Launchkey MK3 49 LKMK3 DAW In` / `... DAW Out` | **Novation Launchkey MK3 (Full)** | the same number on input and output, e.g. `10` |
| Keys port | `LKMK3 MIDI` / `Launchkey MK3 49` | `Launchkey MK3 49 LKMK3 MIDI In` / `... Out` | *(generic controller)* | another number or none |

1. *Input* list: enable the **DAW** input, select it, set *Controller type* to **Novation Launchkey MK3 (Full)** and
   give it a *Port* number.
2. *Output* list: select the **DAW** output and give it the **same** port number. That is how the script's LED and
   screen messages reach the keyboard.
3. Enable the **keys** input as *(generic controller)*: keys, wheels, sustain and the pads' Drum / Chord layouts
   play the selected channel from there.
4. If FL Studio auto-assigned its built-in *Novation Launchkey MK3* script to the DAW port, replace it with this one.

The screen greets you with `FL Studio / LK MK3 Full 0.2.0` and the Launchkey switches to DAW mode.

## Feature map

Every physical control of the Launchkey MK3 49. **Shift** is a modifier: hold it and press the other control.
"Keyboard" means the Launchkey handles that control itself (FL Studio receives notes / CCs on the keys port).

### Transport and edit buttons

| Control | Press | Shift + press |
|---|---|---|
| **▶ Play** | Play / pause | Stop and play from the start |
| **■ Stop** | Stop | Stop and rewind to the start |
| **● Record** | Record on / off | Step edit on / off |
| **⟲ Loop** | Pattern ⇄ Song mode | Loop recording on / off |
| **Click** | Metronome on / off | Count-in (precount) on / off |
| **Undo** | Undo | Redo |
| **Capture MIDI** | Write the last *n* seconds (default 30) of played notes into the selected pattern (FL Studio's score log) | Clear the score log |
| **Quantise** | Quick-quantise the selected channel's note starts | Quantise starts and lengths |

### Navigation

| Control | Function | Shift + press |
|---|---|---|
| **Track ◀ / ▶** | Select the previous / next mixer track (the bank of eight follows). With the pots in **Device** mode: previous / next parameter page | Move the mixer bank by eight tracks |
| **Scene ▲ / ▼** (left of the pads) | Depends on the pad layer, see below | |
| **► Scene Launch** (right of the top pad row) | Next pad layer: Steps → Patterns → Channels → Mixer | Previous pad layer |
| **Stop/Solo/Mute** (right of the bottom pad row) | Fader buttons: cycle Mute → Solo → Select | Cycle backwards |
| **Device Select** | Tap: open / close the device's plugin window. Hold: the pads become a device picker (see below) | Pots: Device mode ⇄ the previous pot mode |
| **Device Lock** | Lock / unlock the device (pots keep controlling it when you focus something else) | |

### Pads (Session layout)

| Pad layer | Pads | Scene ▲ / ▼ | Shift + Scene ▲ / ▼ | Shift + pad |
|---|---|---|---|---|
| **Steps** (amber ►) | The selected channel's steps 1–16 of the current page: set steps in the channel colour (white for grey channels), empty steps off with a dim-white beat grid; playhead **white over a set step** (yellow if the channel is white/grey), **blue over an empty step** | Previous / next channel | Previous / next step page | Jump to step page *n* |
| **Patterns** (cyan ►) | Patterns of the page in their colours, current one pulsing, dim green = create a new pattern | Previous / next pattern | Previous / next page of 16 | — |
| **Channels** (green ►) | Select channels of the page (channel colours, selected pulsing, muted dim red) | Previous / next page of 16 | Previous / next channel | Mute / unmute the channel |
| **Mixer** (magenta ►) | Top row: select the bank's tracks; bottom row: mute (lit = audible) | Previous / next bank | Previous / next track | Bottom row: solo |

**Drum layout** (chosen on the keyboard): the pads play the selected channel — FL Studio receives the notes (36–51,
FPC's default layout) and records them as usual. The pads light in the FPC's pad colours (or the channel colour) and
white while held.

**Device Select held** (Device Select layout): top row = the eight channels around the selected one (pick one to make
its instrument the device), bottom row = effect slots 1–8 of the selected mixer track (lit cyan when used; pick one to
open it and make it the device). The current device pulses.

Pad, pot and fader *modes* are chosen on the keyboard (Shift + mode pads, see Novation's user guide); the script
follows what the keyboard reports.

### Pots

| Pot mode (keyboard) | Pots 1–8 control |
|---|---|
| **Pan** (default) | Pan of the bank's eight mixer tracks (centre detent at 63/64) |
| **Volume** | Volume of the bank's tracks |
| **Send A / Send B** | Level of the route from each bank track to the Send A / Send B track (default insert 124 / 125) |
| **Device** | Parameters 1–8 of the current page of the device (see [Device mode](#device-mode)) |
| Custom modes | Keyboard (your Components mapping, on the keys port) |

### Faders and fader buttons (49 / 61 / 88)

| Control | Function |
|---|---|
| **Faders 1–8** | Fader mode **Volume** (default) / **Send A** / **Send B** of the bank's tracks, or **Device**: parameters 9–16 of the device page |
| **Master fader** (9th) | Master volume, in every fader mode |
| **Fader buttons 1–8** | Mute (default) / Solo / Select the bank's tracks; record-arm in Arm mode |
| Shift + fader button | Select that track |
| **Arm / Select** | Fader buttons: Arm ⇄ Mute/Solo/Select |

### Controls the keyboard handles itself

| Control | Behaviour |
|---|---|
| 49 keys, pitch wheel, mod wheel, sustain pedal | Played into FL Studio from the keys port (generic controller): the selected channel, recordable |
| Octave − / + (and Shift: transpose) | Keyboard |
| Arp, Scale, Fixed Chord and their Shift settings | Keyboard (generate notes on the keys port) |
| Shift | Modifier for all of the above; the keyboard's own Shift functions (selecting pad / pot / fader modes) keep working |

### Device mode

"The device" is, in this order: the **locked** plugin (Device Lock) → the **focused plugin window** (instrument or
mixer effect) → the one **picked** with Device Select + pad → the **selected channel's** instrument.
Pots 1–8 control its named parameters, eight per page; Track ◀ / ▶ turn pages (the screen shows `Page 2/5`). With
the faders in Device mode, a page is 16 parameters: pots 1–8 and faders 9–16. Values change with soft takeover.

### Soft takeover

Pots and faders only take over a value once they reach it (within 3 steps, or by crossing it), so switching banks,
pages or plugins never makes a value jump. Until then the screen shows `> 50%` (turn right) or `50% <` (turn left).
When something else changes the value (mouse, automation, undo), the control has to pick it up again.

## LED and screen feedback

| Element | Shows |
|---|---|
| Pads | See the pad layers above; refreshed whenever FL Studio changes (steps, colours, patterns, mutes, selection) |
| ► Scene Launch | Pad layer: amber Steps, cyan Patterns, green Channels, magenta Mixer; dim white outside the Session layout |
| Scene ▲ / ▼ | Lit when there is something in that direction |
| Track ◀ / ▶ | Lit when there is a track (or, in Device mode, a parameter page) in that direction |
| Stop/Solo/Mute | Fader-button function: amber Mute, blue Solo, white Select, red Arm |
| Fader buttons | Mute: track colour = audible, dark = muted · Solo: pulsing blue = solo · Select: white = selected · Arm: red = armed, dim red = not armed |
| Arm / Select | Bright in Arm mode |
| Device Select | Bright when there is a device |
| Device Lock | Bright while locked |
| Screen row 1 | Selected channel (Steps / Channels), pattern (Patterns), mixer track (Mixer) or device name (Device mode) |
| Screen row 2 | Pad page and transport, e.g. `S1-16 PLAY PAT C` (C = metronome; `ARM` = record on while stopped); `Dev 2/5 LOCK` in Device mode |
| Pot / fader screen | Name and value of what you move: track name and dB / pan / send %, or parameter name and value |
| Messages | Every button press shows what it did for 1.5 s (also in FL Studio's hint bar) |

Play, Stop, Record, Loop, Click, Undo, Capture MIDI, Quantise and Shift have **no LEDs** on the MK3; their state is
on the screen.

## Configuration

Edit `LaunchkeyMK3Full/lkmk3fl/config.py` in the installed folder, then *Update MIDI scripts*:

| Option | Default | Meaning |
|---|---|---|
| `MODEL` | `None` | Force 25 / 37 / 49 / 61 / 88 instead of auto-detection |
| `SOFT_TAKEOVER`, `PICKUP_THRESHOLD` | `True`, `3` | Soft takeover on / off and its catch range |
| `START_POT_MODE`, `START_FADER_MODE` | `"pan"`, `"volume"` | Modes selected on start |
| `SEND_A_TRACK`, `SEND_B_TRACK` | `-2`, `-1` | Send destinations (negative: counted from the last insert) |
| `SEND_CREATE_ROUTE` | `False` | Create a missing route when you turn a send |
| `MESSAGE_SECONDS` | `1.5` | How long messages stay on screen |
| `CAPTURE_SECONDS` | `30` | Capture MIDI length |
| `QUANTISE_START_ONLY` | `True` | What Quantise does without Shift |
| `STEP_PLAYHEAD` | `True` | Moving playhead on the step pads |
| `PLAYHEAD_SET_COLOUR`, `PLAYHEAD_SET_ALT_COLOUR`, `PLAYHEAD_EMPTY_COLOUR` | `3`, `13`, `46` | Playhead palette colours over a set step (white; yellow for white/grey channels) and over an empty step (blue) |
| `START_PAD_LAYER` | `"steps"` | Pad layer on start |
| `HINTS` | `True` | Mirror messages to FL Studio's hint bar |

## Models

| Model | Detected as | Differences |
|---|---|---|
| Launchkey MK3 25 / 37 | Device Inquiry `34h` / `35h` | No faders or fader buttons: use the pots and the Mixer pad layer for volume / mute / solo |
| **Launchkey MK3 49** | `36h` | Everything above |
| Launchkey MK3 61 | `37h` | Same as the 49 |
| Launchkey 88 MK3 | `40h` | Same as the 49 / 61 |

## Known limitations

- **Not yet tested on hardware or in FL Studio.** Everything is verified against a mock of FL Studio's API built from
  the published API stubs; FL Studio's real behaviour may differ in details (see below).
- **Drum layout port:** Novation's documents differ on whether the Drum layout sends on the DAW port (channel 10)
  or stays on the keys port in DAW mode. On the DAW port the script passes the notes on to FL Studio unhandled (so they
  play and record on the selected channel) and lights the pads; on the keys port FL Studio plays them directly and
  the pads keep the keyboard's own colours. To be confirmed on hardware.
- **Device Select layout:** whether the keyboard switches the pads to its Device Select layout by itself while the
  button is held is unconfirmed; the script requests it explicitly and restores the previous layout on release.
- **Send A / B** need MIDI scripting API 36 (FL Studio 21.2+); older versions show `no send`. Sends move existing
  routes only unless `SEND_CREATE_ROUTE` is on.
- **Plugin parameters:** VST plugins in FL Studio's wrapper can expose thousands of parameters; the script pages
  through the first 4096 *named* ones. Some plugins don't provide value strings (the screen then shows a percentage).
- **White-only LEDs** (Arm/Select, Device Select / Lock, Track and Scene arrows) are driven with the palette's white
  entries on channel 1, as in the reference implementation; brightness levels may look different on the hardware.
- Capture MIDI uses FL Studio's score log (`general.dumpScoreLog`, API 15+), which writes into the selected pattern.
- The Launchkey's custom modes are untouched and stay on the keys port.

## Testing

The script runs unchanged against `tests/flmock/`, a mock of FL Studio's modules (`device`, `transport`, `mixer`,
`channels`, `patterns`, `plugins`, `ui`, `general`, `midi`, ...). `tests/conftest.py` provides a simulated surface:
tests press buttons, turn pots and hit pads with real DAW-port MIDI bytes, then assert FL Studio's state and what the
Launchkey would show (LED colours per pad / button, screen rows, pot / fader labels).

```sh
python -m venv .venv && . .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install pytest ruff
pytest                                            # all tests
ruff check . && ruff format --check .             # lint
```

CI (GitHub Actions) runs ruff and pytest on Python 3.9 (FL Studio 20.9–21) and 3.12 (FL Studio 2024+) and uploads the
script folder as an artifact.

## Development

```
src/LaunchkeyMK3Full/
  device_LaunchkeyMK3Full.py   FL Studio entry point (callbacks)
  lkmk3fl/
    protocol.py   Launchkey MK3 DAW-mode protocol (no FL Studio)
    palette.py    LED palette and colour matching
    host.py       the only module calling FL Studio's API
    core.py       lifecycle, transport, mixer, soft takeover, LED / LCD output
    pads.py       pad layers and drum feedback
    devicemode.py plugin parameters, Device Select / Lock
    controls.py   control targets and soft takeover
    leds.py, display.py   cached LED / LCD output
    config.py     user options
tests/
  flmock/   mock of FL Studio's API modules
```

Commits follow [Conventional Commits](https://www.conventionalcommits.org/), versions [SemVer](https://semver.org/),
changes go into [CHANGELOG.md](CHANGELOG.md). The protocol layer is a port of the Launchkey MK3 protocol code from the
LYNX SHARE integration (`Sciddie/lauchkey-mk3-lynx`); sources: Novation's *Launchkey MK3 Programmer's Reference Guide*
and Image-Line's FL Studio MIDI scripting documentation / API stubs.

## License

MIT, see [LICENSE](LICENSE).

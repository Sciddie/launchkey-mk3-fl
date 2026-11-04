# Novation Launchkey MK3 — full FL Studio integration

[![CI](https://github.com/Sciddie/launchkey-mk3-fl/actions/workflows/ci.yml/badge.svg)](https://github.com/Sciddie/launchkey-mk3-fl/actions/workflows/ci.yml)

An FL Studio MIDI controller script for the **Novation Launchkey MK3** (made for the 49, works with 25 / 37 / 61 / 88).
FL Studio's built-in *Novation Launchkey MK3* support covers transport, mixer volume / pan and drum pads; this script
maps every control on the keyboard and keeps LEDs and the screen in sync with FL Studio.

## Install

Requires FL Studio 20.9.2 or newer (sends need 21.2+, see [limitations](#known-limitations)).

1. Download this repository (green *Code* button > *Download ZIP*, or a release / CI artifact) and unpack it.
2. Copy the folder **`src/LaunchkeyMK3Full`** (the folder itself, not just its contents) to
   - **Windows:** `Documents\Image-Line\FL Studio\Settings\Hardware\`
   - **macOS:** `~/Documents/Image-Line/FL Studio/Settings/Hardware/`

   so that you end up with `.../Settings/Hardware/LaunchkeyMK3Full/device_LaunchkeyMK3Full.py`.
3. Start FL Studio (or *Options > MIDI settings > Update MIDI scripts*).

## Set up in FL Studio

Open *Options > MIDI settings* (F10).

| Port (Input and Output) | Windows name | macOS name | Controller type | Port number |
|---|---|---|---|---|
| **DAW port** | `MIDIIN2 (LKMK3 MIDI)` / `MIDIOUT2 (LKMK3 MIDI)` | `Launchkey MK3 49 LKMK3 DAW In` / `... DAW Out` | **Novation Launchkey MK3 (Full)** | same number for input and output, e.g. 10 |
| Keys port | `LKMK3 MIDI` / `Launchkey MK3 49` | `Launchkey MK3 49 LKMK3 MIDI In` | (generic controller) | another number, or none |

- Enable both inputs. Select the DAW input, pick **Novation Launchkey MK3 (Full)** as *Controller type*, and give it a
  *Port* number; select the DAW **output** and give it the **same** port number — that is how the script's LED and
  screen messages reach the keyboard.
- Disable or change any other script on the DAW port (FL Studio may auto-assign its built-in *Novation Launchkey MK3*).
- The keys, wheels, sustain pedal and the pads' Drum / Chord layouts send on the keys port; leave it on
  *(generic controller)* so FL Studio plays the selected channel.
- **Easy Start mode off:** Launchkeys ship in *Easy Start* (mass-storage) mode, which hides the DAW port. Hold
  **Shift** while powering on (or use Novation Components) and turn *Easy Start* off once.

## Controls

Shift is a modifier: hold it while pressing another control.

### Transport and global buttons

| Control | Press | Shift + press |
|---|---|---|
| ▶ Play | Play / pause | Stop and play from the start |
| ■ Stop | Stop | Stop and rewind to the start |
| ● Record | Record on / off | Step edit on / off |
| ⟲ Loop | Pattern ⇄ Song mode | Loop recording on / off |
| Click | Metronome on / off | Count-in (precount) on / off |
| Undo | Undo | Redo |
| Capture MIDI | Write the last *n* seconds of played notes into the selected pattern (score log) | Clear the score log |
| Quantise | Quick-quantise the selected channel (note starts) | Quantise starts and lengths |

### Mixer

| Control | Function |
|---|---|
| Track ◀ / ▶ | Select the previous / next mixer track; the bank of eight follows |
| Shift + Track ◀ / ▶ | Move the bank by eight tracks |
| Pots 1–8 | Pot mode chosen on the keyboard: **Volume**, **Pan** (default), **Send A**, **Send B** of the bank's tracks |
| Faders 1–8 (49/61/88) | Fader mode: **Volume** (default), **Send A**, **Send B** of the bank's tracks |
| Master fader | Master volume, in every fader mode |
| Fader buttons 1–8 | Mute (default) / Solo / Select the bank's tracks, or record-arm in Arm mode |
| Shift + fader button | Select that track |
| Arm / Select | Fader buttons: Arm ⇄ Mute/Solo/Select |
| Stop/Solo/Mute | Cycle the fader-button function Mute → Solo → Select (Shift: backwards) |

Send A / Send B move the level of the route from each bank track to the tracks set in `config.py`
(default: insert 124 / 125).

Pot, fader and pad modes are chosen on the keyboard itself (Shift + the mode pads, see the Launchkey user guide); the
script follows whatever the keyboard reports.

### Soft takeover

Pots and faders only take over a value once they reach it, so switching banks or modes never makes a value jump. The
screen shows `> value` or `value <` for the direction to move until the control picks up.

## LED and screen feedback

| Element | Shows |
|---|---|
| Fader buttons | Mute mode: track colour = audible, dark = muted; Solo: pulsing blue = solo; Select: white = selected; Arm: red = armed, dim red = not armed |
| Arm / Select | Bright = Arm mode |
| Stop/Solo/Mute | Fader-button function: amber = Mute, blue = Solo, white = Select, red = Arm |
| Track ◀ / ▶ | Lit when there is a track in that direction |
| Screen, row 1 | Selected mixer track |
| Screen, row 2 | `PLAY`/`STOP`, `REC`, `SONG`/`PAT`, `CLK` |
| Pot / fader screen | Name and value of what you move (track names, dB, pan, send level) |

Play, Stop, Record, Loop, Click, Undo, Capture MIDI and Quantise have no LEDs on the MK3; their state is on the screen
and in FL Studio's hint bar.

## Configuration

Edit `LaunchkeyMK3Full/lkmk3fl/config.py` in the installed folder (model override, soft takeover, start modes, send
targets, message time, capture length, quantise variant), then *Update MIDI scripts*.

## Known limitations

- Tested against a mock of FL Studio's API only so far; hardware testing is pending.
- Send levels need FL Studio's MIDI scripting API 36 (FL Studio 21.2 or newer); older versions show "no send".
- FL Studio's volume curve: the screen shows FL Studio's own dB value for the track.

## Development

```sh
python -m venv .venv && . .venv/bin/activate
pip install pytest ruff
pytest            # runs the script against tests/flmock, a mock of FL Studio's API modules
ruff check . && ruff format --check .
```

## License

MIT, see [LICENSE](LICENSE).

import os

import pytest

from conftest import ROOT

with open(os.path.join(ROOT, "README.md"), encoding="utf-8") as f:
    README = f.read()

CONTROLS = [
    "Play",
    "Stop",
    "Record",
    "Loop",
    "Click",
    "Undo",
    "Capture MIDI",
    "Quantise",
    "Track ◀ / ▶",
    "Scene ▲ / ▼",
    "Scene Launch",
    "Stop/Solo/Mute",
    "Device Select",
    "Device Lock",
    "Pots",
    "Faders 1–8",
    "Master fader",
    "Fader buttons 1–8",
    "Arm / Select",
    "Shift",
    "Octave",
    "pitch wheel",
    "mod wheel",
    "sustain",
    "Arp",
    "Scale",
    "Fixed Chord",
    "Drum layout",
    "Steps",
    "Patterns",
    "Channels",
    "Mixer",
]


@pytest.mark.parametrize("control", CONTROLS)
def test_every_control_is_documented(control):
    assert "**" + control in README or control in README


def test_install_steps_cover_windows_and_macos():
    assert "Documents\\Image-Line\\FL Studio\\Settings\\Hardware" in README
    assert "~/Documents/Image-Line/FL Studio/Settings/Hardware" in README
    assert "MIDIIN2" in README and "MIDIOUT2" in README
    assert "Easy Start" in README
    assert "Novation Launchkey MK3 (Full)" in README

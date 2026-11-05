import importlib
import os
import sys

import pytest

TESTS = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(TESTS)
SCRIPT_DIR = os.path.join(ROOT, "src", "LaunchkeyMK3Full")

# The script imports FL Studio's modules by their real names (device, mixer, ...): resolve them to the mock.
for path in (os.path.join(TESTS, "flmock"), TESTS, SCRIPT_DIR):
    if path not in sys.path:
        sys.path.insert(0, path)

from flmock.event import FlMidiMsg  # noqa: E402
from flmock.flstate import state as fl_state  # noqa: E402
from lkmk3fl import protocol as p  # noqa: E402


class FakeClock:
    def __init__(self):
        self.now = 1000.0

    def __call__(self):
        return self.now

    def advance(self, seconds):
        self.now += seconds


class Surface:
    """Drives the device script like the hardware would, and reads back what the hardware would show."""

    def __init__(self, script, clock):
        self.script = script
        self.clock = clock
        self.fl = fl_state

    @property
    def controller(self):
        return self.script._controller

    # --- input
    def midi(self, status, data1, data2):
        ev = FlMidiMsg(status, data1, data2)
        self.script.OnMidiMsg(ev)
        return ev

    def sysex(self, data):
        ev = FlMidiMsg(0xF0, sysex=data)
        self.script.OnSysEx(ev)
        return ev

    def cc16(self, cc, value):
        return self.midi(0xBF, cc, value)

    def press(self, cc, shift=False, channel=16):
        status = 0xBF if channel == 16 else 0xB0
        if shift:
            self.midi(0xB0, p.SHIFT_CC, 127)
        ev = self.midi(status, cc, 127)
        self.midi(status, cc, 0)
        if shift:
            self.midi(0xB0, p.SHIFT_CC, 0)
        return ev

    def press1(self, cc, shift=False):
        return self.press(cc, shift, channel=1)

    def pot(self, index, value):
        return self.cc16(p.POT_FIRST_CC + index, value)

    def fader(self, index, value):
        return self.cc16(p.FADER_FIRST_CC + index, value)

    def sweep_pot(self, index, start, end):
        step = 1 if end >= start else -1
        for v in range(start, end + step, step):
            self.pot(index, v)

    def pad(self, index, velocity=100, shift=False):
        if shift:
            self.midi(0xB0, p.SHIFT_CC, 127)
        note = p.session_pad_note(index)
        ev = self.midi(0x90, note, velocity)
        self.midi(0x80, note, 0)
        if shift:
            self.midi(0xB0, p.SHIFT_CC, 0)
        return ev

    def report_pad_mode(self, mode):
        return self.cc16(p.PAD_MODE_CC, mode)

    def report_pot_mode(self, mode):
        return self.cc16(p.POT_MODE_CC, mode)

    def report_fader_mode(self, mode):
        return self.cc16(p.FADER_MODE_CC, mode)

    def idle(self, seconds=0.0):
        self.clock.advance(seconds)
        self.script.OnIdle()

    def refresh(self, flags=0xFFFF):
        self.script.OnRefresh(flags)

    # --- output
    def led_map(self):
        """Current LED colours as the surface would hold them: {(status & 0xF0 | channel, number): colour}."""
        leds = {}
        for status, d1, d2 in self.fl.midi_out:
            leds[(status, d1)] = d2
        return leds

    def cc_led(self, cc):
        """(colour, lighting) of a CC-addressed LED."""
        return self._led(0xB0, cc)

    def session_led(self, index):
        return self._led(0x90, p.session_pad_note(index))

    def drum_led(self, index):
        return self._led(0x99, p.drum_pad_note(index))

    def devsel_led(self, index):
        return self._led(0x90, p.device_select_pad_note(index))

    def _led(self, base, number):
        last = None
        for status, d1, d2 in self.fl.midi_out:
            if d1 == number and base <= status <= base + 2 and (status & 0xF0) == (base & 0xF0):
                last = (d2, status - base)
        return last

    def lcd_rows(self):
        rows = ["", ""]
        for msg in self.fl.sysex_out:
            if msg[:6] == bytes(p.SYSEX_HEADER) and msg[6] == p.SET_DEFAULT_DISPLAY_CMD:
                rows[msg[7]] = msg[8:-1].decode("latin-1")
            elif msg[:6] == bytes(p.SYSEX_HEADER) and msg[6] == p.CLEAR_DEFAULT_DISPLAY_CMD:
                rows = ["", ""]
        return rows

    def label(self, control, index):
        """(name, value) last sent for a pot ("pot") or fader ("fader")."""
        first = p.POT_DISPLAY_FIRST if control == "pot" else p.FADER_DISPLAY_FIRST
        name = value = None
        for msg in self.fl.sysex_out:
            if msg[:6] != bytes(p.SYSEX_HEADER) or len(msg) < 9 or msg[7] != first + index:
                continue
            if msg[6] == p.SET_PARAM_NAME_CMD:
                name = msg[8:-1].decode("latin-1")
            elif msg[6] == p.SET_PARAM_VALUE_CMD:
                value = msg[8:-1].decode("latin-1")
        return name, value

    def calls(self, name):
        return [c for c in self.fl.calls if c[0] == name]

    def clear_output(self):
        self.fl.midi_out.clear()
        self.fl.sysex_out.clear()
        self.fl.calls.clear()


@pytest.fixture
def fl():
    fl_state.reset()
    return fl_state


@pytest.fixture
def make_surface(fl, monkeypatch):
    """Factory: loads a fresh copy of the device script (after any config tweaks) and runs OnInit."""

    def make(model=0x36, init=True, **config):
        from lkmk3fl import config as cfg

        for k, v in config.items():
            monkeypatch.setattr(cfg, k, v)
        script = importlib.import_module("device_LaunchkeyMK3Full")
        script = importlib.reload(script)
        clock = FakeClock()
        script._controller.clock = clock
        script._controller.display.clock = clock
        s = Surface(script, clock)
        if init:
            script.OnInit()
            if model is not None:
                s.sysex(bytes([0xF0, 0x7E, 0x00, 0x06, 0x02, 0x00, 0x20, 0x29, model, 0x01, 0, 0, 0, 1, 0, 0, 0xF7]))
            s.idle(5.0)  # let the welcome message expire
        return s

    return make


@pytest.fixture
def surface(make_surface):
    return make_surface()

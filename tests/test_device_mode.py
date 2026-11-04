import pytest

from flmock.flstate import Plugin
from lkmk3fl import flconst
from lkmk3fl import palette as pal
from lkmk3fl import protocol as p


def synth(n=20, name="3x Osc"):
    params = [["Param %d" % i, 0.5] for i in range(n)]
    params[3][0] = ""  # unnamed parameters are skipped
    return Plugin(name, params)


@pytest.fixture
def dev(make_surface, fl):
    fl.channels[0].plugin = synth()
    fl.channels[1].plugin = synth(4, "Sytrus")
    fl.tracks[0].slots[0] = synth(10, "Fruity Limiter")
    fl.tracks[2].slots[1] = synth(10, "Fruity Reeverb 2")
    s = make_surface()
    s.report_pot_mode(p.POT_DEVICE)
    return s


def test_device_mode_controls_selected_channel_plugin(dev, fl):
    assert dev.label("pot", 0) == ("Param 0", "50%")
    assert dev.label("pot", 3) == ("Param 4", "50%")  # Param 3 has no name
    dev.pot(0, 64)
    assert fl.channels[0].plugin.params[0][1] == pytest.approx(64 / 127)
    assert dev.label("pot", 0)[1] == "50%"


def test_device_mode_pickup(dev, fl):
    dev.pot(1, 127)
    assert fl.channels[0].plugin.params[1][1] == 0.5
    assert dev.label("pot", 1)[1] == "50% <"


def test_device_name_on_screen(dev, fl):
    dev.idle(5)
    assert dev.lcd_rows() == ["3x Osc", "Dev 1/3"]


def test_track_buttons_page_parameters(dev, fl):
    dev.press(p.TRACK_RIGHT_CC)
    assert dev.label("pot", 0)[0] == "Param 9"
    assert dev.lcd_rows() == ["3x Osc", "Page 2/3"]
    assert fl.selected_track == 0  # not moved
    dev.press(p.TRACK_RIGHT_CC)
    dev.press(p.TRACK_RIGHT_CC)
    assert dev.controller.param_pages[(0, -1)] == 2
    assert dev.label("pot", 2)[0] == "Param 19"
    assert dev.label("pot", 3) == ("-", "")
    assert dev.cc_led(p.TRACK_RIGHT_CC) == (pal.OFF, 0)
    assert dev.cc_led(p.TRACK_LEFT_CC) == (pal.WHITE, 0)
    dev.press(p.TRACK_RIGHT_CC, shift=True)  # Shift: mixer banks as usual
    assert dev.controller.bank_start == 9


def test_faders_in_device_mode_take_the_next_eight(dev, fl):
    dev.report_fader_mode(p.FADER_DEVICE)
    assert dev.label("fader", 0)[0] == "Param 9"
    assert dev.label("fader", 8)[0] == "Master"
    dev.fader(0, 64)
    assert fl.channels[0].plugin.params[9][1] == pytest.approx(64 / 127)


def test_focused_effect_window_becomes_the_device(dev, fl):
    fl.focus_effect(2, 1)
    dev.refresh(flconst.HW_DIRTY_FOCUSED_WINDOW)
    assert dev.lcd_rows() == ["Fruity Reeverb 2", "Page 1/2"]
    dev.pot(0, 64)
    assert fl.tracks[2].slots[1].params[0][1] == pytest.approx(64 / 127)


def test_focused_generator_window(dev, fl):
    fl.focus_generator(1)
    dev.refresh(flconst.HW_DIRTY_FOCUSED_WINDOW)
    assert dev.label("pot", 0)[0] == "Param 0"
    dev.pot(0, 64)
    assert fl.channels[1].plugin.params[0][1] == pytest.approx(64 / 127)
    assert fl.channels[0].plugin.params[0][1] == 0.5


def test_device_lock_keeps_the_device(dev, fl):
    dev.press(p.DEVICE_LOCK_CC)
    assert dev.cc_led(p.DEVICE_LOCK_CC) == (pal.WHITE, 0)
    assert dev.lcd_rows() == ["Locked", "3x Osc"]
    fl.focus_effect(2, 1)
    dev.refresh(flconst.HW_DIRTY_FOCUSED_WINDOW)
    dev.pot(0, 64)
    assert fl.channels[0].plugin.params[0][1] == pytest.approx(64 / 127)
    dev.press(p.DEVICE_LOCK_CC)
    assert dev.cc_led(p.DEVICE_LOCK_CC) == (pal.DIM_WHITE, 0)
    dev.pot(0, 64)
    assert fl.tracks[2].slots[1].params[0][1] == pytest.approx(64 / 127)


def test_no_device(make_surface, fl):
    s = make_surface()
    s.report_pot_mode(p.POT_DEVICE)
    assert s.label("pot", 0)[0] == "No device"
    s.idle(5)
    assert s.lcd_rows()[0] == "No device"
    assert s.cc_led(p.DEVICE_SELECT_CC) == (pal.DIM_WHITE, 0)
    s.press(p.DEVICE_LOCK_CC)
    assert s.lcd_rows() == ["Device Lock", "no device"]
    s.press(p.TRACK_RIGHT_CC)
    assert s.lcd_rows()[0] == "No device"


def test_device_select_tap_opens_the_plugin_window(dev, fl):
    dev.press(p.DEVICE_SELECT_CC)
    assert ("channels.showEditor", 0, -1) in fl.calls
    assert dev.controller.pad_mode == p.PAD_SESSION  # back to the pads' layout


def test_device_select_hold_turns_pads_into_a_picker(dev, fl):
    fl.selected_track = 2
    dev.cc16(p.DEVICE_SELECT_CC, 127)
    assert (0xBF, p.PAD_MODE_CC, p.PAD_DEVICE_SELECT) in fl.midi_out
    assert dev.devsel_led(0)[1] == p.PULSING  # current device: channel 1
    assert dev.devsel_led(3) == (pal.OFF, 0)  # no 4th channel
    assert dev.devsel_led(9) == (pal.DIM_CYAN, 0)  # insert 2, slot 2
    assert dev.devsel_led(8) == (pal.OFF, 0)
    dev.midi(0x90, p.device_select_pad_note(9), 100)
    assert ("mixer.focusEditor", 2, 1) in fl.calls
    dev.midi(0x90, p.device_select_pad_note(8), 100)
    assert dev.lcd_rows() == ["Slot 1", "empty"]
    dev.cc16(p.DEVICE_SELECT_CC, 0)
    assert dev.controller.pad_mode == p.PAD_SESSION
    assert (0xBF, p.PAD_MODE_CC, p.PAD_SESSION) in fl.midi_out[-60:]
    assert not any(c[0] == "channels.showEditor" for c in fl.calls)  # a used hold is not a tap
    dev.pot(0, 64)
    assert fl.tracks[2].slots[1].params[0][1] == pytest.approx(64 / 127)


def test_device_select_pad_picks_channel(dev, fl):
    dev.cc16(p.DEVICE_SELECT_CC, 127)
    dev.midi(0x90, p.device_select_pad_note(1), 100)
    dev.cc16(p.DEVICE_SELECT_CC, 0)
    assert fl.selected_channel == 1
    assert dev.label("pot", 3)[0] == "-"  # Sytrus mock: Param 0, 1, 2 (3 unnamed)
    dev.pot(0, 64)
    assert fl.channels[1].plugin.params[0][1] == pytest.approx(64 / 127)


def test_shift_device_select_toggles_pot_device_mode(make_surface, fl):
    fl.channels[0].plugin = synth()
    s = make_surface()
    s.press(p.DEVICE_SELECT_CC, shift=True)
    assert (0xBF, p.POT_MODE_CC, p.POT_DEVICE) in fl.midi_out
    assert s.controller.pot_mode == p.POT_DEVICE
    s.press(p.DEVICE_SELECT_CC, shift=True)
    assert s.controller.pot_mode == p.POT_PAN


def test_parameter_changes_in_fl_release_pickup(dev, fl):
    dev.pot(0, 64)
    fl.channels[0].plugin.params[0][1] = 0.9
    dev.pot(0, 66)
    assert fl.channels[0].plugin.params[0][1] == 0.9


def test_plugin_param_cache_refreshes(dev, fl):
    fl.channels[0].plugin.params[3][0] = "Cutoff"
    dev.refresh(0)
    assert dev.label("pot", 3)[0] == "Param 4"  # cached
    dev.refresh(flconst.HW_DIRTY_NAMES)
    assert dev.label("pot", 3)[0] == "Cutoff"

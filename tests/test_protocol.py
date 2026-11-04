import pytest

from lkmk3fl import protocol as p


@pytest.mark.parametrize(
    "cc,name",
    [
        (115, p.PLAY),
        (116, p.STOP),
        (117, p.RECORD),
        (118, p.LOOP),
        (74, p.CAPTURE_MIDI),
        (75, p.QUANTISE),
        (76, p.CLICK),
        (77, p.UNDO),
        (102, p.TRACK_LEFT),
        (103, p.TRACK_RIGHT),
        (106, p.SCENE_UP),
        (107, p.SCENE_DOWN),
        (45, p.ARM_SELECT),
        (51, p.DEVICE_SELECT),
        (52, p.DEVICE_LOCK),
    ],
)
def test_channel16_buttons(cc, name):
    e = p.decode(0xBF, cc, 127)
    assert (e.kind, e.button, e.pressed) == ("button", name, True)
    assert not p.decode(0xBF, cc, 0).pressed


@pytest.mark.parametrize("cc,name", [(104, p.SCENE_LAUNCH), (105, p.STOP_SOLO_MUTE), (108, p.SHIFT)])
def test_channel1_buttons(cc, name):
    e = p.decode(0xB0, cc, 127)
    assert (e.kind, e.button) == ("button", name)


def test_scene_alias_echoes_are_ignored():
    assert p.decode(0xBF, 104, 127).kind == "none"
    assert p.decode(0xBF, 105, 127).kind == "none"


def test_pots_faders_and_fader_buttons():
    assert p.decode(0xBF, 21, 64) == p.Event("pot", index=0, value=64)
    assert p.decode(0xBF, 28, 1) == p.Event("pot", index=7, value=1)
    assert p.decode(0xBF, 53, 100) == p.Event("fader", index=0, value=100)
    assert p.decode(0xBF, 61, 127) == p.Event("fader", index=8, value=127)
    e = p.decode(0xBF, 44, 127)
    assert (e.kind, e.button, e.index) == ("button", p.FADER_BUTTON, 7)


def test_touch_events_on_channel15():
    assert p.decode(0xBE, 22, 127) == p.Event("pot_touch", index=1, value=127, pressed=True)
    assert p.decode(0xBE, 61, 0) == p.Event("fader_touch", index=8, value=0, pressed=False)


def test_mode_reports():
    assert p.decode(0xBF, 3, p.PAD_DRUM) == p.Event("pad_mode", value=1)
    assert p.decode(0xBF, 9, p.POT_DEVICE) == p.Event("pot_mode", value=2)
    assert p.decode(0xBF, 10, p.FADER_SEND_B) == p.Event("fader_mode", value=5)


def test_session_pads():
    assert p.decode(0x90, 96, 100) == p.Event("pad", index=0, value=100, note=96, pressed=True)
    assert p.decode(0x90, 119, 1).index == 15
    assert not p.decode(0x90, 96, 0).pressed  # note on velocity 0 = release
    assert not p.decode(0x80, 96, 64).pressed
    assert p.decode(0xA0, 112, 50).kind == "pad_pressure"


def test_device_select_and_drum_pads():
    assert p.decode(0x90, 64, 1).kind == "device_select_pad"
    assert p.decode(0x90, 87, 1).index == 15
    e = p.decode(0x99, 36, 90)
    assert (e.kind, e.index, e.note) == ("drum_pad", 8, 36)
    assert p.decode(0xA9, 40, 3).kind == "drum_pressure"
    assert p.decode(0x99, 60, 90).kind == "none"


def test_pad_note_round_trip():
    for i in range(16):
        assert p.session_pad_index(p.session_pad_note(i)) == i
        assert p.device_select_pad_index(p.device_select_pad_note(i)) == i
        assert p.drum_pad_index(p.drum_pad_note(i)) == i


def test_unrelated_messages_decode_to_none():
    assert p.decode(0xB0, 1, 64).kind == "none"  # mod wheel on the keys channel
    assert p.decode(0xE0, 0, 64).kind == "none"
    assert p.decode(0x91, 96, 1).kind == "none"


def test_device_inquiry_reply():
    reply = bytes([0xF0, 0x7E, 0x00, 0x06, 0x02, 0x00, 0x20, 0x29, 0x36, 0x01, 0, 0, 0, 2, 0, 0, 0xF7])
    e = p.decode_sysex(reply)
    assert (e.kind, e.value, e.pressed) == ("device_inquiry", 0x36, True)
    assert p.model_name(e.value) == "Launchkey MK3 49"
    assert p.has_faders(0x36) and p.has_faders(0x40) and not p.has_faders(0x34)
    assert p.decode_sysex(bytes([0xF0, 0x01, 0xF7])).kind == "none"


def test_handshake_messages():
    assert p.daw_mode(True) == (0x9F, 0x0C, 0x7F)
    assert p.daw_mode(False) == (0x9F, 0x0C, 0x00)
    assert p.touch_events(True) == (0x9F, 0x0B, 0x7F)
    assert p.pad_mode(p.PAD_SESSION) == (0xBF, 0x03, 0x02)
    assert p.pot_mode(p.POT_PAN) == (0xBF, 0x09, 0x03)
    assert p.fader_mode(p.FADER_VOLUME) == (0xBF, 0x0A, 0x01)
    assert p.device_inquiry() == bytes([0xF0, 0x7E, 0x7F, 0x06, 0x01, 0xF7])


def test_led_messages():
    assert p.session_pad_led(0, 5) == (0x90, 96, 5)
    assert p.session_pad_led(15, 5, p.PULSING) == (0x92, 119, 5)
    assert p.drum_pad_led(8, 21, p.FLASHING) == (0x9A, 36, 21)
    assert p.device_select_pad_led(0, 3) == (0x90, 64, 3)
    assert p.cc_led(p.SCENE_LAUNCH_CC, 9) == (0xB0, 104, 9)


def test_display_text():
    assert p.display_text("Hello") == b"Hello"
    assert p.display_text("x" * 20) == b"x" * 16
    assert p.display_text("90\u00b0") == bytes([0x39, 0x30, 0x11, 0x30])
    assert p.display_text("Gr\u00fc\u00dfe") == b"Gruesse"
    assert p.display_text("a\u4e00b") == b"a?b"
    assert p.display_text("a\nb") == b"ab"
    assert len(p.display_text("\u00e4" * 10)) == 16


def test_lcd_sysex():
    assert p.set_default_display(0, "FL") == bytes([0xF0, 0, 0x20, 0x29, 2, 0x0F, 4, 0, 0x46, 0x4C, 0xF7])
    assert p.set_default_display(5, "")[7] == 1
    assert p.clear_default_display() == bytes([0xF0, 0, 0x20, 0x29, 2, 0x0F, 6, 0xF7])
    assert p.set_pot_name(0, "Vol")[6:8] == bytes([7, 0x38])
    assert p.set_pot_value(7, "1")[6:8] == bytes([8, 0x3F])
    assert p.set_fader_name(8, "Master")[6:8] == bytes([7, 0x58])
    assert p.set_fader_value(0, "0dB")[6:8] == bytes([8, 0x50])


def test_to_hex():
    assert p.to_hex((0x9F, 0x0C, 0x7F)) == "9F 0C 7F"

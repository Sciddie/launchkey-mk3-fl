"""Launchkey MK3 DAW-mode protocol: decode what the surface sends on its DAW port, encode what the host sends back.

Source of truth: Novation, "Launchkey MK3 Programmer's reference manual" (chapters "DAW mode", "Colouring the
surface", "Controlling the screen"). Ported from the C++ protocol layer of the LYNX SHARE integration
(``lkmk3::proto`` / ``lkmk3::encode``). This module knows nothing about FL Studio: raw MIDI in, typed events out;
typed commands in, raw bytes out. Channel numbers in the comments are 1-based like the manual's; the status nibble is
``channel - 1``.
"""

NOTE_OFF = 0x80
NOTE_ON = 0x90
POLY_PRESSURE = 0xA0
CONTROL_CHANGE = 0xB0
SYSEX_START = 0xF0
SYSEX_END = 0xF7

CH1 = 0x0
CH10 = 0x9
CH15 = 0xE
CH16 = 0xF

# --- DAW mode control: Note On / Off on channel 16 ---
DAW_MODE_NOTE = 0x0C  # 12: DAW mode enable / disable
TOUCH_EVENTS_NOTE = 0x0B  # 11: continuous-control Touch events
POT_PICKUP_NOTE = 0x0A  # 10: continuous-control Pot Pickup (done in the script instead, see controls.py)

# --- mode report / select: CC on channel 16 ---
PAD_MODE_CC = 0x03
POT_MODE_CC = 0x09
FADER_MODE_CC = 0x0A

# --- surface CCs in DAW mode, channel 16 ---
POT_FIRST_CC = 0x15  # 21..28
FADER_FIRST_CC = 0x35  # 53..60; 61 = master fader (49 / 61 / 88)
MASTER_FADER_CC = 0x3D
FADER_BUTTON_FIRST_CC = 0x25  # 37..44 (49 / 61 / 88)
ARM_SELECT_CC = 0x2D  # 45
DEVICE_SELECT_CC = 0x33  # 51
DEVICE_LOCK_CC = 0x34  # 52
CAPTURE_MIDI_CC = 0x4A  # 74
QUANTISE_CC = 0x4B  # 75
CLICK_CC = 0x4C  # 76
UNDO_CC = 0x4D  # 77
TRACK_LEFT_CC = 0x66  # 102
TRACK_RIGHT_CC = 0x67  # 103
SCENE_UP_ALIAS_CC = 0x68  # 104 on ch16: Launchkey Mini MK3 compatibility echo of Scene Up (ignored)
SCENE_DOWN_ALIAS_CC = 0x69  # 105 on ch16: echo of Scene Down (ignored)
SCENE_UP_CC = 0x6A  # 106
SCENE_DOWN_CC = 0x6B  # 107
PLAY_CC = 0x73  # 115
STOP_CC = 0x74  # 116
RECORD_CC = 0x75  # 117
LOOP_CC = 0x76  # 118
# --- channel 1 ---
SCENE_LAUNCH_CC = 0x68  # 104: the > right of the top pad row (RGB LED)
STOP_SOLO_MUTE_CC = 0x69  # 105: right of the bottom pad row (RGB LED)
SHIFT_CC = 0x6C  # 108

# --- pad notes ---
SESSION_TOP_FIRST = 0x60  # ch1: 96..103
SESSION_BOTTOM_FIRST = 0x70  # ch1: 112..119
DEVICE_SELECT_TOP_FIRST = 0x40  # ch1: 64..71
DEVICE_SELECT_BOTTOM_FIRST = 0x50  # ch1: 80..87
# Drum layout (ch10): pad index 0..7 = top row, 8..15 = bottom row.
DRUM_NOTES = (40, 41, 42, 43, 48, 49, 50, 51, 36, 37, 38, 39, 44, 45, 46, 47)

# --- LCD ---
SYSEX_HEADER = (0xF0, 0x00, 0x20, 0x29, 0x02, 0x0F)
SET_DEFAULT_DISPLAY_CMD = 0x04
CLEAR_DEFAULT_DISPLAY_CMD = 0x06
SET_PARAM_NAME_CMD = 0x07
SET_PARAM_VALUE_CMD = 0x08
POT_DISPLAY_FIRST = 0x38  # 56..63
FADER_DISPLAY_FIRST = 0x50  # 80..88 (88 = master fader)
DISPLAY_COLUMNS = 16

PAD_COUNT = 16
POT_COUNT = 8
FADER_COUNT = 8  # plus the master fader (index 8)

# Modes the surface reports (CC 3 / 9 / 10 on channel 16) and the host may select.
PAD_CUSTOM0 = 0
PAD_DRUM = 1
PAD_SESSION = 2
PAD_SCALE_CHORDS = 3
PAD_USER_CHORDS = 4
PAD_DEVICE_SELECT = 9
PAD_NAVIGATION = 10

POT_CUSTOM0 = 0
POT_VOLUME = 1
POT_DEVICE = 2
POT_PAN = 3
POT_SEND_A = 4
POT_SEND_B = 5

FADER_CUSTOM0 = 0
FADER_VOLUME = 1
FADER_DEVICE = 2
FADER_SEND_A = 4
FADER_SEND_B = 5

# LED lighting: the channel offset added to the stationary channel.
STATIONARY = 0
FLASHING = 1
PULSING = 2

# Device Inquiry reply device types.
MODELS = {
    0x34: "Launchkey MK3 25",
    0x35: "Launchkey MK3 37",
    0x36: "Launchkey MK3 49",
    0x37: "Launchkey MK3 61",
    0x40: "Launchkey MK3 88",
}
MODELS_WITH_FADERS = (0x36, 0x37, 0x40)

# Button identifiers (strings keep tests and logs readable).
PLAY = "play"
STOP = "stop"
RECORD = "record"
LOOP = "loop"
CAPTURE_MIDI = "capture_midi"
QUANTISE = "quantise"
CLICK = "click"
UNDO = "undo"
TRACK_LEFT = "track_left"
TRACK_RIGHT = "track_right"
SCENE_UP = "scene_up"
SCENE_DOWN = "scene_down"
SCENE_LAUNCH = "scene_launch"
STOP_SOLO_MUTE = "stop_solo_mute"
SHIFT = "shift"
DEVICE_SELECT = "device_select"
DEVICE_LOCK = "device_lock"
ARM_SELECT = "arm_select"
FADER_BUTTON = "fader_button"

_CH16_BUTTONS = {
    ARM_SELECT_CC: ARM_SELECT,
    DEVICE_SELECT_CC: DEVICE_SELECT,
    DEVICE_LOCK_CC: DEVICE_LOCK,
    CAPTURE_MIDI_CC: CAPTURE_MIDI,
    QUANTISE_CC: QUANTISE,
    CLICK_CC: CLICK,
    UNDO_CC: UNDO,
    TRACK_LEFT_CC: TRACK_LEFT,
    TRACK_RIGHT_CC: TRACK_RIGHT,
    SCENE_UP_CC: SCENE_UP,
    SCENE_DOWN_CC: SCENE_DOWN,
    PLAY_CC: PLAY,
    STOP_CC: STOP,
    RECORD_CC: RECORD,
    LOOP_CC: LOOP,
}
_CH1_BUTTONS = {SCENE_LAUNCH_CC: SCENE_LAUNCH, STOP_SOLO_MUTE_CC: STOP_SOLO_MUTE, SHIFT_CC: SHIFT}

# Where each button's LED lives (CC number, channel-1 palette addressing). Only these buttons have LEDs on the MK3:
# Play / Stop / Record / Loop / Capture / Quantise / Click / Undo / Shift have none.
BUTTON_LED_CC = {
    SCENE_LAUNCH: SCENE_LAUNCH_CC,
    STOP_SOLO_MUTE: STOP_SOLO_MUTE_CC,
    ARM_SELECT: ARM_SELECT_CC,
    DEVICE_SELECT: DEVICE_SELECT_CC,
    DEVICE_LOCK: DEVICE_LOCK_CC,
    TRACK_LEFT: TRACK_LEFT_CC,
    TRACK_RIGHT: TRACK_RIGHT_CC,
    SCENE_UP: SCENE_UP_CC,
    SCENE_DOWN: SCENE_DOWN_CC,
}


class Event:
    """One decoded message from the surface.

    ``kind`` is one of: ``"none"``, ``"button"``, ``"pot"``, ``"fader"``, ``"pot_touch"``, ``"fader_touch"``,
    ``"pad"`` (Session layout), ``"pad_pressure"``, ``"drum_pad"``, ``"drum_pressure"``, ``"device_select_pad"``,
    ``"pad_mode"``, ``"pot_mode"``, ``"fader_mode"``, ``"device_inquiry"``.
    """

    __slots__ = ("kind", "button", "index", "value", "note", "pressed")

    def __init__(self, kind="none", button=None, index=0, value=0, note=0, pressed=False):
        self.kind = kind
        self.button = button
        self.index = index
        self.value = value
        self.note = note
        self.pressed = pressed

    def __eq__(self, other):
        return isinstance(other, Event) and all(getattr(self, s) == getattr(other, s) for s in self.__slots__)

    def __repr__(self):
        return "Event(" + ", ".join(s + "=" + repr(getattr(self, s)) for s in self.__slots__) + ")"


NONE = Event()


def _button(name, value, index=0):
    return Event("button", button=name, index=index, value=value, pressed=value > 0)


def session_pad_index(note):
    """Pad index 0..15 (0..7 top row, 8..15 bottom row) of a Session-layout note, -1 when outside."""
    if SESSION_TOP_FIRST <= note < SESSION_TOP_FIRST + 8:
        return note - SESSION_TOP_FIRST
    if SESSION_BOTTOM_FIRST <= note < SESSION_BOTTOM_FIRST + 8:
        return 8 + note - SESSION_BOTTOM_FIRST
    return -1


def device_select_pad_index(note):
    if DEVICE_SELECT_TOP_FIRST <= note < DEVICE_SELECT_TOP_FIRST + 8:
        return note - DEVICE_SELECT_TOP_FIRST
    if DEVICE_SELECT_BOTTOM_FIRST <= note < DEVICE_SELECT_BOTTOM_FIRST + 8:
        return 8 + note - DEVICE_SELECT_BOTTOM_FIRST
    return -1


def drum_pad_index(note):
    try:
        return DRUM_NOTES.index(note)
    except ValueError:
        return -1


def session_pad_note(index):
    index = max(0, min(15, index))
    return SESSION_TOP_FIRST + index if index < 8 else SESSION_BOTTOM_FIRST + index - 8


def device_select_pad_note(index):
    index = max(0, min(15, index))
    return DEVICE_SELECT_TOP_FIRST + index if index < 8 else DEVICE_SELECT_BOTTOM_FIRST + index - 8


def drum_pad_note(index):
    return DRUM_NOTES[max(0, min(15, index))]


def _decode_cc16(cc, value):
    if POT_FIRST_CC <= cc < POT_FIRST_CC + POT_COUNT:
        return Event("pot", index=cc - POT_FIRST_CC, value=value)
    if FADER_FIRST_CC <= cc <= MASTER_FADER_CC:
        return Event("fader", index=cc - FADER_FIRST_CC, value=value)
    if FADER_BUTTON_FIRST_CC <= cc < FADER_BUTTON_FIRST_CC + FADER_COUNT:
        return _button(FADER_BUTTON, value, cc - FADER_BUTTON_FIRST_CC)
    if cc == PAD_MODE_CC:
        return Event("pad_mode", value=value)
    if cc == POT_MODE_CC:
        return Event("pot_mode", value=value)
    if cc == FADER_MODE_CC:
        return Event("fader_mode", value=value)
    name = _CH16_BUTTONS.get(cc)
    if name is not None:
        return _button(name, value)
    # 104 / 105 on channel 16 echo Scene Up / Down (the surface also sends 106 / 107): acting on both would move twice.
    return NONE


def _decode_note(channel, note, velocity, on):
    pressed = on and velocity > 0
    if channel == CH1:
        i = session_pad_index(note)
        if i >= 0:
            return Event("pad", index=i, value=velocity, note=note, pressed=pressed)
        i = device_select_pad_index(note)
        if i >= 0:
            return Event("device_select_pad", index=i, value=velocity, note=note, pressed=pressed)
    if channel == CH10:
        i = drum_pad_index(note)
        if i >= 0:
            return Event("drum_pad", index=i, value=velocity, note=note, pressed=pressed)
    return NONE


def decode_sysex(data):
    """Decodes a complete SysEx message (F0 .. F7)."""
    d = list(data)
    # Universal Device Inquiry reply: F0 7E <id> 06 02 00 20 29 <dev_type> <01|11> 00 00 <4 version bytes> F7
    if len(d) >= 17 and d[1] == 0x7E and d[3:8] == [0x06, 0x02, 0x00, 0x20, 0x29]:
        return Event("device_inquiry", value=d[8], pressed=d[9] == 0x01)
    return NONE


def decode(status, data1=0, data2=0):
    """Decodes one short MIDI message (status byte incl. channel, two data bytes)."""
    kind = status & 0xF0
    channel = status & 0x0F
    data1 &= 0x7F
    data2 &= 0x7F
    if kind == NOTE_ON:
        return _decode_note(channel, data1, data2, True)
    if kind == NOTE_OFF:
        return _decode_note(channel, data1, 0, False)
    if kind == POLY_PRESSURE:
        e = _decode_note(channel, data1, data2, True)
        if e.kind == "pad":
            e.kind = "pad_pressure"
        elif e.kind == "drum_pad":
            e.kind = "drum_pressure"
        else:
            return NONE
        e.pressed = False
        return e
    if kind == CONTROL_CHANGE:
        if channel == CH16:
            return _decode_cc16(data1, data2)
        if channel == CH1:
            name = _CH1_BUTTONS.get(data1)
            return _button(name, data2) if name else NONE
        if channel == CH15:  # Touch On (127) / Off (0), when enabled
            if POT_FIRST_CC <= data1 < POT_FIRST_CC + POT_COUNT:
                return Event("pot_touch", index=data1 - POT_FIRST_CC, value=data2, pressed=data2 > 0)
            if FADER_FIRST_CC <= data1 <= MASTER_FADER_CC:
                return Event("fader_touch", index=data1 - FADER_FIRST_CC, value=data2, pressed=data2 > 0)
    return NONE


# ----------------------------------------------------------------------------------------------------------------
# Encoding. Short messages are (status, data1, data2) tuples; SysEx messages are bytes.


def daw_mode(on):
    return (NOTE_ON | CH16, DAW_MODE_NOTE, 0x7F if on else 0x00)


def touch_events(on):
    return (NOTE_ON | CH16, TOUCH_EVENTS_NOTE, 0x7F if on else 0x00)


def pot_pickup(on):
    return (NOTE_ON | CH16, POT_PICKUP_NOTE, 0x7F if on else 0x00)


def pad_mode(mode):
    return (CONTROL_CHANGE | CH16, PAD_MODE_CC, mode & 0x7F)


def pot_mode(mode):
    return (CONTROL_CHANGE | CH16, POT_MODE_CC, mode & 0x7F)


def fader_mode(mode):
    return (CONTROL_CHANGE | CH16, FADER_MODE_CC, mode & 0x7F)


def session_pad_led(index, colour, lighting=STATIONARY):
    return (NOTE_ON | (CH1 + lighting), session_pad_note(index), colour & 0x7F)


def device_select_pad_led(index, colour, lighting=STATIONARY):
    return (NOTE_ON | (CH1 + lighting), device_select_pad_note(index), colour & 0x7F)


def drum_pad_led(index, colour, lighting=STATIONARY):
    return (NOTE_ON | (CH10 + lighting), drum_pad_note(index), colour & 0x7F)


def cc_led(cc, colour, lighting=STATIONARY):
    """Palette colour on a CC-addressed LED (buttons; white-only LEDs use the palette's white entries 0..3)."""
    return (CONTROL_CHANGE | (CH1 + lighting), cc & 0x7F, colour & 0x7F)


def device_inquiry():
    return bytes((0xF0, 0x7E, 0x7F, 0x06, 0x01, 0xF7))


def display_text(text, max_columns=DISPLAY_COLUMNS):
    """The bytes the device shows for ``text``: printable ASCII; '°' via the ISO-8859-2 escape (11h 30h); German
    umlauts and sharp s transliterated; anything else becomes '?'. Truncated to ``max_columns`` columns."""
    out = []
    columns = 0
    for ch in str(text):
        if columns >= max_columns:
            break
        cp = ord(ch)
        if 0x20 <= cp <= 0x7E:
            out.append(cp)
        elif ch == "\u00b0":
            out.extend((0x11, 0x30))
        elif ch == "\t":
            out.append(0x20)
        elif ch in _TRANSLIT:
            for c in _TRANSLIT[ch]:
                if columns >= max_columns:
                    break
                out.append(ord(c))
                columns += 1
            continue
        elif cp < 0x20:
            continue
        else:
            out.append(ord("?"))
        columns += 1
    return bytes(out)


_TRANSLIT = {
    "\u00e4": "ae",
    "\u00f6": "oe",
    "\u00fc": "ue",
    "\u00c4": "Ae",
    "\u00d6": "Oe",
    "\u00dc": "Ue",
    "\u00df": "ss",
    "\u00e9": "e",
    "\u00e8": "e",
    "\u00e0": "a",
    "\u2013": "-",
    "\u2014": "-",
    "\u2192": ">",
    "\u2190": "<",
}


def _sysex(command, args, tail=b""):
    return bytes(SYSEX_HEADER) + bytes([command]) + bytes(args) + bytes(tail) + bytes([SYSEX_END])


def set_default_display(row, text):
    return _sysex(SET_DEFAULT_DISPLAY_CMD, [max(0, min(1, row))], display_text(text))


def clear_default_display():
    return _sysex(CLEAR_DEFAULT_DISPLAY_CMD, [])


def set_pot_name(pot, text):
    return _sysex(SET_PARAM_NAME_CMD, [POT_DISPLAY_FIRST + max(0, min(7, pot))], display_text(text))


def set_pot_value(pot, text):
    return _sysex(SET_PARAM_VALUE_CMD, [POT_DISPLAY_FIRST + max(0, min(7, pot))], display_text(text))


def set_fader_name(fader, text):
    return _sysex(SET_PARAM_NAME_CMD, [FADER_DISPLAY_FIRST + max(0, min(8, fader))], display_text(text))


def set_fader_value(fader, text):
    return _sysex(SET_PARAM_VALUE_CMD, [FADER_DISPLAY_FIRST + max(0, min(8, fader))], display_text(text))


def model_name(device_type):
    return MODELS.get(device_type, "")


def has_faders(device_type):
    return device_type in MODELS_WITH_FADERS


def to_hex(message):
    return " ".join(f"{b:02X}" for b in message)

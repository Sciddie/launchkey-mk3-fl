"""The Launchkey MK3 controller: turns decoded surface events into FL Studio actions and FL Studio's state into LED
and LCD feedback. The FL Studio callbacks in ``device_LaunchkeyMK3Full.py`` forward to one ``Controller``
(controller.py), which adds the pad and device layers on top of this core.
"""

from lkmk3fl import config, host
from lkmk3fl import palette as pal
from lkmk3fl import protocol as p
from lkmk3fl.controls import NoTarget, Pickup, TrackPan, TrackSend, TrackVolume
from lkmk3fl.display import Display
from lkmk3fl.leds import LedCache, LedState
from lkmk3fl.version import VERSION

try:
    import time

    _clock = time.monotonic
except Exception:  # pragma: no cover - FL Studio always ships time; keep the script alive regardless
    _ticks = [0.0]

    def _clock():
        _ticks[0] += 0.02
        return _ticks[0]


BANK_SIZE = 8

POT_MODE_NAMES = {
    p.POT_VOLUME: "Volume",
    p.POT_DEVICE: "Device",
    p.POT_PAN: "Pan",
    p.POT_SEND_A: "Send A",
    p.POT_SEND_B: "Send B",
}
FADER_MODE_NAMES = {
    p.FADER_VOLUME: "Volume",
    p.FADER_DEVICE: "Device",
    p.FADER_SEND_A: "Send A",
    p.FADER_SEND_B: "Send B",
}
_POT_MODE_BY_NAME = {
    "volume": p.POT_VOLUME,
    "device": p.POT_DEVICE,
    "pan": p.POT_PAN,
    "send_a": p.POT_SEND_A,
    "send_b": p.POT_SEND_B,
}
_FADER_MODE_BY_NAME = {
    "volume": p.FADER_VOLUME,
    "device": p.FADER_DEVICE,
    "send_a": p.FADER_SEND_A,
    "send_b": p.FADER_SEND_B,
}
_MODEL_BY_KEYS = {25: 0x34, 37: 0x35, 49: 0x36, 61: 0x37, 88: 0x40}

# Fader-button functions, cycled with Stop/Solo/Mute (Arm/Select switches to arm and back).
FADER_BUTTON_FUNCTIONS = ("mute", "solo", "select")
FADER_BUTTON_FUNCTION_COLOURS = {"mute": pal.AMBER, "solo": pal.BLUE, "select": pal.WHITE}


class CoreController:
    def __init__(self, clock=None):
        self.clock = clock or _clock
        self.leds = LedCache()
        self.display = Display(self.clock)
        self.pot_pickups = [Pickup() for _ in range(p.POT_COUNT)]
        self.fader_pickups = [Pickup() for _ in range(p.FADER_COUNT + 1)]
        self.reset_state()

    def reset_state(self):
        self.active = False
        self.shift = False
        self.model = _MODEL_BY_KEYS.get(config.MODEL, 0x36)
        self.model_detected = config.MODEL is not None
        self.pad_mode = p.PAD_SESSION
        self.pot_mode = _POT_MODE_BY_NAME.get(config.START_POT_MODE, p.POT_PAN)
        self.fader_mode = _FADER_MODE_BY_NAME.get(config.START_FADER_MODE, p.FADER_VOLUME)
        self.bank_start = 1
        self.arm_mode = False
        self.fader_button_function = "mute"
        for pk in self.pot_pickups + self.fader_pickups:
            pk.reset()

    # ------------------------------------------------------------------------------------------------ lifecycle

    @property
    def has_faders(self):
        return p.has_faders(self.model)

    def init(self):
        self.reset_state()
        self.leds.forget()
        self.display.forget()
        if not host.is_output_assigned():
            host.hint("Launchkey MK3: set the MIDI output port number to the input's (DAW port)")
        host.send(p.daw_mode(True))
        host.send_sysex(p.device_inquiry())
        host.send(p.pad_mode(p.PAD_SESSION))
        host.send(p.pot_mode(self.pot_mode))
        host.send(p.fader_mode(self.fader_mode))
        self.active = True
        self.display.show_message("FL Studio", "LK MK3 Full " + VERSION, 2.0)
        self.refresh()

    def deinit(self):
        if not self.active:
            return
        self.leds.clear_all(self._all_led_addresses())
        self.display.clear()
        host.send(p.daw_mode(False))  # back to Standalone (MIDI) mode, which restores its own LEDs and screen
        self.active = False

    def _all_led_addresses(self):
        addrs = [("cc", cc) for cc in p.BUTTON_LED_CC.values()]
        addrs += [("cc", p.FADER_BUTTON_FIRST_CC + i) for i in range(p.FADER_COUNT)]
        addrs += [("session", i) for i in range(p.PAD_COUNT)]
        return addrs

    # ------------------------------------------------------------------------------------------------ MIDI in

    def on_midi(self, status, data1, data2):
        """Handles one short message from the DAW port. Returns True when the script consumed it."""
        e = p.decode(status, data1, data2)
        if e.kind == "none":
            return False
        return self.on_event(e)

    def on_sysex(self, data):
        e = p.decode_sysex(data)
        if e.kind == "device_inquiry":
            if config.MODEL is None and e.value in p.MODELS:
                self.model = e.value
                self.model_detected = True
                self.display.show_message(p.model_name(e.value), "FL Studio Full", 1.5)
                self.refresh()
            return True
        return False

    def on_event(self, e):
        kind = e.kind
        if kind == "button":
            self.on_button(e)
        elif kind == "pot":
            self.on_pot(e.index, e.value)
        elif kind == "fader":
            self.on_fader(e.index, e.value)
        elif kind == "pad_mode":
            self.on_pad_mode(e.value)
        elif kind == "pot_mode":
            self.pot_mode = e.value
            self.display.show_message("Pots: " + POT_MODE_NAMES.get(e.value, "Custom"), "", config.MESSAGE_SECONDS)
            self.update_labels()
        elif kind == "fader_mode":
            self.fader_mode = e.value
            self.display.show_message("Faders: " + FADER_MODE_NAMES.get(e.value, "Custom"), "", config.MESSAGE_SECONDS)
            self.update_labels()
        elif kind in ("pad", "device_select_pad"):
            self.on_pad(e)
        elif kind == "drum_pad":
            return self.on_drum_pad(e)
        elif kind in ("pad_pressure", "drum_pressure", "pot_touch", "fader_touch"):
            return kind != "drum_pressure"  # drum aftertouch goes on to FL Studio like the notes
        self.refresh_leds()
        return True

    def on_pad_mode(self, mode):
        self.pad_mode = mode
        self.leds.forget(("session", "drum", "devsel"))

    # hooks filled in by later layers (pads, device mode)
    def on_pad(self, e):
        pass

    def on_drum_pad(self, e):
        return False

    # ------------------------------------------------------------------------------------------------ buttons

    def message(self, top, bottom=""):
        self.display.show_message(top, bottom, config.MESSAGE_SECONDS)
        if config.HINTS:
            host.hint(("Launchkey: " + top + (" " + bottom if bottom else "")).strip())

    def on_button(self, e):
        b = e.button
        if b == p.SHIFT:
            self.shift = e.pressed
            return
        if not e.pressed:
            self.on_button_release(e)
            return
        handler = getattr(self, "_btn_" + b, None)
        if handler is not None:
            if b == p.FADER_BUTTON:
                handler(e.index)
            else:
                handler()

    def on_button_release(self, e):
        pass

    # transport
    def _btn_play(self):
        if self.shift:  # restart from the beginning
            host.stop()
            host.toggle_play()
            self.message("Play from start")
            return
        host.toggle_play()
        self.message("Play" if host.is_playing() else "Pause")

    def _btn_stop(self):
        if self.shift:
            host.stop()
            host.rewind_to_start()
            self.message("Stop + rewind")
            return
        host.stop()
        self.message("Stop")

    def _btn_record(self):
        if self.shift:
            host.toggle_step_edit()
            self.message("Step edit", _on_off(host.is_step_edit_on()))
            return
        host.toggle_record()
        self.message("Record", _on_off(host.is_recording()))

    def _btn_loop(self):
        if self.shift:
            host.toggle_loop_record()
            self.message("Loop record", _on_off(host.is_loop_record_on()))
            return
        host.toggle_song_mode()
        self.message("Song mode" if host.is_song_mode() else "Pattern mode")

    def _btn_click(self):
        if self.shift:
            host.toggle_precount()
            self.message("Count-in", _on_off(host.is_precount_on()))
            return
        host.toggle_metronome()
        self.message("Metronome", _on_off(host.is_metronome_on()))

    def _btn_undo(self):
        if self.shift:
            host.redo()
            self.message("Redo")
        else:
            host.undo()
            self.message("Undo")

    def _btn_capture_midi(self):
        if self.shift:
            host.clear_capture()
            self.message("Capture cleared")
            return
        host.capture_midi(config.CAPTURE_SECONDS)
        self.message("Captured MIDI", "to pattern %d" % host.pattern())

    def _btn_quantise(self):
        ch = host.selected_channel()
        if ch < 0:
            self.message("Quantise", "no channel")
            return
        start_only = self.shift != config.QUANTISE_START_ONLY  # Shift: the other variant
        host.quantise(ch, start_only)
        self.message("Quantised" + (" starts" if start_only else ""), host.channel_name(ch))

    # mixer navigation
    def _btn_track_left(self):
        self.navigate_track(-1)

    def _btn_track_right(self):
        self.navigate_track(1)

    def navigate_track(self, delta):
        if self.shift:
            self.move_bank(delta * BANK_SIZE)
            return
        track = max(0, min(host.last_insert(), host.selected_track() + delta))
        host.select_track(track)
        self.follow_track(track)
        self.message(host.track_name(track), "Track %d" % track if track else "Master")

    def move_bank(self, delta):
        last_start = max(1, host.last_insert() - BANK_SIZE + 1)
        new = max(1, min(last_start, self.bank_start + delta))
        if new != self.bank_start:
            self.bank_start = new
            self.retarget()
        self.message("Tracks %d-%d" % (self.bank_start, self.bank_start + BANK_SIZE - 1))

    def follow_track(self, track):
        """Keeps the bank of eight around the selected mixer track."""
        if track < 1:
            return
        if track < self.bank_start or track >= self.bank_start + BANK_SIZE:
            last_start = max(1, host.last_insert() - BANK_SIZE + 1)
            self.bank_start = max(1, min(last_start, ((track - 1) // BANK_SIZE) * BANK_SIZE + 1))
            self.retarget()

    def retarget(self):
        """Controls point at new targets: let soft takeover pick them up again and relabel the screen."""
        self.update_labels()

    def bank_tracks(self):
        last = host.last_insert()
        return [t if t <= last else -1 for t in range(self.bank_start, self.bank_start + BANK_SIZE)]

    # fader buttons
    def _btn_arm_select(self):
        self.arm_mode = not self.arm_mode
        self.message("Fader buttons", "Arm" if self.arm_mode else self.fader_button_function.capitalize())

    def _btn_stop_solo_mute(self):
        i = FADER_BUTTON_FUNCTIONS.index(self.fader_button_function)
        step = -1 if self.shift else 1
        self.fader_button_function = FADER_BUTTON_FUNCTIONS[(i + step) % len(FADER_BUTTON_FUNCTIONS)]
        self.arm_mode = False
        self.message("Fader buttons", self.fader_button_function.capitalize())

    def _btn_fader_button(self, index):
        track = self.bank_tracks()[index]
        if track < 0:
            return
        if self.shift or (not self.arm_mode and self.fader_button_function == "select"):
            host.select_track(track)
            self.message(host.track_name(track), "selected")
        elif self.arm_mode:
            host.toggle_track_arm(track)
            self.message(host.track_name(track), "Armed" if host.is_track_armed(track) else "Disarmed")
        elif self.fader_button_function == "solo":
            host.toggle_track_solo(track)
            self.message(host.track_name(track), "Solo " + _on_off(host.is_track_solo(track)))
        else:
            host.toggle_track_mute(track)
            self.message(host.track_name(track), "Muted" if host.is_track_muted(track) else "Unmuted")

    # filled in by the device layer
    def _btn_device_select(self):
        self.message("Device Select", "n/a")

    def _btn_device_lock(self):
        self.message("Device Lock", "n/a")

    def _btn_scene_launch(self):
        pass

    def _btn_scene_up(self):
        pass

    def _btn_scene_down(self):
        pass

    # ------------------------------------------------------------------------------------------------ pots & faders

    def send_dest(self, which):
        rel = config.SEND_A_TRACK if which == "a" else config.SEND_B_TRACK
        last = host.last_insert()
        return last + 1 + rel if rel < 0 else min(rel, last)

    def mixer_target(self, kind, track):
        if track < 0:
            return NoTarget()
        if kind == "volume":
            return TrackVolume(track)
        if kind == "pan":
            return TrackPan(track)
        dest = self.send_dest(kind[-1])
        if dest == track:
            return NoTarget("-")
        return TrackSend(track, dest, config.SEND_CREATE_ROUTE)

    def device_target(self, slot):
        """Plugin parameter ``slot`` (0..15) of the controlled plugin; NoTarget without device mode."""
        return NoTarget("Device")

    def pot_target(self, index):
        track = self.bank_tracks()[index]
        mode = self.pot_mode
        if mode == p.POT_VOLUME:
            return self.mixer_target("volume", track)
        if mode == p.POT_PAN:
            return self.mixer_target("pan", track)
        if mode == p.POT_SEND_A:
            return self.mixer_target("send_a", track)
        if mode == p.POT_SEND_B:
            return self.mixer_target("send_b", track)
        if mode == p.POT_DEVICE:
            return self.device_target(index)
        return NoTarget()

    def fader_target(self, index):
        if index == p.FADER_COUNT:
            return TrackVolume(0)  # the 9th fader: master, in every fader mode
        track = self.bank_tracks()[index]
        mode = self.fader_mode
        if mode == p.FADER_VOLUME:
            return self.mixer_target("volume", track)
        if mode == p.FADER_SEND_A:
            return self.mixer_target("send_a", track)
        if mode == p.FADER_SEND_B:
            return self.mixer_target("send_b", track)
        if mode == p.FADER_DEVICE:
            return self.device_target(p.POT_COUNT + index)
        return NoTarget()

    def on_pot(self, index, value):
        self._move(self.pot_pickups[index], self.pot_target(index), value, "pot", index)

    def on_fader(self, index, value):
        self._move(self.fader_pickups[index], self.fader_target(index), value, "fader", index)

    def _move(self, pickup, target, value, control, index):
        if not target.valid():
            return
        applied, direction = pickup.move(target, value, config.SOFT_TAKEOVER, config.PICKUP_THRESHOLD)
        text = target.text()
        if not applied:
            text = (direction + " " + text) if direction == ">" else (text + " " + direction)
        self.display.set_label(control, index, target.short, text)
        if config.HINTS:
            host.hint("%s: %s" % (target.short, text))

    def update_labels(self):
        for i in range(p.POT_COUNT):
            t = self.pot_target(i)
            self.display.set_label("pot", i, t.short, t.text() if t.valid() else "")
        if self.has_faders:
            for i in range(p.FADER_COUNT + 1):
                t = self.fader_target(i)
                self.display.set_label("fader", i, t.short, t.text() if t.valid() else "")

    # ------------------------------------------------------------------------------------------------ feedback

    def refresh(self):
        if not self.active:
            return
        self.follow_track(host.selected_track())
        self.update_labels()
        self.refresh_leds()
        self.refresh_display()

    def refresh_leds(self):
        if not self.active:
            return
        leds = {}
        self.button_leds(leds)
        self.pad_leds(leds)
        self.leds.update(leds)

    def button_leds(self, leds):
        if self.has_faders:
            tracks = self.bank_tracks()
            for i in range(p.FADER_COUNT):
                leds[("cc", p.FADER_BUTTON_FIRST_CC + i)] = self.fader_button_led(tracks[i])
            leds[("cc", p.ARM_SELECT_CC)] = LedState(pal.WHITE if self.arm_mode else pal.DIM_WHITE)
        colour = pal.RED if self.arm_mode else FADER_BUTTON_FUNCTION_COLOURS[self.fader_button_function]
        leds[("cc", p.STOP_SOLO_MUTE_CC)] = LedState(colour)
        selected = host.selected_track()
        leds[("cc", p.TRACK_LEFT_CC)] = LedState(pal.WHITE if selected > 0 else pal.OFF)
        leds[("cc", p.TRACK_RIGHT_CC)] = LedState(pal.WHITE if selected < host.last_insert() else pal.OFF)

    def fader_button_led(self, track):
        if track < 0:
            return LedState(pal.OFF)
        colour = pal.of_fl_colour(host.track_colour(track))
        if self.arm_mode:
            return LedState(pal.RED if host.is_track_armed(track) else pal.DIM_RED)
        if self.fader_button_function == "solo":
            return LedState(pal.BLUE, p.PULSING) if host.is_track_solo(track) else LedState(pal.dimmed(colour))
        if self.fader_button_function == "select":
            return LedState(pal.WHITE) if track == host.selected_track() else LedState(pal.dimmed(colour))
        return LedState(pal.OFF if host.is_track_muted(track) else colour)

    def pad_leds(self, leds):
        if self.pad_mode == p.PAD_SESSION:
            for i in range(p.PAD_COUNT):
                leds[("session", i)] = LedState(pal.OFF)

    def default_rows(self):
        track = host.selected_track()
        top = host.track_name(track)
        return top, self.transport_text()

    def transport_text(self):
        flags = []
        flags.append("PLAY" if host.is_playing() else "STOP")
        if host.is_recording():
            flags.append("REC")
        flags.append("SONG" if host.is_song_mode() else "PAT")
        if host.is_metronome_on():
            flags.append("CLK")
        return " ".join(flags)

    def refresh_display(self):
        if not self.active:
            return
        top, bottom = self.default_rows()
        self.display.set_default(top, bottom)

    # ------------------------------------------------------------------------------------------------ FL callbacks

    def on_refresh(self, flags):
        self.refresh()

    def on_idle(self):
        if not self.active:
            return
        if self.display.message is not None and not self.display.message_active():
            self.refresh_display()

    def on_beat(self, value):
        pass

    def on_dirty_mixer_track(self, index):
        if self.active:
            self.refresh_leds()


def _on_off(on):
    return "On" if on else "Off"

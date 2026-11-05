"""The 16 pads in the Session layout as four switchable layers, plus Drum-layout feedback.

Layers (cycled with Scene Launch >):
- steps:    step sequencer of the selected channel (16 steps per page, channel colour, moving playhead)
- patterns: pick / create patterns (16 per page, pattern colours, current one pulsing)
- channels: select channels (Shift: mute), 16 per page, channel colours
- mixer:    top row selects the bank's mixer tracks, bottom row mutes them (Shift: solo)
"""

from lkmk3fl import config, host
from lkmk3fl import palette as pal
from lkmk3fl import protocol as p
from lkmk3fl.leds import LedState

LAYERS = ("steps", "patterns", "channels", "mixer")
LAYER_NAMES = {"steps": "Steps", "patterns": "Patterns", "channels": "Channels", "mixer": "Mixer"}
LAYER_COLOURS = {"steps": pal.AMBER, "patterns": pal.CYAN, "channels": pal.GREEN, "mixer": pal.MAGENTA}
PADS = p.PAD_COUNT


def _pages(count):
    return max(1, (count + PADS - 1) // PADS)


class PadsMixin:
    def reset_state(self):
        super().reset_state()
        self.layer = config.START_PAD_LAYER if config.START_PAD_LAYER in LAYERS else "steps"
        self.step_page = 0
        self.pattern_page = 0
        self.channel_page = 0
        self.playhead = -1
        self.drum_held = set()

    # ------------------------------------------------------------------------------------------------ helpers

    def step_count(self):
        return max(PADS, host.pattern_length(host.pattern()))

    def step_pages(self):
        return _pages(self.step_count())

    def pattern_pages(self):
        return _pages(min(host.pattern_max(), host.pattern_count() + 1))

    def channel_pages(self):
        return _pages(host.channel_count())

    def clamp_pages(self):
        self.step_page = max(0, min(self.step_page, self.step_pages() - 1))
        self.pattern_page = max(0, min(self.pattern_page, self.pattern_pages() - 1))
        self.channel_page = max(0, min(self.channel_page, self.channel_pages() - 1))

    def set_layer(self, layer):
        self.layer = layer
        self.playhead = -1
        self.message("Pads: " + LAYER_NAMES[layer], self.layer_text())

    def layer_text(self):
        if self.layer == "steps":
            first = self.step_page * PADS + 1
            return "Steps %d-%d" % (first, first + PADS - 1)
        if self.layer == "patterns":
            first = self.pattern_page * PADS + 1
            return "Pat %d-%d" % (first, first + PADS - 1)
        if self.layer == "channels":
            first = self.channel_page * PADS + 1
            return "Ch %d-%d" % (first, first + PADS - 1)
        return "Mix %d-%d" % (self.bank_start, self.bank_start + 7)

    # ------------------------------------------------------------------------------------------------ buttons

    def _btn_scene_launch(self):
        i = LAYERS.index(self.layer)
        self.set_layer(LAYERS[(i + (-1 if self.shift else 1)) % len(LAYERS)])
        if self.pad_mode != p.PAD_SESSION:  # bring the pads back to the session layout the layers live in
            host.send(p.pad_mode(p.PAD_SESSION))
            self.on_pad_mode(p.PAD_SESSION)

    def _btn_scene_up(self):
        self.scene(-1)

    def _btn_scene_down(self):
        self.scene(1)

    def scene(self, delta):
        layer = self.layer
        if layer == "steps":
            if self.shift:
                self.step_page = max(0, min(self.step_pages() - 1, self.step_page + delta))
                self.message("Steps", self.layer_text())
            else:
                self.move_channel(delta)
        elif layer == "patterns":
            if self.shift:
                self.pattern_page = max(0, min(self.pattern_pages() - 1, self.pattern_page + delta))
                self.message("Patterns", self.layer_text())
            else:
                target = max(1, min(host.pattern_max(), host.pattern() + delta))
                host.jump_to_pattern(target)
                self.follow_pattern()
                self.message(host.pattern_name(target), "Pattern %d" % target)
        elif layer == "channels":
            if self.shift:
                self.move_channel(delta)
            else:
                self.channel_page = max(0, min(self.channel_pages() - 1, self.channel_page + delta))
                self.message("Channels", self.layer_text())
        else:
            if self.shift:
                self.navigate_track_by(delta)
            else:
                self.move_bank(delta * 8)

    def navigate_track_by(self, delta):
        shift, self.shift = self.shift, False
        self.navigate_track(delta)
        self.shift = shift

    def move_channel(self, delta):
        count = host.channel_count()
        if count == 0:
            return
        current = host.selected_channel()
        target = max(0, min(count - 1, (current if current >= 0 else 0) + delta))
        host.select_channel(target)
        self.follow_channel()
        self.on_channel_selected(target)
        self.message(host.channel_name(target), "Channel %d" % (target + 1))

    def on_channel_selected(self, channel):
        """Hook for the device layer (the selected channel's plugin may become the device)."""

    def follow_channel(self):
        ch = host.selected_channel()
        if ch >= 0:
            self.channel_page = ch // PADS

    def follow_pattern(self):
        self.pattern_page = (host.pattern() - 1) // PADS

    # ------------------------------------------------------------------------------------------------ pads

    def on_pad(self, e):
        if e.kind == "device_select_pad":
            self.on_device_select_pad(e)
            return
        if not e.pressed:
            return
        handler = getattr(self, "_pad_" + self.layer)
        handler(e.index)

    def on_device_select_pad(self, e):
        """Overridden by the device layer."""

    def _pad_steps(self, index):
        ch = host.selected_channel()
        if ch < 0:
            self.message("Steps", "no channel")
            return
        if self.shift:  # Shift + pad: jump to that step page
            if index < self.step_pages():
                self.step_page = index
                self.message("Steps", self.layer_text())
            return
        step = self.step_page * PADS + index
        if step >= self.step_count():
            return
        host.set_step(ch, step, not host.step(ch, step))

    def _pad_patterns(self, index):
        n = self.pattern_page * PADS + index + 1
        if n > host.pattern_max() or n > host.pattern_count() + 1:
            return
        host.jump_to_pattern(n)
        self.message(host.pattern_name(n), "Pattern %d" % n)

    def _pad_channels(self, index):
        ch = self.channel_page * PADS + index
        if ch >= host.channel_count():
            return
        if self.shift:
            host.toggle_channel_mute(ch)
            self.message(host.channel_name(ch), "Muted" if host.is_channel_muted(ch) else "Unmuted")
            return
        host.select_channel(ch)
        self.on_channel_selected(ch)
        self.message(host.channel_name(ch), "Channel %d" % (ch + 1))

    def _pad_mixer(self, index):
        track = self.bank_tracks()[index % 8]
        if track < 0:
            return
        if index < 8:
            host.select_track(track)
            self.message(host.track_name(track), "selected")
        elif self.shift:
            host.toggle_track_solo(track)
            self.message(host.track_name(track), "Solo " + ("On" if host.is_track_solo(track) else "Off"))
        else:
            host.toggle_track_mute(track)
            self.message(host.track_name(track), "Muted" if host.is_track_muted(track) else "Unmuted")

    def on_drum_pad(self, e):
        """Drum layout notes go on to FL Studio (it plays / records them on the selected channel, e.g. FPC); the
        script only lights the pads."""
        if e.pressed:
            self.drum_held.add(e.index)
        else:
            self.drum_held.discard(e.index)
        self.refresh_leds()
        return False

    # ------------------------------------------------------------------------------------------------ feedback

    def pad_leds(self, leds):
        if self.pad_mode == p.PAD_SESSION:
            self.clamp_pages()
            colours = getattr(self, "_leds_" + self.layer)()
            for i in range(PADS):
                leds[("session", i)] = colours[i]
        elif self.pad_mode == p.PAD_DRUM:
            for i, state in enumerate(self.drum_leds()):
                leds[("drum", i)] = state
        elif self.pad_mode == p.PAD_DEVICE_SELECT:
            for i, state in enumerate(self.device_select_leds()):
                leds[("devsel", i)] = state

    def device_select_leds(self):
        return [LedState(pal.OFF) for _ in range(PADS)]

    def button_leds(self, leds):
        super().button_leds(leds)
        session = self.pad_mode == p.PAD_SESSION
        leds[("cc", p.SCENE_LAUNCH_CC)] = LedState(LAYER_COLOURS[self.layer] if session else pal.DIM_WHITE)
        up, down = self.scene_possible()
        leds[("cc", p.SCENE_UP_CC)] = LedState(pal.WHITE if session and up else pal.OFF)
        leds[("cc", p.SCENE_DOWN_CC)] = LedState(pal.WHITE if session and down else pal.OFF)

    def scene_possible(self):
        layer = self.layer
        if layer == "steps":
            if self.shift:
                return self.step_page > 0, self.step_page + 1 < self.step_pages()
            ch = host.selected_channel()
            return ch > 0, 0 <= ch < host.channel_count() - 1
        if layer == "patterns":
            return host.pattern() > 1, host.pattern() < host.pattern_max()
        if layer == "channels":
            return self.channel_page > 0, self.channel_page + 1 < self.channel_pages()
        return self.bank_start > 1, self.bank_start + 8 <= host.last_insert()

    def _leds_steps(self):
        ch = host.selected_channel()
        out = []
        if ch < 0:
            return [LedState(pal.OFF) for _ in range(PADS)]
        colour = pal.of_fl_colour(host.channel_colour(ch), pal.AMBER)
        if pal.is_grey(colour):
            colour = pal.WHITE  # grey channels (FL's default colour): keep set steps apart from the dim beat grid
        count = self.step_count()
        for i in range(PADS):
            step = self.step_page * PADS + i
            if step >= count:
                out.append(LedState(pal.OFF))
            elif step == self.playhead:
                out.append(LedState(self.playhead_colour(host.step(ch, step), colour)))
            elif host.step(ch, step):
                out.append(LedState(colour))
            else:
                out.append(LedState(pal.DIM_WHITE if step % 4 == 0 else pal.OFF))
        return out

    @staticmethod
    def playhead_colour(is_set, channel_colour):
        """Playhead over a set step vs. an empty one: two clearly different colours, never the plain step colours."""
        if not is_set:
            return config.PLAYHEAD_EMPTY_COLOUR & 0x7F
        colour = config.PLAYHEAD_SET_COLOUR & 0x7F
        if channel_colour == colour or (pal.is_grey(channel_colour) and pal.is_grey(colour)):
            colour = config.PLAYHEAD_SET_ALT_COLOUR & 0x7F
        return colour

    def current_step(self):
        """Step under the playhead in the current pattern, -1 when not playing (or in song mode)."""
        if not config.STEP_PLAYHEAD or not host.is_playing() or host.is_song_mode():
            return -1
        pos = host.song_step()
        if pos < 0:
            return -1
        return pos % self.step_count()

    def _leds_patterns(self):
        out = []
        current = host.pattern()
        count = host.pattern_count()
        top = host.pattern_max()
        for i in range(PADS):
            n = self.pattern_page * PADS + i + 1
            if n > top:
                out.append(LedState(pal.OFF))
            elif n <= count:
                colour = pal.of_fl_colour(host.pattern_colour(n), pal.CYAN)
                if n == current:
                    out.append(LedState(colour, p.PULSING))
                else:
                    out.append(LedState(pal.dimmed(colour)))
            elif n == count + 1:
                out.append(LedState(pal.DIM_GREEN))  # press to create a new pattern
            else:
                out.append(LedState(pal.OFF))
        return out

    def _leds_channels(self):
        out = []
        count = host.channel_count()
        selected = host.selected_channel()
        for i in range(PADS):
            ch = self.channel_page * PADS + i
            if ch >= count:
                out.append(LedState(pal.OFF))
                continue
            colour = pal.of_fl_colour(host.channel_colour(ch))
            if host.is_channel_muted(ch):
                out.append(LedState(pal.DIM_RED))
            elif ch == selected:
                out.append(LedState(colour, p.PULSING))
            else:
                out.append(LedState(pal.dimmed(colour)))
        return out

    def _leds_mixer(self):
        out = []
        tracks = self.bank_tracks()
        selected = host.selected_track()
        for t in tracks:
            if t < 0:
                out.append(LedState(pal.OFF))
            else:
                colour = pal.of_fl_colour(host.track_colour(t))
                out.append(LedState(pal.WHITE) if t == selected else LedState(pal.dimmed(colour)))
        for t in tracks:
            if t < 0:
                out.append(LedState(pal.OFF))
            elif host.is_track_solo(t):
                out.append(LedState(pal.BLUE, p.PULSING))
            else:
                colour = pal.of_fl_colour(host.track_colour(t))
                out.append(LedState(pal.OFF if host.is_track_muted(t) else colour))
        return out

    def drum_leds(self):
        ch = host.selected_channel()
        fpc = {}
        if ch >= 0:
            for note, colour in host.fpc_pads(ch):
                fpc.setdefault(note, colour)
        base = pal.of_fl_colour(host.channel_colour(ch)) if ch >= 0 else pal.AMBER
        out = []
        for i in range(PADS):
            if i in self.drum_held:
                out.append(LedState(pal.WHITE))
                continue
            note = p.drum_pad_note(i)
            if fpc:
                out.append(LedState(pal.of_fl_colour(fpc[note]) if note in fpc else pal.OFF))
            else:
                out.append(LedState(pal.dimmed(base)))
        return out

    def default_rows(self):
        if self.layer == "steps" or self.layer == "channels":
            ch = host.selected_channel()
            top = host.channel_name(ch) if ch >= 0 else "No channel"
        elif self.layer == "patterns":
            top = host.pattern_name(host.pattern())
        else:
            top = host.track_name(host.selected_track())
        return top, self.short_layer_text() + " " + self.transport_text()

    def short_layer_text(self):
        """ "S1-16" (steps), "P17-32" (patterns), "C1-16" (channels), "M9-16" (mixer)."""
        text = self.layer_text()
        return self.layer[0].upper() + text[text.index(" ") + 1 :]

    # ------------------------------------------------------------------------------------------------ FL callbacks

    def refresh(self):
        if self.active:
            self.follow_channel_if_needed()
        super().refresh()

    def follow_channel_if_needed(self):
        ch = host.selected_channel()
        if self.layer == "channels" and ch >= 0 and ch // PADS != self.channel_page:
            self.channel_page = ch // PADS

    def on_idle(self):
        super().on_idle()
        if not self.active or self.layer != "steps" or self.pad_mode != p.PAD_SESSION:
            return
        step = self.current_step()
        if step != self.playhead:
            self.playhead = step
            # follow the playhead across step pages while playing
            if step >= 0 and step // PADS != self.step_page and step // PADS < self.step_pages():
                self.step_page = step // PADS
            self.refresh_leds()

    def on_beat(self, value):
        super().on_beat(value)
        self.on_idle()

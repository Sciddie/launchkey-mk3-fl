"""Shared, resettable state behind the mocked FL Studio API modules.

The mock models just enough of FL Studio for the script's logic: transport, a mixer with routes, a channel rack with
step grids, patterns, plugins with parameters (generators on channels, effects in mixer slots), focused windows and
undo. Every call that changes something is also appended to ``calls`` so tests can assert on intent.
"""


class Plugin:
    def __init__(self, name, params=None, pads=None, user_name=None):
        self.name = name
        self.user_name = user_name  # the name the user gave the plugin in FL Studio, if any
        # list of [name, value 0..1]
        self.params = [list(p) for p in (params or [])]
        # FPC: list of (note, colour)
        self.pads = list(pads or [])


class Channel:
    def __init__(self, name, colour=0x5F7581, plugin=None, target_fx=0):
        self.name = name
        self.colour = colour
        self.muted = False
        self.selected = False
        self.grid = {}  # pattern -> set of steps
        self.plugin = plugin
        self.target_fx = target_fx
        self.notes = []  # (note, velocity) from midiNoteOn
        self.quantized = []


class Track:
    def __init__(self, name, colour=0x6E7681):
        self.name = name
        self.colour = colour
        self.volume = 0.8
        self.pan = 0.0
        self.muted = False
        self.solo = False
        self.armed = False
        self.routes = {}  # dest -> level
        self.slots = {}  # slot -> Plugin


class Pattern:
    def __init__(self, name, colour=0x4B5B66, length=16):
        self.name = name
        self.colour = colour
        self.length = length


class State:
    def __init__(self):
        self.reset()

    def reset(self):
        self.api_version = 36
        self.calls = []
        self.midi_out = []  # short messages as (status, data1, data2)
        self.sysex_out = []
        self.hints = []
        self.port_name = "MIDIIN2 (LKMK3 MIDI)"
        self.assigned = True
        self.playing = False
        self.recording = False
        self.loop_mode = 0  # 0 = pattern, 1 = song
        self.metronome = False
        self.precount = False
        self.loop_record = False
        self.step_edit = False
        self.song_pos = 0.0
        self.song_step = 0
        self.undo_pos = 0
        self.score_dumps = []
        self.score_cleared = 0
        # mixer: master, inserts 1..125, "current"
        self.tracks = [Track("Master")] + [Track("Insert %d" % i) for i in range(1, 126)] + [Track("Current")]
        self.selected_track = 0
        # channel rack
        self.channels = [Channel("Kick", 0xE04040), Channel("Clap", 0x40E040), Channel("Hat", 0x4040E0)]
        self.selected_channel = 0
        self.channels[0].selected = True
        # patterns (1-based in FL)
        self.patterns = {1: Pattern("Pattern 1")}
        self.pattern = 1
        # windows: focused widget id or None, form id
        self.focused = None
        self.form_id = -1
        self.editors_shown = []

    # helpers for tests
    def add_channels(self, count, plugin=None):
        for _ in range(count):
            self.channels.append(Channel("Ch %d" % (len(self.channels) + 1), 0x808080, plugin))

    def select_channel(self, index):
        for c in self.channels:
            c.selected = False
        self.channels[index].selected = True
        self.selected_channel = index

    def focus_generator(self, channel):
        self.focused = 7
        self.form_id = channel

    def focus_effect(self, track, slot):
        self.focused = 6
        self.form_id = track * 4194304 + slot * 65536

    def focus_window(self, widget):
        self.focused = widget
        self.form_id = widget

    def plugin_at(self, index, slot):
        if slot is None or slot < 0:
            if 0 <= index < len(self.channels):
                return self.channels[index].plugin
            return None
        if 0 <= index < len(self.tracks):
            return self.tracks[index].slots.get(slot)
        return None


state = State()

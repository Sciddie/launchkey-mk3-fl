"""Continuous controls (pots, faders): what each one is mapped to, and soft takeover.

A *target* is something a pot or fader can move: a mixer track's volume / pan / send level, or a plugin parameter.
Every target works with normalised values 0..1 so pickup and display code does not care what it controls.
"""

from lkmk3fl import host


class Target:
    """Base class; ``key`` identifies the target so a control notices when it was re-mapped."""

    key = None
    short = ""  # name for the pot / fader label on the LCD

    def get(self):
        return None

    def set(self, value):
        pass

    def text(self):
        return ""

    def valid(self):
        return self.key is not None


class NoTarget(Target):
    def __init__(self, label=""):
        self.short = label


class TrackVolume(Target):
    def __init__(self, track):
        self.track = track
        self.key = ("vol", track)
        self.short = host.track_name(track)

    def get(self):
        return host.track_volume(self.track)

    def set(self, value):
        host.set_track_volume(self.track, value)

    def text(self):
        return format_db(host.track_volume_db(self.track))


class TrackPan(Target):
    def __init__(self, track):
        self.track = track
        self.key = ("pan", track)
        self.short = host.track_name(track)

    def get(self):
        return (host.track_pan(self.track) + 1.0) / 2.0

    def set(self, value):
        host.set_track_pan(self.track, value * 2.0 - 1.0)

    def text(self):
        return format_pan(host.track_pan(self.track))


class TrackSend(Target):
    def __init__(self, track, dest, create_route):
        self.track = track
        self.dest = dest
        self.create_route = create_route
        self.key = ("send", track, dest)
        self.short = host.track_name(track)

    def get(self):
        return host.send_level(self.track, self.dest)

    def set(self, value):
        host.set_send_level(self.track, self.dest, value, self.create_route)

    def text(self):
        level = self.get()
        if level is None:
            return "no send"
        return format_percent(level)


class PluginParam(Target):
    def __init__(self, plugin, param, name):
        self.plugin = plugin
        self.param = param
        self.key = ("param", plugin, param)
        self.short = name

    def get(self):
        return host.param_value(self.plugin, self.param)

    def set(self, value):
        host.set_param_value(self.plugin, self.param, value)

    def text(self):
        s = host.param_value_string(self.plugin, self.param)
        return s if s else format_percent(self.get())


def format_db(db):
    if db is None or db != db or db < -199:
        return "-inf dB"
    return "%+.1f dB" % db if abs(db) >= 0.05 else "0.0 dB"


def format_pan(pan):
    p = int(round(pan * 100))
    if p == 0:
        return "C"
    return ("L%d" % -p) if p < 0 else ("R%d" % p)


def format_percent(value):
    return "%d%%" % int(round((value or 0.0) * 100))


class Pickup:
    """Soft takeover for one physical control.

    The control only moves its target once its position reaches (within ``threshold`` steps) or crosses the target's
    current value. It lets go again when the target is re-mapped or changed by something else (mouse, automation).
    """

    def __init__(self):
        self.key = None
        self.engaged = False
        self.last_hw = None
        self.last_set = None

    def reset(self):
        self.key = None
        self.engaged = False
        self.last_hw = None
        self.last_set = None

    def move(self, target, hw, enabled=True, threshold=3):
        """Returns (applied, hint): hint is "" when applied, else "<" / ">" for the direction to turn."""
        if target.key != self.key:
            self.reset()
            self.key = target.key
        current = target.get()
        if current is not None and self.last_set is not None and abs(current - self.last_set) > 1.5 / 127:
            self.engaged = False  # moved by someone else
            self.last_hw = None
        if not enabled or current is None:
            self.engaged = True
        elif not self.engaged:
            cur_hw = current * 127.0
            near = abs(hw - cur_hw) <= threshold
            crossed = self.last_hw is not None and (self.last_hw - cur_hw) * (hw - cur_hw) <= 0
            self.engaged = near or crossed
        self.last_hw = hw
        if not self.engaged:
            return False, ("<" if hw > current * 127.0 else ">")
        value = hw / 127.0
        if isinstance(target, TrackPan) and hw in (63, 64):
            value = 0.5  # detent: centre
        target.set(value)
        self.last_set = value
        return True, ""

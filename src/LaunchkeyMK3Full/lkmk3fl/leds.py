"""LED feedback with a cache, so only LEDs whose colour changed are sent to the surface."""

from lkmk3fl import host
from lkmk3fl import protocol as p


class LedState:
    __slots__ = ("colour", "lighting", "base")

    def __init__(self, colour=0, lighting=p.STATIONARY, base=0):
        self.colour = colour
        self.lighting = lighting
        self.base = base  # stationary colour under a flashing one

    def as_tuple(self):
        return (self.colour, self.lighting, self.base)


def _messages(address, state):
    kind, number = address
    colour, lighting, base = state.as_tuple()
    out = []

    def one(c, light):
        if kind == "session":
            out.append(p.session_pad_led(number, c, light))
        elif kind == "drum":
            out.append(p.drum_pad_led(number, c, light))
        elif kind == "devsel":
            out.append(p.device_select_pad_led(number, c, light))
        else:
            out.append(p.cc_led(number, c, light))

    if lighting == p.STATIONARY:
        one(colour, p.STATIONARY)
    elif lighting == p.FLASHING:
        one(base, p.STATIONARY)
        one(colour, p.FLASHING)
    else:
        one(colour, p.PULSING)
    return out


class LedCache:
    def __init__(self):
        self.sent = {}

    def forget(self, kinds=None):
        if kinds is None:
            self.sent.clear()
        else:
            for k in [a for a in self.sent if a[0] in kinds]:
                del self.sent[k]

    def update(self, desired):
        """``desired``: {(kind, number): LedState}; kind is "session", "drum", "devsel" or "cc"."""
        for address, state in desired.items():
            t = state.as_tuple()
            if self.sent.get(address) == t:
                continue
            for m in _messages(address, state):
                host.send(m)
            self.sent[address] = t

    def clear_all(self, addresses):
        for a in addresses:
            for m in _messages(a, LedState()):
                host.send(m)
        self.sent.clear()

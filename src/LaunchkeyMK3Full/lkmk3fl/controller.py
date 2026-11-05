"""The complete controller, composed from its layers:

- core.CoreController: DAW-mode lifecycle, transport, mixer control, soft takeover, LED / LCD output
- pads.PadsMixin: step sequencer, pattern, channel and mixer pad layers, Drum-layout feedback
- devicemode.DeviceMixin: plugin parameters on pots / faders, Device Select and Device Lock
"""

from lkmk3fl.core import CoreController
from lkmk3fl.devicemode import DeviceMixin
from lkmk3fl.pads import PadsMixin


class Controller(DeviceMixin, PadsMixin, CoreController):
    pass

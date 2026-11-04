"""The complete controller, composed from its layers:

- core.CoreController: DAW-mode lifecycle, transport, mixer control, soft takeover, LED / LCD output
- pads.PadsMixin: step sequencer, pattern, channel and mixer pad layers, Drum-layout feedback
"""

from lkmk3fl.core import CoreController
from lkmk3fl.pads import PadsMixin


class Controller(PadsMixin, CoreController):
    pass

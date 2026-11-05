class FlMidiMsg:
    """Stand-in for FL Studio's ``eventData`` object passed to OnMidiMsg / OnSysEx."""

    def __init__(self, status=0, data1=0, data2=0, sysex=None, port=0):
        self.status = status
        self.data1 = data1
        self.data2 = data2
        self.sysex = bytes(sysex) if sysex is not None else None
        self.port = port
        self.handled = False

    @property
    def midiId(self):
        return self.status & 0xF0

    @property
    def midiChan(self):
        return self.status & 0x0F

    @property
    def note(self):
        return self.data1

    @property
    def velocity(self):
        return self.data2

    @property
    def controlNum(self):
        return self.data1

    @property
    def controlVal(self):
        return self.data2

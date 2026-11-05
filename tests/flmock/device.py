from flmock.flstate import state


def midiOutMsg(message, channel=None, data1=None, data2=None):
    if channel is not None:
        state.midi_out.append((message | channel, data1, data2))
    else:
        state.midi_out.append((message & 0xFF, (message >> 8) & 0xFF, (message >> 16) & 0xFF))


def midiOutSysex(message):
    state.sysex_out.append(bytes(message))


def isAssigned():
    return state.assigned


def getName():
    return state.port_name


def getPortNumber():
    return 0


def setHasMeters():
    pass

from flmock.flstate import state


def channelCount(globalCount=False):
    return len(state.channels)


def selectedChannel(canBeNone=False, offset=0, indexGlobal=False):
    if state.selected_channel is None:
        return -1 if canBeNone else 0
    return state.selected_channel


def channelNumber(canBeNone=False, offset=0):
    return selectedChannel(canBeNone, offset)


def selectOneChannel(index, useGlobalIndex=False):
    state.calls.append(("channels.selectOneChannel", index))
    state.select_channel(index)


def isChannelSelected(index, useGlobalIndex=False):
    return state.channels[index].selected


def getChannelName(index, useGlobalIndex=False):
    return state.channels[index].name


def getChannelColor(index, useGlobalIndex=False):
    return state.channels[index].colour


def isChannelMuted(index, useGlobalIndex=False):
    return state.channels[index].muted


def muteChannel(index, value=-1, useGlobalIndex=False):
    state.calls.append(("channels.muteChannel", index))
    c = state.channels[index]
    c.muted = (not c.muted) if value == -1 else bool(value)


def getGridBit(index, position, useGlobalIndex=False):
    return position in state.channels[index].grid.get(state.pattern, set())


def setGridBit(index, position, value, useGlobalIndex=False):
    state.calls.append(("channels.setGridBit", index, position, bool(value)))
    steps = state.channels[index].grid.setdefault(state.pattern, set())
    if value:
        steps.add(position)
    else:
        steps.discard(position)


def quickQuantize(index, startOnly=1, useGlobalIndex=False):
    state.calls.append(("channels.quickQuantize", index, startOnly))
    state.channels[index].quantized.append(startOnly)


def getChannelIndex(index):
    return index


def midiNoteOn(indexGlobal, note, velocity, channel=-1):
    state.calls.append(("channels.midiNoteOn", indexGlobal, note, velocity))
    state.channels[indexGlobal].notes.append((note, velocity))


def getTargetFxTrack(index, useGlobalIndex=False):
    return state.channels[index].target_fx


def showEditor(index, value=-1, useGlobalIndex=False):
    state.calls.append(("channels.showEditor", index, value))
    state.editors_shown.append(index)
    state.focus_generator(index)


def focusEditor(index, useGlobalIndex=False):
    state.calls.append(("channels.focusEditor", index))
    state.focus_generator(index)

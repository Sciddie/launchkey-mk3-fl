from flmock.flstate import state


def trackCount():
    return len(state.tracks)


def trackNumber():
    return state.selected_track


def setTrackNumber(trackNumber, flags=0):
    state.calls.append(("mixer.setTrackNumber", trackNumber))
    state.selected_track = trackNumber


def isTrackSelected(index):
    return index == state.selected_track


def getTrackName(index):
    return state.tracks[index].name


def getTrackColor(index):
    return state.tracks[index].colour


def getTrackVolume(index, mode=0):
    v = state.tracks[index].volume
    if mode:
        if v <= 0:
            return float("-inf")
        # FL's curve is not linear; a rough stand-in good enough for display tests: 0.8 -> 0 dB
        import math

        return 20 * math.log10((v / 0.8) ** 2)
    return v


def setTrackVolume(index, volume, pickupMode=0):
    state.calls.append(("mixer.setTrackVolume", index, round(volume, 4)))
    state.tracks[index].volume = volume


def getTrackPan(index):
    return state.tracks[index].pan


def setTrackPan(index, pan, pickupMode=0):
    state.calls.append(("mixer.setTrackPan", index, round(pan, 4)))
    state.tracks[index].pan = pan


def isTrackMuted(index):
    return state.tracks[index].muted


def muteTrack(index, value=-1):
    state.calls.append(("mixer.muteTrack", index))
    t = state.tracks[index]
    t.muted = (not t.muted) if value == -1 else bool(value)


def isTrackSolo(index):
    return state.tracks[index].solo


def soloTrack(index, value=-1, mode=-1):
    state.calls.append(("mixer.soloTrack", index))
    t = state.tracks[index]
    t.solo = (not t.solo) if value == -1 else bool(value)


def isTrackArmed(index):
    return state.tracks[index].armed


def armTrack(index):
    state.calls.append(("mixer.armTrack", index))
    state.tracks[index].armed = not state.tracks[index].armed


def getRouteSendActive(index, destIndex):
    return destIndex in state.tracks[index].routes


def getRouteToLevel(index, destIndex):
    return state.tracks[index].routes.get(destIndex, 0.0)


def setRouteToLevel(index, destIndex, level):
    state.calls.append(("mixer.setRouteToLevel", index, destIndex, round(level, 4)))
    state.tracks[index].routes[destIndex] = level


def setRouteTo(index, destIndex, value, updateUI=False):
    state.calls.append(("mixer.setRouteTo", index, destIndex, value))
    if value:
        state.tracks[index].routes.setdefault(destIndex, 0.8)
    else:
        state.tracks[index].routes.pop(destIndex, None)


def isTrackPluginValid(index, plugIndex):
    return plugIndex in state.tracks[index].slots


def getSongStepPos():
    return state.song_step


def focusEditor(index, plugIndex):
    state.calls.append(("mixer.focusEditor", index, plugIndex))
    state.focus_effect(index, plugIndex)


def getActiveEffectIndex():
    if state.focused == 6:
        return (state.form_id >> 22, (state.form_id >> 16) & 0x3F)
    return None

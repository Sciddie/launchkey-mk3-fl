from flmock.flstate import state


def getVersion():
    return state.api_version


def undoUp():
    state.calls.append(("general.undoUp",))
    state.undo_pos += 1


def undoDown():
    state.calls.append(("general.undoDown",))
    state.undo_pos -= 1


def getUseMetronome():
    return state.metronome


def getPrecount():
    return state.precount


def dumpScoreLog(time, silent=False):
    state.calls.append(("general.dumpScoreLog", time, silent))
    state.score_dumps.append((time, state.pattern))


def clearLog():
    state.calls.append(("general.clearLog",))
    state.score_cleared += 1


def saveUndo(name, flags, update=True):
    state.calls.append(("general.saveUndo", name))

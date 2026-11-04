from flmock.flstate import state


def patternNumber():
    return state.pattern


def patternCount():
    return len(state.patterns)


def patternMax():
    return 999


def getPatternName(index):
    p = state.patterns.get(index)
    return p.name if p else ""


def getPatternColor(index):
    p = state.patterns.get(index)
    return p.colour if p else 0


def getPatternLength(index):
    p = state.patterns.get(index)
    return p.length if p else 0


def jumpToPattern(index):
    from flmock.flstate import Pattern

    state.calls.append(("patterns.jumpToPattern", index))
    if index not in state.patterns:
        state.patterns[index] = Pattern("Pattern %d" % index)
    state.pattern = index


def isPatternDefault(index):
    return index not in state.patterns

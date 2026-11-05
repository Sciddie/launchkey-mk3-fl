from flmock.flstate import state


def getFocused(index):
    if state.focused is None:
        return False
    if index == 5:
        return state.focused in (6, 7)
    return state.focused == index


def getFocusedFormID():
    return state.form_id


def getFocusedPluginName():
    p = None
    if state.focused == 7:
        p = state.plugin_at(state.form_id, -1)
    elif state.focused == 6:
        p = state.plugin_at(state.form_id >> 22, (state.form_id >> 16) & 0x3F)
    return p.name if p else ""


def setHintMsg(msg):
    state.hints.append(msg)


def showWindow(index):
    state.calls.append(("ui.showWindow", index))
    state.focus_window(index)


def isMetronomeEnabled():
    return state.metronome


def isPrecountEnabled():
    return state.precount


def isLoopRecEnabled():
    return state.loop_record


def getStepEditMode():
    return state.step_edit

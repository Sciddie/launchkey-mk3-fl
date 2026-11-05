from flmock.flstate import state


def _p(index, slotIndex):
    p = state.plugin_at(index, slotIndex)
    if p is None:
        raise TypeError("Operation unsafe at current time")
    return p


def isValid(index, slotIndex=-1, useGlobalIndex=False):
    return state.plugin_at(index, slotIndex) is not None


def getPluginName(index, slotIndex=-1, userName=False, useGlobalIndex=False):
    p = _p(index, slotIndex)
    return (p.user_name or p.name) if userName else p.name


def getParamCount(index, slotIndex=-1, useGlobalIndex=False):
    return len(_p(index, slotIndex).params)


def getParamName(paramIndex, index, slotIndex=-1, useGlobalIndex=False):
    return _p(index, slotIndex).params[paramIndex][0]


def getParamValue(paramIndex, index, slotIndex=-1, useGlobalIndex=False):
    return _p(index, slotIndex).params[paramIndex][1]


def setParamValue(value, paramIndex, index, slotIndex=-1, pickupMode=0, useGlobalIndex=False):
    state.calls.append(("plugins.setParamValue", round(value, 4), paramIndex, index, slotIndex))
    _p(index, slotIndex).params[paramIndex][1] = value


def getParamValueString(paramIndex, index, slotIndex=-1, pickupMode=0, useGlobalIndex=False):
    return "%d%%" % round(_p(index, slotIndex).params[paramIndex][1] * 100)


def getPadInfo(chanIndex, slotIndex=-1, paramOption=0, paramIndex=-1, useGlobalIndex=False):
    p = state.plugin_at(chanIndex, slotIndex)
    pads = p.pads if p else []
    if paramOption == 0:
        return len(pads)
    if paramOption == 1:
        return pads[paramIndex][0]
    if paramOption == 2:
        return pads[paramIndex][1]
    return 0

"""The only module that talks to FL Studio's API. Everything else (controller, pads, controls, display) calls these
functions, which keeps FL Studio quirks (API versions, index conventions, calls that raise while a project loads) in
one place and lets the tests swap in a mock of FL Studio's modules.
"""

import channels
import device
import general
import mixer
import patterns
import plugins
import transport
import ui

from lkmk3fl import flconst as fl

# --- MIDI out ------------------------------------------------------------------------------------------------------


def send(message):
    """Sends a (status, data1, data2) tuple on the script's output port."""
    status, data1, data2 = message
    device.midiOutMsg(status | (data1 << 8) | (data2 << 16))


def send_sysex(data):
    device.midiOutSysex(bytes(data))


def is_output_assigned():
    try:
        return bool(device.isAssigned())
    except Exception:
        return True


def port_name():
    try:
        return device.getName()
    except Exception:
        return ""


def api_version():
    try:
        return int(general.getVersion())
    except Exception:
        return 1


def hint(text):
    try:
        ui.setHintMsg(text)
    except Exception:
        pass


# --- transport -----------------------------------------------------------------------------------------------------


def toggle_play():
    transport.start()


def stop():
    transport.stop()


def toggle_record():
    transport.record()


def is_playing():
    return bool(transport.isPlaying())


def is_recording():
    return bool(transport.isRecording())


def is_song_mode():
    return transport.getLoopMode() == 1


def toggle_song_mode():
    transport.setLoopMode()


def rewind_to_start():
    transport.setSongPos(0.0)


def global_transport(command):
    transport.globalTransport(command, 1, fl.PME_SYSTEM, fl.GT_ALL)


def toggle_metronome():
    global_transport(fl.FPT_METRONOME)


def is_metronome_on():
    try:
        return bool(ui.isMetronomeEnabled())
    except Exception:
        return bool(general.getUseMetronome())


def toggle_precount():
    global_transport(fl.FPT_COUNT_DOWN)


def is_precount_on():
    try:
        return bool(ui.isPrecountEnabled())
    except Exception:
        return bool(general.getPrecount())


def toggle_loop_record():
    global_transport(fl.FPT_LOOP_RECORD)


def is_loop_record_on():
    try:
        return bool(ui.isLoopRecEnabled())
    except Exception:
        return False


def toggle_step_edit():
    global_transport(fl.FPT_STEP_EDIT)


def is_step_edit_on():
    try:
        return bool(ui.getStepEditMode())
    except Exception:
        return False


def song_step():
    """Playback position in steps (16th notes)."""
    try:
        return int(mixer.getSongStepPos())
    except Exception:
        return -1


def undo():
    general.undoUp()


def redo():
    general.undoDown()


def capture_midi(seconds):
    """Writes recently played notes into the selected pattern (FL Studio's score log, API 15+)."""
    general.dumpScoreLog(int(seconds), False)


def clear_capture():
    general.clearLog()


# --- mixer ---------------------------------------------------------------------------------------------------------


def track_count():
    """All mixer tracks incl. master (0) and FL's hidden "current" track (the last one)."""
    return int(mixer.trackCount())


def last_insert():
    return max(1, track_count() - 2)


def selected_track():
    return int(mixer.trackNumber())


def select_track(index):
    mixer.setTrackNumber(index, fl.CURFX_SCROLL_TO_MAKE_VISIBLE)


def track_name(index):
    return mixer.getTrackName(index)


def track_colour(index):
    return mixer.getTrackColor(index)


def track_volume(index):
    return float(mixer.getTrackVolume(index))


def track_volume_db(index):
    return float(mixer.getTrackVolume(index, 1))


def set_track_volume(index, value):
    mixer.setTrackVolume(index, value, fl.PIM_NONE)


def track_pan(index):
    return float(mixer.getTrackPan(index))


def set_track_pan(index, value):
    mixer.setTrackPan(index, value, fl.PIM_NONE)


def is_track_muted(index):
    return bool(mixer.isTrackMuted(index))


def toggle_track_mute(index):
    mixer.muteTrack(index)


def is_track_solo(index):
    return bool(mixer.isTrackSolo(index))


def toggle_track_solo(index):
    mixer.soloTrack(index)


def is_track_armed(index):
    return bool(mixer.isTrackArmed(index))


def toggle_track_arm(index):
    mixer.armTrack(index)


def has_route(source, dest):
    return bool(mixer.getRouteSendActive(source, dest))


def send_level(source, dest):
    """Route level 0..1, or None where FL Studio cannot report it (API < 36) or there is no route."""
    if api_version() < 36 or not has_route(source, dest):
        return None
    return float(mixer.getRouteToLevel(source, dest))


def set_send_level(source, dest, level, create_route=False):
    if api_version() < 36:
        return False
    if not has_route(source, dest):
        if not create_route:
            return False
        mixer.setRouteTo(source, dest, True, True)
    mixer.setRouteToLevel(source, dest, level)
    return True


def is_effect_valid(track, slot):
    try:
        return bool(mixer.isTrackPluginValid(track, slot))
    except Exception:
        return False


def focus_effect(track, slot):
    mixer.focusEditor(track, slot)


# --- channel rack --------------------------------------------------------------------------------------------------


def channel_count():
    return int(channels.channelCount())


def selected_channel():
    """Selected channel (index within the current group), -1 when none."""
    try:
        return int(channels.selectedChannel(True))
    except TypeError:
        return int(channels.channelNumber())


def select_channel(index):
    channels.selectOneChannel(index)


def channel_name(index):
    return channels.getChannelName(index)


def channel_colour(index):
    return channels.getChannelColor(index)


def is_channel_muted(index):
    return bool(channels.isChannelMuted(index))


def toggle_channel_mute(index):
    channels.muteChannel(index)


def step(channel, position):
    return bool(channels.getGridBit(channel, position))


def set_step(channel, position, on):
    channels.setGridBit(channel, position, 1 if on else 0)


def quantise(channel, start_only):
    channels.quickQuantize(channel, 1 if start_only else 0)


def show_channel_editor(channel):
    channels.showEditor(channel)


def channel_target_track(channel):
    try:
        return int(channels.getTargetFxTrack(channel))
    except Exception:
        return 0


# --- patterns ------------------------------------------------------------------------------------------------------


def pattern():
    return int(patterns.patternNumber())


def pattern_count():
    return int(patterns.patternCount())


def pattern_max():
    try:
        return int(patterns.patternMax())
    except Exception:
        return 999


def pattern_name(index):
    return patterns.getPatternName(index)


def pattern_colour(index):
    return patterns.getPatternColor(index)


def pattern_length(index):
    try:
        return int(patterns.getPatternLength(index))
    except Exception:
        return 16


def jump_to_pattern(index):
    patterns.jumpToPattern(index)


# --- windows & plugins ---------------------------------------------------------------------------------------------


def focused_plugin():
    """(index, slot) of the focused plugin window: (channel, -1) for a generator, (track, slot) for an effect."""
    try:
        if ui.getFocused(fl.WID_PLUGIN_GENERATOR):
            form = int(ui.getFocusedFormID())
            if form >= 0:
                return (form, -1)
        if ui.getFocused(fl.WID_PLUGIN_EFFECT):
            form = int(ui.getFocusedFormID())
            if form >= 0:
                return (form >> fl.FORM_ID_TRACK_SHIFT, (form >> fl.FORM_ID_SLOT_SHIFT) & 0x3F)
    except Exception:
        pass
    return None


def is_mixer_focused():
    return bool(ui.getFocused(fl.WID_MIXER))


def show_window(widget):
    ui.showWindow(widget)


def plugin_valid(target):
    if target is None:
        return False
    try:
        return bool(plugins.isValid(target[0], target[1]))
    except Exception:
        return False


def plugin_name(target):
    try:
        return plugins.getPluginName(target[0], target[1], True)
    except TypeError:
        return plugins.getPluginName(target[0], target[1])


def param_count(target):
    return int(plugins.getParamCount(target[0], target[1]))


def param_name(target, param):
    return plugins.getParamName(param, target[0], target[1])


def param_value(target, param):
    return float(plugins.getParamValue(param, target[0], target[1]))


def param_value_string(target, param):
    try:
        return plugins.getParamValueString(param, target[0], target[1])
    except Exception:
        return ""


def set_param_value(target, param, value):
    plugins.setParamValue(value, param, target[0], target[1])


def fpc_pads(channel):
    """[(note, colour)] for an FPC on ``channel``, [] for anything else (FL Studio API 19+)."""
    if api_version() < 19:
        return []
    try:
        if not plugins.isValid(channel, -1):
            return []
        count = int(plugins.getPadInfo(channel, -1, 0))
        return [
            (int(plugins.getPadInfo(channel, -1, 1, i)), int(plugins.getPadInfo(channel, -1, 2, i)))
            for i in range(count)
        ]
    except Exception:
        return []

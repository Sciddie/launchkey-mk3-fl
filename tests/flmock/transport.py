from flmock.flstate import state

FPT_Metronome = 110
FPT_WaitForInput = 111
FPT_LoopRecord = 113
FPT_StepEdit = 114
FPT_CountDown = 115


def start():
    state.calls.append(("transport.start",))
    state.playing = not state.playing


def stop():
    state.calls.append(("transport.stop",))
    state.playing = False
    state.song_step = 0


def record():
    state.calls.append(("transport.record",))
    state.recording = not state.recording


def isPlaying():
    return state.playing


def isRecording():
    return state.recording


def getLoopMode():
    return state.loop_mode


def setLoopMode():
    state.calls.append(("transport.setLoopMode",))
    state.loop_mode = 1 - state.loop_mode


def getSongPos(mode=-1):
    return state.song_pos


def setSongPos(position, mode=-1):
    state.calls.append(("transport.setSongPos", position))
    state.song_pos = position


def globalTransport(command, value, pmeflags=2, flags=15):
    state.calls.append(("transport.globalTransport", command, value))
    if value:
        if command == FPT_Metronome:
            state.metronome = not state.metronome
        elif command == FPT_CountDown:
            state.precount = not state.precount
        elif command == FPT_LoopRecord:
            state.loop_record = not state.loop_record
        elif command == FPT_StepEdit:
            state.step_edit = not state.step_edit
    return 1

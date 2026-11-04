# name=Novation Launchkey MK3 (Full)
# url=https://github.com/Sciddie/launchkey-mk3-fl
"""FL Studio MIDI controller script: full integration for the Novation Launchkey MK3 (25 / 37 / 49 / 61 / 88).

Assign it to the Launchkey's DAW port (Windows: MIDIIN2 / MIDIOUT2 (LKMK3 MIDI); macOS: "Launchkey MK3 xx LKMK3 DAW
In / Out") and give input and output the same port number. The keys port stays a generic controller. See README.md.
"""

from lkmk3fl.controller import Controller

_controller = Controller()


def OnInit():
    _controller.init()


def OnDeInit():
    _controller.deinit()


def OnMidiMsg(event):
    if event.status in (0xF0, 0xF7):
        return
    if _controller.on_midi(event.status, event.data1, event.data2):
        event.handled = True


def OnSysEx(event):
    if event.sysex is not None and _controller.on_sysex(event.sysex):
        event.handled = True


def OnRefresh(flags):
    _controller.on_refresh(flags)


def OnDirtyMixerTrack(index):
    _controller.on_dirty_mixer_track(index)


def OnIdle():
    _controller.on_idle()


def OnUpdateBeatIndicator(value):
    _controller.on_beat(value)


def OnProjectLoad(status):
    _controller.on_refresh(0)

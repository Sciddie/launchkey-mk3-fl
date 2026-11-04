from lkmk3fl import flconst
from lkmk3fl import protocol as p


def test_play_toggles_playback(surface, fl):
    surface.press(p.PLAY_CC)
    assert fl.playing
    assert surface.lcd_rows()[0] == "Play"
    surface.press(p.PLAY_CC)
    assert not fl.playing
    assert surface.lcd_rows()[0] == "Pause"


def test_shift_play_restarts(surface, fl):
    fl.playing = True
    surface.press(p.PLAY_CC, shift=True)
    assert fl.playing
    assert [c[0] for c in fl.calls[-2:]] == ["transport.stop", "transport.start"]


def test_stop(surface, fl):
    fl.playing = True
    surface.press(p.STOP_CC)
    assert not fl.playing


def test_shift_stop_rewinds(surface, fl):
    fl.song_pos = 0.5
    surface.press(p.STOP_CC, shift=True)
    assert fl.song_pos == 0.0


def test_record_and_shift_record_step_edit(surface, fl):
    surface.press(p.RECORD_CC)
    assert fl.recording
    assert surface.lcd_rows() == ["Record", "On"]
    surface.press(p.RECORD_CC, shift=True)
    assert fl.step_edit
    assert ("transport.globalTransport", flconst.FPT_STEP_EDIT, 1) in fl.calls


def test_loop_switches_pattern_song_and_shift_loop_record(surface, fl):
    surface.press(p.LOOP_CC)
    assert fl.loop_mode == 1
    assert surface.lcd_rows()[0] == "Song mode"
    surface.press(p.LOOP_CC)
    assert fl.loop_mode == 0
    surface.press(p.LOOP_CC, shift=True)
    assert fl.loop_record


def test_click_metronome_and_shift_click_count_in(surface, fl):
    surface.press(p.CLICK_CC)
    assert fl.metronome
    surface.press(p.CLICK_CC, shift=True)
    assert fl.precount
    assert surface.lcd_rows() == ["Count-in", "On"]


def test_undo_redo(surface, fl):
    surface.press(p.UNDO_CC)
    assert fl.calls[-1] == ("general.undoUp",)
    surface.press(p.UNDO_CC, shift=True)
    assert fl.calls[-1] == ("general.undoDown",)
    assert surface.lcd_rows()[0] == "Redo"


def test_capture_midi_and_shift_clear(make_surface, fl):
    s = make_surface(CAPTURE_SECONDS=12)
    s.press(p.CAPTURE_MIDI_CC)
    assert ("general.dumpScoreLog", 12, False) in fl.calls
    assert s.lcd_rows() == ["Captured MIDI", "to pattern 1"]
    s.press(p.CAPTURE_MIDI_CC, shift=True)
    assert fl.score_cleared == 1


def test_quantise_selected_channel(surface, fl):
    fl.select_channel(1)
    surface.press(p.QUANTISE_CC)
    assert fl.channels[1].quantized == [1]
    surface.press(p.QUANTISE_CC, shift=True)
    assert fl.channels[1].quantized == [1, 0]
    assert surface.lcd_rows()[1] == "Clap"


def test_quantise_without_channel(surface, fl):
    fl.selected_channel = None
    surface.press(p.QUANTISE_CC)
    assert surface.lcd_rows() == ["Quantise", "no channel"]


def test_button_release_does_nothing(surface, fl):
    fl.calls.clear()
    surface.cc16(p.PLAY_CC, 0)
    assert fl.calls == []


def test_transport_state_on_display(surface, fl):
    fl.playing = True
    fl.recording = True
    fl.loop_mode = 1
    surface.refresh()
    assert surface.lcd_rows()[1] == "S1-16 REC SONG"

from flmock.flstate import Pattern
from lkmk3fl import palette as pal
from lkmk3fl import protocol as p


def kick_colour(fl):
    return pal.of_fl_colour(fl.channels[0].colour)


# --- steps layer -------------------------------------------------------------------------------------------------


def test_step_pads_toggle_steps_of_selected_channel(surface, fl):
    surface.pad(0)
    surface.pad(4)
    assert fl.channels[0].grid[1] == {0, 4}
    assert surface.session_led(0) == (kick_colour(fl), 0)
    assert surface.session_led(8) == (pal.DIM_WHITE, 0)  # beat grid
    assert surface.session_led(1) == (pal.OFF, 0)
    surface.pad(0)
    assert fl.channels[0].grid[1] == {4}
    assert surface.session_led(0) == (pal.DIM_WHITE, 0)


def test_step_pads_follow_selected_channel(surface, fl):
    fl.channels[1].grid[1] = {2}
    fl.select_channel(1)
    surface.refresh()
    assert surface.session_led(2) == (pal.of_fl_colour(fl.channels[1].colour), 0)
    assert surface.lcd_rows()[0] == "Clap"


def test_scene_buttons_select_channels_in_steps_layer(surface, fl):
    assert surface.cc_led(p.SCENE_UP_CC) == (pal.OFF, 0)
    assert surface.cc_led(p.SCENE_DOWN_CC) == (pal.WHITE, 0)
    surface.press(p.SCENE_DOWN_CC)
    assert fl.selected_channel == 1
    assert surface.lcd_rows() == ["Clap", "Channel 2"]
    surface.press(p.SCENE_DOWN_CC)
    surface.press(p.SCENE_DOWN_CC)
    assert fl.selected_channel == 2  # clamps at the last channel
    surface.press(p.SCENE_UP_CC)
    assert fl.selected_channel == 1


def test_step_pages_for_long_patterns(surface, fl):
    fl.patterns[1].length = 32
    surface.press(p.SCENE_DOWN_CC, shift=True)
    assert surface.controller.step_page == 1
    surface.pad(3)
    assert fl.channels[0].grid[1] == {19}
    surface.press(p.SCENE_DOWN_CC, shift=True)
    assert surface.controller.step_page == 1  # no third page
    surface.pad(0, shift=True)  # Shift + pad: jump to page 1
    assert surface.controller.step_page == 0


def test_steps_beyond_pattern_length_are_dark(surface, fl):
    fl.patterns[1].length = 12
    surface.refresh()
    assert surface.controller.step_count() == 16  # FL shows at least 16 steps
    fl.patterns[1].length = 20
    surface.press(p.SCENE_DOWN_CC, shift=True)
    assert surface.session_led(4) == (pal.OFF, 0)
    fl.calls.clear()
    surface.pad(4)
    assert not surface.calls("channels.setGridBit")


def test_playhead_moves_while_playing(surface, fl):
    fl.channels[0].grid[1] = {0}
    fl.playing = True
    fl.song_step = 2
    surface.idle(0.02)
    assert surface.session_led(2) == (pal.WHITE, 0)
    fl.song_step = 3
    surface.idle(0.02)
    assert surface.session_led(2) == (pal.OFF, 0)
    assert surface.session_led(3) == (pal.WHITE, 0)
    fl.song_step = 16  # wraps in a 16-step pattern
    surface.idle(0.02)
    assert surface.session_led(0) == (pal.WHITE, 0)
    fl.playing = False
    surface.idle(0.02)
    assert surface.session_led(0) == (kick_colour(fl), 0)


def test_playhead_follows_pages(surface, fl):
    fl.patterns[1].length = 32
    fl.playing = True
    fl.song_step = 20
    surface.idle(0.02)
    assert surface.controller.step_page == 1
    assert surface.session_led(4) == (pal.WHITE, 0)


def test_no_playhead_in_song_mode_or_when_disabled(make_surface, fl):
    s = make_surface()
    fl.playing = True
    fl.loop_mode = 1
    fl.song_step = 2
    s.idle(0.02)
    assert s.session_led(2) == (pal.OFF, 0)
    s = make_surface(STEP_PLAYHEAD=False)
    fl.loop_mode = 0
    s.idle(0.02)
    assert s.session_led(2) == (pal.OFF, 0)


def test_beat_indicator_updates_playhead(surface, fl):
    fl.playing = True
    fl.song_step = 5
    surface.script.OnUpdateBeatIndicator(2)
    assert surface.session_led(5) == (pal.WHITE, 0)


# --- layer switching ---------------------------------------------------------------------------------------------


def test_scene_launch_cycles_layers(surface):
    assert surface.cc_led(p.SCENE_LAUNCH_CC) == (pal.AMBER, 0)
    surface.press1(p.SCENE_LAUNCH_CC)
    assert surface.controller.layer == "patterns"
    assert surface.lcd_rows()[0] == "Pads: Patterns"
    assert surface.cc_led(p.SCENE_LAUNCH_CC) == (pal.CYAN, 0)
    surface.press1(p.SCENE_LAUNCH_CC)
    assert surface.controller.layer == "channels"
    surface.press1(p.SCENE_LAUNCH_CC)
    assert surface.controller.layer == "mixer"
    surface.press1(p.SCENE_LAUNCH_CC)
    assert surface.controller.layer == "steps"
    surface.press1(p.SCENE_LAUNCH_CC, shift=True)
    assert surface.controller.layer == "mixer"


def test_start_layer_from_config(make_surface):
    assert make_surface(START_PAD_LAYER="patterns").controller.layer == "patterns"
    assert make_surface(START_PAD_LAYER="bogus").controller.layer == "steps"


def test_scene_launch_returns_pads_to_session_layout(surface, fl):
    surface.report_pad_mode(p.PAD_DRUM)
    surface.press1(p.SCENE_LAUNCH_CC)
    assert (0xBF, p.PAD_MODE_CC, p.PAD_SESSION) in fl.midi_out[-40:]
    assert surface.controller.pad_mode == p.PAD_SESSION


# --- patterns layer ----------------------------------------------------------------------------------------------


def test_pattern_pads(make_surface, fl):
    fl.patterns[2] = Pattern("Drop", 0xE04040)
    s = make_surface(START_PAD_LAYER="patterns")
    assert s.session_led(0)[1] == p.PULSING  # current
    assert s.session_led(1) == (pal.dimmed(pal.of_fl_colour(0xE04040)), 0)
    assert s.session_led(2) == (pal.DIM_GREEN, 0)  # new pattern slot
    assert s.session_led(3) == (pal.OFF, 0)
    s.pad(1)
    assert fl.pattern == 2
    assert s.lcd_rows() == ["Drop", "Pattern 2"]
    s.pad(2)
    assert fl.pattern == 3 and 3 in fl.patterns
    fl.calls.clear()
    s.pad(9)  # beyond the next free slot
    assert not s.calls("patterns.jumpToPattern")


def test_pattern_scene_buttons(make_surface, fl):
    s = make_surface(START_PAD_LAYER="patterns")
    s.press(p.SCENE_DOWN_CC)
    assert fl.pattern == 2
    s.press(p.SCENE_UP_CC)
    assert fl.pattern == 1
    s.press(p.SCENE_UP_CC)
    assert fl.pattern == 1
    for i in range(3, 20):
        fl.patterns[i] = Pattern("P%d" % i)
    s.press(p.SCENE_DOWN_CC, shift=True)
    assert s.controller.pattern_page == 1
    s.pad(0)
    assert fl.pattern == 17


# --- channels layer ----------------------------------------------------------------------------------------------


def test_channel_pads_select_and_mute(make_surface, fl):
    s = make_surface(START_PAD_LAYER="channels")
    assert s.session_led(0) == (kick_colour(fl), p.PULSING)
    assert s.session_led(3) == (pal.OFF, 0)
    s.pad(2)
    assert fl.selected_channel == 2
    s.pad(1, shift=True)
    assert fl.channels[1].muted
    assert s.session_led(1) == (pal.DIM_RED, 0)


def test_channel_pages(make_surface, fl):
    fl.add_channels(20)
    s = make_surface(START_PAD_LAYER="channels")
    s.press(p.SCENE_DOWN_CC)
    assert s.controller.channel_page == 1
    s.pad(0)
    assert fl.selected_channel == 16
    s.press(p.SCENE_DOWN_CC)
    assert s.controller.channel_page == 1
    s.press(p.SCENE_UP_CC, shift=True)
    assert fl.selected_channel == 15
    assert s.controller.channel_page == 0


# --- mixer layer -------------------------------------------------------------------------------------------------


def test_mixer_pads(make_surface, fl):
    s = make_surface(START_PAD_LAYER="mixer")
    s.pad(2)
    assert fl.selected_track == 3
    assert s.session_led(2) == (pal.WHITE, 0)
    s.pad(8 + 1)
    assert fl.tracks[2].muted
    assert s.session_led(9) == (pal.OFF, 0)
    s.pad(8 + 4, shift=True)
    assert fl.tracks[5].solo
    assert s.session_led(12) == (pal.BLUE, p.PULSING)


def test_mixer_layer_scene_buttons_move_bank(make_surface, fl):
    s = make_surface(START_PAD_LAYER="mixer")
    s.press(p.SCENE_DOWN_CC)
    assert s.controller.bank_start == 9
    s.press(p.SCENE_DOWN_CC, shift=True)
    assert fl.selected_track == 1
    s.press(p.SCENE_UP_CC)
    assert s.controller.bank_start == 1


# --- drum layout -------------------------------------------------------------------------------------------------


def test_drum_pads_pass_through_to_fl(surface, fl):
    surface.report_pad_mode(p.PAD_DRUM)
    ev = surface.midi(0x99, 36, 100)
    assert not ev.handled  # FL Studio plays / records the note on the selected channel
    assert surface.drum_led(8) == (pal.WHITE, 0)
    surface.midi(0x89, 36, 0)
    assert surface.drum_led(8) == (pal.dimmed(kick_colour(fl)), 0)
    assert not surface.midi(0xA9, 36, 30).handled


def test_drum_pads_show_fpc_colours(surface, fl):
    from flmock.flstate import Plugin

    fl.channels[0].plugin = Plugin("FPC", pads=[(36, 0xFF0000), (37, 0x00FF00)])
    surface.report_pad_mode(p.PAD_DRUM)
    assert surface.drum_led(8) == (pal.of_fl_colour(0xFF0000), 0)
    assert surface.drum_led(9) == (pal.of_fl_colour(0x00FF00), 0)
    assert surface.drum_led(0) == (pal.OFF, 0)


def test_pad_mode_change_resends_pad_leds(surface, fl):
    surface.report_pad_mode(p.PAD_DRUM)
    surface.report_pad_mode(p.PAD_SESSION)
    fl.midi_out.clear()
    surface.report_pad_mode(p.PAD_DRUM)
    assert sum(1 for st, _, _ in fl.midi_out if st == 0x99) == 16


def test_custom_pad_modes_get_no_script_leds(surface, fl):
    fl.midi_out.clear()
    surface.report_pad_mode(p.PAD_CUSTOM0)
    assert not any((st & 0xF0) == 0x90 for st, _, _ in fl.midi_out)

import pytest

from lkmk3fl import controls
from lkmk3fl import palette as pal
from lkmk3fl import protocol as p


def test_faders_control_bank_volume_after_pickup(surface, fl):
    # volume 0.8 = 101.6 of 127: a fader at 0 must not jump the track
    surface.fader(0, 0)
    assert fl.tracks[1].volume == 0.8
    name, value = surface.label("fader", 0)
    assert name == "Insert 1" and value.startswith(">")
    surface.fader(0, 100)  # within 3 steps of 101.6? no: 1.6 away -> picked up
    assert fl.tracks[1].volume == pytest.approx(100 / 127)
    surface.fader(0, 50)
    assert fl.tracks[1].volume == pytest.approx(50 / 127)


def test_fader_picks_up_when_crossing(surface, fl):
    surface.fader(1, 90)
    surface.fader(1, 110)  # jumped across 101.6
    assert fl.tracks[2].volume == pytest.approx(110 / 127)


def test_soft_takeover_can_be_disabled(make_surface, fl):
    s = make_surface(SOFT_TAKEOVER=False)
    s.fader(0, 0)
    assert fl.tracks[1].volume == 0.0


def test_master_fader_is_always_master(surface, fl):
    surface.report_fader_mode(p.FADER_SEND_A)
    surface.fader(8, 102)
    assert fl.tracks[0].volume == pytest.approx(102 / 127)
    assert surface.label("fader", 8)[0] == "Master"


def test_external_change_releases_pickup(surface, fl):
    surface.fader(0, 102)
    assert fl.tracks[1].volume == pytest.approx(102 / 127)
    fl.tracks[1].volume = 0.2  # mouse
    surface.fader(0, 100)
    assert fl.tracks[1].volume == 0.2


def test_pots_default_to_pan_with_centre_detent(surface, fl):
    surface.pot(2, 64)
    assert fl.tracks[3].pan == 0.0
    surface.sweep_pot(2, 64, 127)
    assert fl.tracks[3].pan == pytest.approx(1.0)
    assert surface.label("pot", 2) == ("Insert 3", "R100")
    surface.sweep_pot(2, 127, 63)
    assert fl.tracks[3].pan == 0.0


def test_pot_volume_mode(surface, fl):
    surface.report_pot_mode(p.POT_VOLUME)
    assert surface.lcd_rows()[0] == "Pots: Volume"
    assert surface.label("pot", 0)[0] == "Insert 1"
    surface.pot(0, 101)
    assert fl.tracks[1].volume == pytest.approx(101 / 127)


def test_send_modes_move_existing_routes_only(surface, fl):
    fl.tracks[1].routes[124] = 0.5  # Send A = last insert - 1 = 124
    surface.report_pot_mode(p.POT_SEND_A)
    surface.pot(0, 64)
    assert fl.tracks[1].routes[124] == pytest.approx(64 / 127)
    surface.pot(1, 64)
    assert 124 not in fl.tracks[2].routes
    assert surface.label("pot", 1)[1].endswith("no send")


def test_send_b_creates_route_when_configured(make_surface, fl):
    s = make_surface(SEND_CREATE_ROUTE=True, SOFT_TAKEOVER=False)
    s.report_fader_mode(p.FADER_SEND_B)
    s.fader(0, 127)
    assert fl.tracks[1].routes[125] == pytest.approx(1.0)


def test_sends_need_api_36(surface, fl):
    fl.api_version = 30
    fl.tracks[1].routes[124] = 0.5
    surface.report_pot_mode(p.POT_SEND_A)
    surface.sweep_pot(0, 60, 70)
    assert fl.tracks[1].routes[124] == 0.5


def test_send_to_itself_is_disabled(make_surface, fl):
    s = make_surface(SEND_A_TRACK=3)
    s.report_pot_mode(p.POT_SEND_A)
    assert s.label("pot", 2)[0] == "-"


def test_track_buttons_select_and_follow_bank(surface, fl):
    surface.press(p.TRACK_RIGHT_CC)
    assert fl.selected_track == 1
    assert surface.lcd_rows() == ["Insert 1", "Track 1"]
    for _ in range(8):
        surface.press(p.TRACK_RIGHT_CC)
    assert fl.selected_track == 9
    assert surface.controller.bank_start == 9
    assert surface.label("fader", 0)[0] == "Insert 9"
    surface.press(p.TRACK_LEFT_CC)
    assert surface.controller.bank_start == 1


def test_track_left_stops_at_master(surface, fl):
    surface.press(p.TRACK_LEFT_CC)
    assert fl.selected_track == 0
    assert surface.cc_led(p.TRACK_LEFT_CC) == (pal.OFF, 0)
    assert surface.cc_led(p.TRACK_RIGHT_CC) == (pal.WHITE, 0)


def test_shift_track_moves_bank_by_eight(surface, fl):
    surface.press(p.TRACK_RIGHT_CC, shift=True)
    assert surface.controller.bank_start == 9
    assert surface.lcd_rows()[0] == "Tracks 9-16"
    for _ in range(30):
        surface.press(p.TRACK_RIGHT_CC, shift=True)
    assert surface.controller.bank_start == 118  # last bank ends at insert 125
    surface.press(p.TRACK_LEFT_CC, shift=True)
    assert surface.controller.bank_start == 110


def test_bank_change_resets_pickup(surface, fl):
    surface.fader(0, 102)
    surface.press(p.TRACK_RIGHT_CC, shift=True)
    surface.fader(0, 10)
    assert fl.tracks[9].volume == 0.8


def test_selecting_a_track_in_fl_moves_the_bank(surface, fl):
    fl.selected_track = 20
    surface.refresh()
    assert surface.controller.bank_start == 17


def test_fader_buttons_mute_by_default(surface, fl):
    surface.press(p.FADER_BUTTON_FIRST_CC)
    assert fl.tracks[1].muted
    assert surface.cc_led(p.FADER_BUTTON_FIRST_CC) == (pal.OFF, 0)
    surface.press(p.FADER_BUTTON_FIRST_CC)
    assert not fl.tracks[1].muted
    assert surface.cc_led(p.FADER_BUTTON_FIRST_CC)[0] == pal.of_fl_colour(fl.tracks[1].colour)


def test_stop_solo_mute_cycles_fader_button_function(surface, fl):
    assert surface.cc_led(p.STOP_SOLO_MUTE_CC) == (pal.AMBER, 0)
    surface.press1(p.STOP_SOLO_MUTE_CC)
    assert surface.controller.fader_button_function == "solo"
    assert surface.cc_led(p.STOP_SOLO_MUTE_CC) == (pal.BLUE, 0)
    surface.press(p.FADER_BUTTON_FIRST_CC + 1)
    assert fl.tracks[2].solo
    assert surface.cc_led(p.FADER_BUTTON_FIRST_CC + 1) == (pal.BLUE, p.PULSING)
    surface.press1(p.STOP_SOLO_MUTE_CC)
    assert surface.controller.fader_button_function == "select"
    surface.press(p.FADER_BUTTON_FIRST_CC + 2)
    assert fl.selected_track == 3
    assert surface.cc_led(p.FADER_BUTTON_FIRST_CC + 2) == (pal.WHITE, 0)
    surface.press1(p.STOP_SOLO_MUTE_CC, shift=True)
    assert surface.controller.fader_button_function == "solo"


def test_arm_select_switches_fader_buttons_to_arm(surface, fl):
    assert surface.cc_led(p.ARM_SELECT_CC) == (pal.DIM_WHITE, 0)
    surface.press(p.ARM_SELECT_CC)
    assert surface.cc_led(p.ARM_SELECT_CC) == (pal.WHITE, 0)
    assert surface.cc_led(p.STOP_SOLO_MUTE_CC) == (pal.RED, 0)
    surface.press(p.FADER_BUTTON_FIRST_CC + 3)
    assert fl.tracks[4].armed
    assert surface.cc_led(p.FADER_BUTTON_FIRST_CC + 3) == (pal.RED, 0)
    assert surface.cc_led(p.FADER_BUTTON_FIRST_CC + 4) == (pal.DIM_RED, 0)
    surface.press(p.ARM_SELECT_CC)
    assert not surface.controller.arm_mode


def test_shift_fader_button_selects(surface, fl):
    surface.press(p.FADER_BUTTON_FIRST_CC + 5, shift=True)
    assert fl.selected_track == 6
    assert not fl.tracks[6].muted


def test_fader_buttons_beyond_last_insert_are_dark(surface, fl):
    surface.controller.bank_start = 120
    surface.refresh()
    assert surface.cc_led(p.FADER_BUTTON_FIRST_CC + 7) == (pal.OFF, 0)
    fl.calls.clear()
    surface.press(p.FADER_BUTTON_FIRST_CC + 7)
    assert not surface.calls("mixer.muteTrack")


def test_mixer_changes_in_fl_update_leds(surface, fl):
    fl.tracks[2].muted = True
    surface.script.OnDirtyMixerTrack(2)
    assert surface.cc_led(p.FADER_BUTTON_FIRST_CC + 1) == (pal.OFF, 0)


def test_volume_text_formatting():
    assert controls.format_db(0.0) == "0.0 dB"
    assert controls.format_db(-6.02) == "-6.0 dB"
    assert controls.format_db(5.6) == "+5.6 dB"
    assert controls.format_db(float("-inf")) == "-inf dB"
    assert controls.format_pan(-0.5) == "L50"
    assert controls.format_pan(0.004) == "C"
    assert controls.format_percent(0.333) == "33%"

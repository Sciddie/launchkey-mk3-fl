from lkmk3fl import protocol as p


def test_init_enters_daw_mode_and_asks_for_the_model(make_surface, fl):
    s = make_surface(model=None)
    assert fl.midi_out[0] == (0x9F, 0x0C, 0x7F)
    assert bytes([0xF0, 0x7E, 0x7F, 0x06, 0x01, 0xF7]) in fl.sysex_out
    assert (0xBF, p.PAD_MODE_CC, p.PAD_SESSION) in fl.midi_out
    assert (0xBF, p.POT_MODE_CC, p.POT_PAN) in fl.midi_out
    assert (0xBF, p.FADER_MODE_CC, p.FADER_VOLUME) in fl.midi_out
    assert s.controller.active


def test_start_modes_come_from_config(make_surface, fl):
    make_surface(START_POT_MODE="device", START_FADER_MODE="send_a")
    assert (0xBF, p.POT_MODE_CC, p.POT_DEVICE) in fl.midi_out
    assert (0xBF, p.FADER_MODE_CC, p.FADER_SEND_A) in fl.midi_out


def test_welcome_message_then_default_display(make_surface, fl):
    s = make_surface(model=None, init=False)
    s.script.OnInit()
    assert s.lcd_rows()[0] == "FL Studio"
    s.idle(3.0)
    assert s.lcd_rows() == ["Master", "STOP PAT"]


def test_deinit_clears_leds_and_leaves_daw_mode(surface, fl):
    surface.script.OnDeInit()
    assert fl.midi_out[-1] == (0x9F, 0x0C, 0x00)
    assert surface.session_led(0) == (0, 0)
    assert surface.cc_led(p.SCENE_LAUNCH_CC) == (0, 0)
    assert bytes([0xF0, 0, 0x20, 0x29, 2, 0x0F, 6, 0xF7]) in fl.sysex_out
    assert not surface.controller.active
    fl.midi_out.clear()
    surface.script.OnDeInit()  # twice is harmless
    assert fl.midi_out == []


def test_model_detection(make_surface):
    s = make_surface(model=0x34)
    assert s.controller.model == 0x34 and not s.controller.has_faders
    s = make_surface(model=0x40)
    assert s.controller.has_faders
    assert s.controller.model_detected


def test_forced_model_ignores_inquiry(make_surface):
    s = make_surface(model=0x36, MODEL=25)
    assert s.controller.model == 0x34


def test_25_and_37_get_no_fader_feedback(make_surface, fl):
    s = make_surface(model=0x35)
    s.clear_output()
    s.controller.leds.forget()
    s.controller.display.forget()
    s.refresh()
    assert fl.midi_out
    assert not any(
        st == 0xB0 and p.FADER_BUTTON_FIRST_CC <= d1 < p.FADER_BUTTON_FIRST_CC + 8 for st, d1, _ in fl.midi_out
    )
    assert not any(m[6] == p.SET_PARAM_NAME_CMD and m[7] >= p.FADER_DISPLAY_FIRST for m in fl.sysex_out)


def test_events_are_marked_handled(surface):
    assert surface.cc16(p.PLAY_CC, 127).handled
    assert surface.pot(0, 10).handled
    assert surface.midi(0x90, 96, 100).handled
    assert not surface.midi(0xB0, 1, 64).handled  # not ours: FL Studio processes it


def test_unrelated_sysex_is_not_handled(surface):
    assert not surface.sysex(bytes([0xF0, 0x01, 0x02, 0xF7])).handled


def test_leds_are_only_resent_when_they_change(surface, fl):
    surface.refresh()
    fl.midi_out.clear()
    surface.refresh()
    surface.refresh()
    assert fl.midi_out == []


def test_temporary_message_expires_back_to_default_rows(surface):
    surface.press(p.CLICK_CC)
    assert surface.lcd_rows() == ["Metronome", "On"]
    surface.idle(0.5)
    assert surface.lcd_rows()[0] == "Metronome"
    surface.idle(2.0)
    assert surface.lcd_rows() == ["Master", "STOP PAT CLK"]


def test_hint_bar_mirrors_messages(surface, fl):
    surface.press(p.CLICK_CC)
    assert fl.hints[-1] == "Launchkey: Metronome On"


def test_hints_can_be_disabled(make_surface, fl):
    s = make_surface(HINTS=False)
    fl.hints.clear()
    s.press(p.CLICK_CC)
    assert fl.hints == []


def test_unassigned_output_port_warns(make_surface, fl):
    fl.assigned = False
    make_surface()
    assert any("output port" in h for h in fl.hints)

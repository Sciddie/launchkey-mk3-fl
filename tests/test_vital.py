import pytest

from flmock.flstate import Plugin
from lkmk3fl import flconst, plugin_maps
from lkmk3fl import protocol as p
from lkmk3fl.plugin_maps import vital

# A plausible subset of Vital's parameter names (display names), deliberately not in Vital's own order, with some
# unrelated parameters in between.
VITAL_NAMES = [
    "Bypass",
    "Volume",
    "Macro 3",
    "Macro 1",
    "Macro 2",
    "Macro 4",
    "Polyphony",
    "Envelope 1 Attack",
    "Envelope 1 Decay",
    "Envelope 1 Sustain",
    "Envelope 1 Release",
    "Envelope 2 Attack",
    "Envelope 2 Decay",
    "Envelope 2 Sustain",
    "Envelope 2 Release",
    "Filter 1 Cutoff",
    "Filter 1 Resonance",
    "Filter 1 Drive",
    "Filter 1 Mix",
    "Filter 1 Key Track",
    "Filter 1 Blend",
    "Filter 2 Cutoff",
    "Filter 2 Resonance",
    "Filter 2 Drive",
    "Filter 2 Mix",
    "Oscillator 1 Level",
    "Oscillator 1 Transpose",
    "Oscillator 1 Tune",
    "Oscillator 1 Wave Frame",
    "Oscillator 1 Unison Voices",
    "Oscillator 1 Unison Detune",
    "Oscillator 2 Level",
    "Oscillator 2 Wave Frame",
    "Oscillator 3 Level",
    "Reverb Mix",
    "Reverb Size",
    "Delay Mix",
    "Delay Feedback",
    "Chorus Mix",
    "LFO 1 Frequency",
    "Sub Level",
]


def vital_plugin(names=VITAL_NAMES, name="Vital", user_name=None):
    return Plugin(name, [[n, 0.5] for n in names], user_name=user_name)


@pytest.fixture
def vit(make_surface, fl):
    fl.channels[0].plugin = vital_plugin()
    s = make_surface()
    s.report_pot_mode(p.POT_DEVICE)
    return s


def idx(name):
    return VITAL_NAMES.index(name)


# --- the data-driven resolver ------------------------------------------------------------------------------------


def test_find_map_by_name():
    assert plugin_maps.find_map("Vital") is vital.MAP
    assert plugin_maps.find_map("", "My Vital Lead") is vital.MAP
    assert plugin_maps.find_map("3x Osc") is None
    assert plugin_maps.find_map(None) is None


def test_map_shape():
    for page in vital.MAP["pages"]:
        assert len(page["name"]) <= 8
        assert len(page["pots"]) <= 8 and len(page["faders"]) <= 8
        for label, candidates in page["pots"] + page["faders"]:
            assert len(label) <= 16
            assert candidates and all(isinstance(c, str) for c in candidates)


def test_resolve_by_name_not_index():
    pages = plugin_maps.resolve(vital.MAP, VITAL_NAMES)
    macros = pages[0]
    assert macros.name == "Macros"
    assert macros.slots[0] == (idx("Macro 1"), "Macro 1")
    assert macros.slots[2] == (idx("Macro 3"), "Macro 3")
    assert macros.slots[7] == (idx("Volume"), "Volume")
    assert macros.slots[8] == (idx("Oscillator 1 Level"), "Osc1 Level")


def test_missing_parameters_leave_empty_slots_and_empty_pages_are_dropped():
    pages = plugin_maps.resolve(vital.MAP, VITAL_NAMES)
    names = [pg.name for pg in pages]
    assert names == ["Macros", "Osc", "Filter", "Env", "FX"]
    osc = pages[1]
    assert osc.slots[2] is None  # no "Oscillator 3 Wave Frame" in this list
    pages = plugin_maps.resolve(vital.MAP, ["Macro 1", "Something"])
    assert [pg.name for pg in pages] == ["Macros"]
    assert plugin_maps.resolve(vital.MAP, ["Gain"]) == []


def test_resolve_falls_back_to_internal_ids_and_prefixes():
    pages = plugin_maps.resolve(vital.MAP, ["macro_control_1", "MACRO 2", "Filter 1 Cutoff (Hz)", "osc_1_level"])
    macros = pages[0]
    assert macros.slots[0][0] == 0  # internal id
    assert macros.slots[1][0] == 1  # case / spacing
    assert macros.slots[4][0] == 2  # host appended a unit
    assert macros.slots[8][0] == 3


def test_a_parameter_is_used_once_per_page():
    pages = plugin_maps.resolve(
        {
            "name": "X",
            "match": ("x",),
            "pages": [{"name": "P", "pots": [("A", ("Level",)), ("B", ("Level",))], "faders": []}],
        },
        ["Level"],
    )
    assert pages[0].slots[0] == (0, "A") and pages[0].slots[1] is None


# --- in Device mode ----------------------------------------------------------------------------------------------


def test_vital_gets_curated_pages(vit, fl):
    assert vit.label("pot", 0) == ("Macro 1", "50%")
    assert vit.label("pot", 4)[0] == "F1 Cutoff"
    vit.idle(5)
    assert vit.lcd_rows() == ["Vital", "Dev 1/11 Macros"]  # 5 curated + 6 generic pages (41 names)
    vit.pot(0, 64)
    assert fl.channels[0].plugin.params[idx("Macro 1")][1] == pytest.approx(64 / 127)
    assert fl.channels[0].plugin.params[0][1] == 0.5  # "Bypass", the first parameter, untouched


def test_track_buttons_turn_curated_pages(vit, fl):
    vit.press(p.TRACK_RIGHT_CC)
    assert vit.lcd_rows() == ["Vital", "2/11 Osc"]
    assert vit.label("pot", 0)[0] == "Osc1 WaveFrame"
    assert vit.label("pot", 2) == ("-", "")  # not found -> empty slot
    vit.press(p.TRACK_RIGHT_CC)
    assert vit.label("pot", 1)[0] == "F1 Reso"
    vit.press(p.TRACK_RIGHT_CC)
    assert vit.label("pot", 3)[0] == "Env1 Release"
    vit.pot(3, 64)
    assert fl.channels[0].plugin.params[idx("Envelope 1 Release")][1] == pytest.approx(64 / 127)
    vit.press(p.TRACK_RIGHT_CC)
    assert vit.lcd_rows()[1] == "5/11 FX"
    vit.press(p.TRACK_RIGHT_CC)  # then the generic pages
    assert vit.lcd_rows()[1] == "6/11 Params"
    assert vit.label("pot", 0)[0] == "Bypass"
    for _ in range(10):
        vit.press(p.TRACK_RIGHT_CC)
    assert vit.controller.current_page((0, -1)) == 10  # stops at the last page
    assert vit.cc_led(p.TRACK_RIGHT_CC)[0] == 0
    vit.press(p.TRACK_LEFT_CC)
    assert vit.lcd_rows()[1] == "10/11 Params"


def test_faders_take_the_curated_fader_slots(vit, fl):
    vit.report_fader_mode(p.FADER_DEVICE)
    assert vit.label("fader", 0)[0] == "Osc1 Level"
    assert vit.label("fader", 3)[0] == "Sub Level"
    assert vit.label("fader", 4) == ("-", "")
    vit.fader(0, 64)
    assert fl.channels[0].plugin.params[idx("Oscillator 1 Level")][1] == pytest.approx(64 / 127)
    assert vit.label("fader", 8)[0] == "Master"


def test_renamed_vital_is_still_detected(make_surface, fl):
    fl.channels[0].plugin = vital_plugin(user_name="Bass")
    s = make_surface()
    s.report_pot_mode(p.POT_DEVICE)
    assert s.label("pot", 0)[0] == "Macro 1"
    s.idle(5)
    assert s.lcd_rows()[0] == "Bass"


def test_vital_as_mixer_effect_slot(make_surface, fl):
    fl.tracks[3].slots[0] = vital_plugin()
    s = make_surface()
    s.report_pot_mode(p.POT_DEVICE)
    fl.focus_effect(3, 0)
    s.refresh(flconst.HW_DIRTY_FOCUSED_WINDOW)
    assert s.label("pot", 0)[0] == "Macro 1"


def test_curated_pages_can_be_disabled(make_surface, fl):
    fl.channels[0].plugin = vital_plugin()
    s = make_surface(CURATED_PLUGIN_PAGES=False)
    s.report_pot_mode(p.POT_DEVICE)
    assert s.label("pot", 0)[0] == "Bypass"


def test_vital_without_known_names_falls_back_to_generic(make_surface, fl):
    fl.channels[0].plugin = vital_plugin(["Param A", "Param B"])
    s = make_surface()
    s.report_pot_mode(p.POT_DEVICE)
    assert s.label("pot", 0)[0] == "Param A"
    s.idle(5)
    assert s.lcd_rows()[1] == "Dev 1/1"


def test_other_plugins_unchanged(make_surface, fl):
    fl.channels[0].plugin = Plugin("Sytrus", [["Macro 1", 0.5], ["Cutoff", 0.5]])
    s = make_surface()
    s.report_pot_mode(p.POT_DEVICE)
    assert s.label("pot", 1)[0] == "Cutoff"

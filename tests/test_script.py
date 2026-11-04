import os
import re

from conftest import ROOT, SCRIPT_DIR

SCRIPT = os.path.join(SCRIPT_DIR, "device_LaunchkeyMK3Full.py")


def test_header_names_the_script_for_fl_studio():
    with open(SCRIPT, encoding="utf-8") as f:
        lines = f.read().splitlines()
    assert lines[0] == "# name=Novation Launchkey MK3 (Full)"
    assert lines[1] == "# url=https://github.com/Sciddie/launchkey-mk3-fl"


def test_script_file_name_matches_fl_studio_pattern():
    assert re.fullmatch(r"device_\w+\.py", os.path.basename(SCRIPT))


def test_callbacks_exist(surface):
    for name in (
        "OnInit",
        "OnDeInit",
        "OnMidiMsg",
        "OnSysEx",
        "OnRefresh",
        "OnIdle",
        "OnUpdateBeatIndicator",
        "OnDirtyMixerTrack",
        "OnProjectLoad",
    ):
        assert callable(getattr(surface.script, name))


def test_project_load_refreshes(surface, fl):
    fl.select_channel(2)
    surface.script.OnProjectLoad(100)
    surface.idle(5)
    assert surface.lcd_rows()[0] == "Hat"


def test_script_uses_only_fl_modules_and_its_package():
    allowed = {
        "device",
        "midi",
        "transport",
        "mixer",
        "channels",
        "patterns",
        "plugins",
        "ui",
        "general",
        "playlist",
        "utils",
        "time",
        "lkmk3fl",
    }
    for folder, _, files in os.walk(SCRIPT_DIR):
        for name in files:
            if not name.endswith(".py"):
                continue
            with open(os.path.join(folder, name), encoding="utf-8") as f:
                for line in f:
                    m = re.match(r"\s*(?:from|import)\s+([\w.]+)", line)
                    if m:
                        assert m.group(1).split(".")[0] in allowed, (name, line)


def test_versions_agree():
    from lkmk3fl.version import VERSION

    with open(os.path.join(ROOT, "CHANGELOG.md"), encoding="utf-8") as f:
        changelog = f.read()
    with open(os.path.join(ROOT, "pyproject.toml"), encoding="utf-8") as f:
        pyproject = f.read()
    assert "## [%s]" % VERSION in changelog
    assert 'version = "%s"' % VERSION in pyproject

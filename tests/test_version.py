import re

from lkmk3fl.version import VERSION


def test_version_is_semver():
    assert re.fullmatch(r"\d+\.\d+\.\d+", VERSION)

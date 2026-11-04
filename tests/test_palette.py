from lkmk3fl import palette


def test_table_has_128_entries():
    assert len(palette.TABLE) == 128


def test_primary_colours_match_expected_hues():
    assert palette.nearest(0xFF0000) in (5, 72, 120, 106)
    assert palette.nearest(0x00FF00) in (21, 87, 122)
    assert palette.nearest(0x0000FF) in (45, 67, 79)
    assert palette.nearest(0xFFFFFF) in (3, 119)


def test_black_is_off():
    assert palette.nearest(0x000000) == palette.OFF
    assert palette.of_fl_colour(0x000000, palette.AMBER) == palette.AMBER


def test_negative_fl_colours_are_masked():
    assert palette.nearest(-0x1000000 | 0xFF0000) == palette.nearest(0xFF0000)


def test_dimmed_stays_dark_and_in_hue_block():
    assert palette.dimmed(palette.RED) == palette.DIM_RED
    assert palette.dimmed(palette.WHITE) == palette.DIM_WHITE
    assert palette.dimmed(palette.OFF) == palette.OFF
    for i in range(1, 128):
        d = palette.dimmed(i)
        assert 1 <= d <= 63
        assert d <= palette.WHITE or d % 4 == 3


def test_rgb_of():
    assert palette.rgb_of(3) == 0xFFFFFF
    assert palette.rgb_of(128 + 3) == 0xFFFFFF

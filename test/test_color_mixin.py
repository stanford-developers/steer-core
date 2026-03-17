# SPDX-FileCopyrightText: 2024-2026 Nicholas Siemons
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Tests for steer_core.Mixins.Colors.ColorMixin."""

import pytest

from steer_core.Mixins.Colors import ColorMixin


class TestRgbTupleToHex:

    def test_black(self):
        assert ColorMixin.rgb_tuple_to_hex((0, 0, 0)) == "#000000"

    def test_white(self):
        assert ColorMixin.rgb_tuple_to_hex((255, 255, 255)) == "#ffffff"

    def test_red(self):
        assert ColorMixin.rgb_tuple_to_hex((255, 0, 0)) == "#ff0000"

    def test_arbitrary_color(self):
        assert ColorMixin.rgb_tuple_to_hex((76, 120, 168)) == "#4c78a8"


class TestGetColorway:

    def test_two_colors(self):
        result = ColorMixin.get_colorway("#000000", "#ffffff", 2)
        assert len(result) == 2
        assert result[0] == "#000000"
        assert result[-1] == "#ffffff"

    def test_gradient_length(self):
        result = ColorMixin.get_colorway("#ff0000", "#0000ff", 5)
        assert len(result) == 5

    def test_single_color(self):
        result = ColorMixin.get_colorway("#ff0000", "#0000ff", 1)
        assert len(result) == 1


class TestAdjustFillOpacity:

    def test_hex_to_rgba(self):
        result = ColorMixin.adjust_fill_opacity("#ff0000", 0.5)
        assert "rgba(" in result
        assert "0.5" in result

    def test_rgb_to_rgba(self):
        result = ColorMixin.adjust_fill_opacity("rgb(255, 0, 0)", 0.3)
        assert "rgba(255, 0, 0, 0.3)" == result

    def test_rgba_updates_opacity(self):
        result = ColorMixin.adjust_fill_opacity("rgba(255, 0, 0, 1.0)", 0.5)
        assert "0.5" in result

    def test_empty_string_passthrough(self):
        assert ColorMixin.adjust_fill_opacity("", 0.5) == ""

    def test_named_color_passthrough(self):
        assert ColorMixin.adjust_fill_opacity("red", 0.5) == "red"


class TestHexToRgba:

    def test_six_char_hex(self):
        result = ColorMixin._hex_to_rgba("#FF0000", 0.5)
        assert result == "rgba(255, 0, 0, 0.5)"

    def test_three_char_hex(self):
        result = ColorMixin._hex_to_rgba("#F00", 0.8)
        assert "rgba(" in result

    def test_invalid_hex_returns_original(self):
        result = ColorMixin._hex_to_rgba("#ZZZZZZ", 0.5)
        assert result == "ZZZZZZ"  # lstrip removes #


class TestGetColorFormat:

    def test_hex(self):
        assert ColorMixin.get_color_format("#ff0000") == "hex"

    def test_rgb(self):
        assert ColorMixin.get_color_format("rgb(255,0,0)") == "rgb"

    def test_rgba(self):
        assert ColorMixin.get_color_format("rgba(255,0,0,1)") == "rgba"

    def test_hsl(self):
        assert ColorMixin.get_color_format("hsl(0,100%,50%)") == "hsl"

    def test_named(self):
        assert ColorMixin.get_color_format("red") == "named"

    def test_empty_string(self):
        assert ColorMixin.get_color_format("") == "unknown"

    def test_none(self):
        assert ColorMixin.get_color_format(None) == "unknown"

    def test_non_string(self):
        assert ColorMixin.get_color_format(123) == "unknown"


class TestValidateOpacity:

    def test_valid_opacity(self):
        ColorMixin.validate_opacity(0.5)  # Should not raise

    def test_zero_opacity(self):
        ColorMixin.validate_opacity(0.0)

    def test_one_opacity(self):
        ColorMixin.validate_opacity(1.0)

    def test_negative_raises(self):
        with pytest.raises(ValueError):
            ColorMixin.validate_opacity(-0.1)

    def test_above_one_raises(self):
        with pytest.raises(ValueError):
            ColorMixin.validate_opacity(1.1)

    def test_non_numeric_raises(self):
        with pytest.raises(ValueError):
            ColorMixin.validate_opacity("half")

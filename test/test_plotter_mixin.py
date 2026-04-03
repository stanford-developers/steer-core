# SPDX-FileCopyrightText: 2024-2026 Stanford University
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Tests for steer_core.Mixins.Plotter.PlotterMixin."""

import pytest

from steer_core.Mixins.Plotter import PlotterMixin


class TestHexToRgb:

    def test_basic(self):
        assert PlotterMixin.hex_to_rgb("#4C78A8") == (76, 120, 168)

    def test_black(self):
        assert PlotterMixin.hex_to_rgb("#000000") == (0, 0, 0)

    def test_white(self):
        assert PlotterMixin.hex_to_rgb("#FFFFFF") == (255, 255, 255)


class TestRgbToHex:

    def test_basic(self):
        assert PlotterMixin.rgb_to_hex((76, 120, 168)) == "#4c78a8"


class TestLightenColor:

    def test_no_lighten(self):
        assert PlotterMixin.lighten_color("#000000", 0) == "#000000"

    def test_full_lighten(self):
        assert PlotterMixin.lighten_color("#000000", 1) == "#ffffff"

    def test_partial_lighten(self):
        result = PlotterMixin.lighten_color("#000000", 0.5)
        # Should be close to mid-gray
        assert result.startswith("#")


class TestHexToRgba:

    def test_basic(self):
        result = PlotterMixin.hex_to_rgba("#FF0000", 0.5)
        assert result == "rgba(255, 0, 0, 0.5)"

    def test_full_opacity(self):
        result = PlotterMixin.hex_to_rgba("#FF0000")
        assert result == "rgba(255, 0, 0, 1.0)"


class TestDefaultPalette:

    def test_has_ten_colors(self):
        assert len(PlotterMixin.DEFAULT_PALETTE) == 10

    def test_colors_are_hex(self):
        for color in PlotterMixin.DEFAULT_PALETTE:
            assert color.startswith("#")
            assert len(color) == 7


class TestAxisConfigs:

    def test_scatter_x_axis_has_grid(self):
        assert "showgrid" in PlotterMixin.SCATTER_X_AXIS

    def test_schematic_x_axis_has_anchor(self):
        assert "scaleanchor" in PlotterMixin.SCHEMATIC_X_AXIS

    def test_bottom_legend(self):
        assert PlotterMixin.BOTTOM_LEGEND["orientation"] == "h"

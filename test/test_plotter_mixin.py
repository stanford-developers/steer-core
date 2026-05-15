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


class TestPlotBreakdownSunburst:

    def test_nested_totals(self):
        data = {"A": 10, "B": {"B1": 3, "B2": 7}}
        fig = PlotterMixin.plot_breakdown_sunburst(data, root_label="Root")

        sunburst = fig.data[0]
        root_idx = list(sunburst.ids).index("Root")

        assert sunburst.values[root_idx] == 20.0

    def test_sorts_siblings_by_contribution(self):
        data = {"Small": 1, "Large": 10, "Medium": 5}
        fig = PlotterMixin.plot_breakdown_sunburst(data)

        sunburst = fig.data[0]

        assert list(sunburst.labels)[1:4] == ["Large", "Medium", "Small"]

    def test_hover_text_includes_parent_and_total_percentages(self):
        data = {"Parent": {"Child": 5, "Other": 5}, "Sibling": 10}
        fig = PlotterMixin.plot_breakdown_sunburst(data, unit="g")

        sunburst = fig.data[0]
        child_idx = list(sunburst.ids).index("Parent/Child")
        child_hover = sunburst.customdata[child_idx]

        assert "5.00 g" in child_hover
        assert "50.0% of parent" in child_hover
        assert "25.0% of total" in child_hover

    def test_segment_colors_and_borders_are_populated(self):
        data = {"A": 10, "B": {"B1": 3, "B2": 7}}
        fig = PlotterMixin.plot_breakdown_sunburst(data)

        sunburst = fig.data[0]

        assert len(sunburst.marker.colors) == len(sunburst.labels)
        assert sunburst.marker.line.color == "white"
        assert sunburst.marker.line.width == 1.5

    def test_branch_color_map_colors_matching_branches_and_descendants(self):
        data = {
            "Electrode Assembly": {
                "Cathode": {"Coating": 6},
                "Anode": {"Coating": 4},
            },
        }
        fig = PlotterMixin.plot_breakdown_sunburst(
            data,
            branch_color_map={"Cathode": "#2563eb", "Anode": "#16a34a"},
        )

        sunburst = fig.data[0]
        ids = list(sunburst.ids)
        colors = list(sunburst.marker.colors)

        cathode_idx = ids.index("Electrode Assembly/Cathode")
        cathode_coating_idx = ids.index("Electrode Assembly/Cathode/Coating")
        anode_idx = ids.index("Electrode Assembly/Anode")

        assert colors[cathode_idx] == "#2563eb"
        assert colors[cathode_coating_idx] != colors[anode_idx]
        assert colors[anode_idx] == "#16a34a"

    def test_label_only_text_default_keeps_long_labels_available(self):
        fig = PlotterMixin.plot_breakdown_sunburst({"Electrode Assembly": 10})

        sunburst = fig.data[0]

        assert sunburst.textinfo == "label"
        assert sunburst.insidetextorientation == "horizontal"
        assert fig.layout.uniformtext.mode == "show"

    def test_long_labels_wrap_for_sunburst_display(self):
        fig = PlotterMixin.plot_breakdown_sunburst({"Electrode Assembly": 10})

        sunburst = fig.data[0]

        assert "Electrode<br>Assembly" in list(sunburst.labels)
        assert "Electrode Assembly" in list(sunburst.ids)

    def test_click_transition_is_enabled(self):
        fig = PlotterMixin.plot_breakdown_sunburst({"A": {"A1": 1}})

        assert fig.layout.transition.duration == 350
        assert fig.layout.transition.easing == "cubic-in-out"

    def test_empty_breakdown_returns_placeholder_figure(self):
        fig = PlotterMixin.plot_breakdown_sunburst({}, title="Empty Breakdown")

        assert len(fig.data) == 0
        assert fig.layout.annotations[0].text == "No empty breakdown data available"

    def test_layout_kwargs_can_override_defaults(self):
        fig = PlotterMixin.plot_breakdown_sunburst(
            {"A": 1},
            paper_bgcolor="#f8fafc",
            margin=dict(t=10, r=8, b=6, l=4),
        )

        assert fig.layout.paper_bgcolor == "#f8fafc"
        assert fig.layout.margin.t == 10

# SPDX-FileCopyrightText: 2024-2026 Stanford University
# SPDX-License-Identifier: AGPL-3.0-or-later

from __future__ import annotations

from typing import Any, Callable

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from steer_core.Mixins.Colors import ColorMixin
from steer_core.Mixins.Coordinates import CoordinateMixin


class PlotterMixin:

    DEFAULT_PALETTE = [
        "#4C78A8", "#F58518", "#E45756", "#72B7B2",
        "#54A24B", "#EECA3B", "#B279A2", "#FF9DA6",
        "#9D755D", "#BAB0AC",
    ]

    SCATTER_X_AXIS = dict(
        showgrid=True,
        gridcolor="rgba(128, 128, 128, 0.2)",
        gridwidth=1,
        zeroline=True,
        zerolinecolor="rgba(0, 0, 0, 0.5)",
        zerolinewidth=1,
    )

    SCATTER_Y_AXIS = dict(
        showgrid=True,
        gridcolor="rgba(128, 128, 128, 0.2)",
        gridwidth=1,
        zeroline=True,
        zerolinecolor="rgba(0, 0, 0, 0.5)",
        zerolinewidth=1,
    )

    SCHEMATIC_X_AXIS = dict(
        zeroline=False,
        scaleanchor="y",
        title="X (mm)"
    )

    SCHEMATIC_Y_AXIS = dict(
        zeroline=False,
        title="Y (mm)"
    )

    SCHEMATIC_Z_AXIS = dict(
        zeroline=False,
        scaleanchor="x",
        title="Z (mm)"
    )

    BOTTOM_LEGEND = dict(
        orientation="h",
        yanchor="top",
        y=-0.3,
        xanchor="center",
        x=0.5,
    )

    # ── Colour utilities (partially delegated to ColorMixin) ────────────

    @staticmethod
    def hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
        """Convert a hex colour string (e.g. ``'#4C78A8'``) to an ``(R, G, B)`` tuple."""
        hex_color = hex_color.lstrip("#")
        return tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))

    @staticmethod
    def rgb_to_hex(rgb: tuple[int, int, int]) -> str:
        """Convert an ``(R, G, B)`` tuple to a hex colour string."""
        return ColorMixin.rgb_tuple_to_hex(rgb)

    @staticmethod
    def lighten_color(hex_color: str, factor: float) -> str:
        """Lighten *hex_color* by blending towards white.

        Args:
            hex_color: Hex colour string, e.g. ``'#4C78A8'``.
            factor: Blend factor — ``0`` returns the original colour, ``1`` returns white.
        """
        r, g, b = PlotterMixin.hex_to_rgb(hex_color)
        r = int(r + (255 - r) * factor)
        g = int(g + (255 - g) * factor)
        b = int(b + (255 - b) * factor)
        return ColorMixin.rgb_tuple_to_hex((r, g, b))

    @staticmethod
    def hex_to_rgba(hex_color: str, alpha: float = 1.0) -> str:
        """Convert a hex colour string to an ``rgba()`` CSS string."""
        return ColorMixin._hex_to_rgba(hex_color, alpha)

    # ── Internal helpers ──────────────────────────────────────────────

    @staticmethod
    def _apply_layout_defaults(
        fig: go.Figure,
        layout_defaults: dict[str, Any] | None = None,
    ) -> go.Figure:
        """Apply an optional dictionary of layout overrides to *fig*."""
        if layout_defaults and fig is not None and hasattr(fig, "update_layout"):
            fig.update_layout(**layout_defaults)
        return fig

    # ── Component trace (existing) ────────────────────────────────────

    @staticmethod
    def create_component_trace(
            components: list | object,
            coord_attr: str,
            name: str,
            line_width: float,
            color_func: Callable,
            unit_conversion_factor: float,
            order_clockwise: str | None = None,
            gl: bool = False,
            ) -> go.Scatter | go.Scattergl | None:
        """Create a single trace for a component or group of components with NaN separators.

        Args:
            components: Single component or list of components to process.
            coord_attr: Attribute path for coordinates (e.g., '_a_side_coating_coordinates').
            name: Name for the trace.
            line_width: Width of the trace line.
            color_func: Function to get color from component.
            unit_conversion_factor: Factor to convert coordinates to desired units.
            order_clockwise: Plane for clockwise ordering ('xy', 'xz', 'yz') or None to disable,
                by default None.
            gl: Whether to use WebGL rendering.

        Returns:
            Plotly scatter trace or None if no valid coordinates.
        """
        # Convert single component to list for uniform processing
        if not isinstance(components, list):
            components = [components]
            
        if not components:
            return None
            
        # Extract coordinates using nested getattr for dot notation
        coord_arrays = []
        for component in components:
            coords = component
            # Handle nested attributes like '_current_collector._body_coordinates'
            for attr_part in coord_attr.split('.'):
                coords = getattr(coords, attr_part)
                
            if coords is not None and len(coords) > 0:
                coord_arrays.append(coords)

        if not coord_arrays:
            return None
        
        # Concatenate coordinates with NaN separators
        combined_coords = CoordinateMixin.concat_with_nan_separators(coord_arrays)
        
        # Order coordinates clockwise if requested
        if order_clockwise is not None:
            combined_coords = CoordinateMixin.order_coordinates_clockwise_numpy(combined_coords, plane=order_clockwise)
        
        # Convert to mm and extract y,z coordinates directly (avoid DataFrame overhead)
        y_coords = combined_coords[:, 1] * unit_conversion_factor
        z_coords = combined_coords[:, 2] * unit_conversion_factor
        
        # Create trace
        if gl:
            return go.Scattergl(
                x=y_coords,
                y=z_coords,
                mode="lines",
                name=name,
                line={'width': line_width, 'color': "black"},
                fill="toself",
                fillcolor=color_func(components[0]),
                legendgroup=name,
                showlegend=True,
            )
        else:
            return go.Scatter(
                x=y_coords,
                y=z_coords,
                mode="lines",
                name=name,
                line={'width': line_width, 'color': "black"},
                fill="toself",
                fillcolor=color_func(components[0]),
                legendgroup=name,
                showlegend=True,
            )

    @staticmethod
    def plot_breakdown_sunburst(
        breakdown_dict: dict[str, Any],
        title: str = "Breakdown",
        root_label: str = "Total",
        unit: str = "",
        colorway: list[str] = None,
        sort_siblings: bool = True,
        textinfo: str = "label",
        branch_color_map: dict[str, str] | None = None,
        label_wrap_width: int = 14,
        **kwargs,
    ) -> go.Figure:
        """Create a sunburst plot for any generic nested breakdown dictionary.

        Args:
            breakdown_dict: Nested dictionary where values can be either numbers or nested
                dictionaries. Each nesting level becomes a ring in the sunburst plot.
            title: Title for the plot. Defaults to "Breakdown".
            root_label: Label for the root node. Defaults to "Total".
            unit: Unit string to display in hover text (e.g., "g", "kg", "%"). Defaults to "".
            colorway: List of colors to use for the inner ring. If None, uses Plotly's default
                colorway. Defaults to None.
            sort_siblings: Sort sibling nodes by descending contribution. Defaults to True.
            textinfo: Text displayed on sunburst segments. Defaults to label only, keeping
                longer labels readable.
            branch_color_map: Optional mapping from label text to a base color. Matching
                labels and their descendants use the mapped color.
            label_wrap_width: Wrap labels longer than this many characters onto multiple
                lines. Set to 0 or None to disable wrapping. Defaults to 14.

        Returns:
            Plotly sunburst figure.
        """
        
        # Default Plotly colorway if none provided
        if colorway is None:
            colorway = [
                '#636EFA', '#EF553B', '#00CC96', '#AB63FA', '#FFA15A',
                '#19D3F3', '#FF6692', '#B6E880', '#FF97FF', '#FECB52'
            ]

        def _calculate_subtotal(data: dict[str, Any]) -> float:
            """Calculate the total value for a dictionary (sum of all nested numeric values)"""
            total = 0.0
            for value in data.values():
                if isinstance(value, dict):
                    total += _calculate_subtotal(value)
                elif isinstance(value, (int, float)):
                    total += float(value)
            return total

        def _node_value(value: Any) -> float:
            """Return the numeric contribution for a scalar or nested node."""
            if isinstance(value, dict):
                return _calculate_subtotal(value)
            if isinstance(value, (int, float)):
                return float(value)
            return 0.0

        def _iter_items(data: dict[str, Any]) -> list[tuple[str, Any]]:
            """Return display-ordered breakdown items."""
            items = list(data.items())
            if sort_siblings:
                items.sort(key=lambda item: _node_value(item[1]), reverse=True)
            return items

        normalized_branch_color_map = {
            key.lower(): value for key, value in (branch_color_map or {}).items()
        }

        def _branch_color_for_label(label: str) -> str | None:
            """Return a semantic branch color for labels such as Cathode or Anode."""
            normalized_label = label.lower()
            for key, color in normalized_branch_color_map.items():
                if key == normalized_label or key in normalized_label:
                    return color
            return None

        def _wrap_label(label: str) -> str:
            """Insert line breaks so long sunburst labels remain visible."""
            if not label_wrap_width or len(label) <= label_wrap_width:
                return label

            words = label.split()
            if len(words) <= 1:
                return label

            lines = []
            current_line = words[0]
            for word in words[1:]:
                candidate = f"{current_line} {word}"
                if len(candidate) > label_wrap_width:
                    lines.append(current_line)
                    current_line = word
                else:
                    current_line = candidate

            lines.append(current_line)
            return "<br>".join(lines)

        def _prepare_sunburst_data(
            data: dict[str, Any],
            parent_id: str = "",
            current_path: str = "",
            depth: int = 1,
            parent_total: float = 0.0,
            first_level_ancestor: str | None = None,
            inherited_branch_color: str | None = None,
        ) -> tuple[
            list[str],
            list[str],
            list[str],
            list[float],
            list[int],
            list[float],
            list[str | None],
            list[str | None],
        ]:
            """Recursively prepare data for sunburst plot with proper hierarchy"""
            ids = []
            labels = []
            parents = []
            values = []
            depths = []
            parent_values = []
            first_level_ancestors = []
            semantic_branch_colors = []

            for key, value in _iter_items(data):
                # Create unique ID for this node
                node_id = f"{current_path}/{key}" if current_path else key
                subtotal = _node_value(value)
                ancestor = key if depth == 1 else first_level_ancestor
                branch_color = _branch_color_for_label(key) or inherited_branch_color

                ids.append(node_id)
                labels.append(key)
                parents.append(parent_id)
                values.append(subtotal)
                depths.append(depth)
                parent_values.append(parent_total)
                first_level_ancestors.append(ancestor)
                semantic_branch_colors.append(branch_color)

                if isinstance(value, dict):
                    # Recursively process nested dictionary
                    (
                        nested_ids,
                        nested_labels,
                        nested_parents,
                        nested_values,
                        nested_depths,
                        nested_parent_values,
                        nested_first_level_ancestors,
                        nested_semantic_branch_colors,
                    ) = _prepare_sunburst_data(
                        value,
                        parent_id=node_id,
                        current_path=node_id,
                        depth=depth + 1,
                        parent_total=subtotal,
                        first_level_ancestor=ancestor,
                        inherited_branch_color=branch_color,
                    )

                    # Add nested data to our lists
                    ids.extend(nested_ids)
                    labels.extend(nested_labels)
                    parents.extend(nested_parents)
                    values.extend(nested_values)
                    depths.extend(nested_depths)
                    parent_values.extend(nested_parent_values)
                    first_level_ancestors.extend(nested_first_level_ancestors)
                    semantic_branch_colors.extend(nested_semantic_branch_colors)

            return (
                ids,
                labels,
                parents,
                values,
                depths,
                parent_values,
                first_level_ancestors,
                semantic_branch_colors,
            )

        # Calculate total value for root node
        total_value = _calculate_subtotal(breakdown_dict)

        if not breakdown_dict or total_value <= 0:
            fig = go.Figure()
            layout_defaults = dict(
                title=dict(text=title, x=0.5, font=dict(size=18)),
                annotations=[
                    dict(
                        text=f"No {title.lower()} data available",
                        showarrow=False,
                        x=0.5,
                        y=0.5,
                        xref="paper",
                        yref="paper",
                        font=dict(size=15, color="#64748B"),
                    )
                ],
                paper_bgcolor="white",
                plot_bgcolor="white",
                margin=dict(t=64, r=16, b=16, l=16),
            )
            layout_defaults.update(kwargs)
            fig.update_layout(**layout_defaults)
            return fig

        # Prepare hierarchical data starting with root
        (
            ids,
            labels,
            parents,
            values,
            depths,
            parent_values,
            first_level_ancestors,
            semantic_branch_colors,
        ) = _prepare_sunburst_data(
            breakdown_dict, parent_id="", parent_total=total_value
        )

        # Add root node at the beginning
        ids.insert(0, root_label)
        labels.insert(0, root_label)
        parents.insert(0, "")
        values.insert(0, total_value)
        depths.insert(0, 0)
        parent_values.insert(0, total_value)
        first_level_ancestors.insert(0, None)
        semantic_branch_colors.insert(0, None)

        # Update parent references to point to root
        for i in range(1, len(parents)):
            if parents[i] == "":
                parents[i] = root_label

        # Generate colors based on alphabetical ordering and depth
        # Get first-level keys (children of root) and sort alphabetically
        first_level_keys = sorted([key for key in breakdown_dict.keys()])
        
        # Assign base colors to first-level keys
        key_to_base_color = {}
        for i, key in enumerate(first_level_keys):
            key_to_base_color[key] = colorway[i % len(colorway)]
        
        # Assign colors to all nodes
        marker_colors = []
        
        for label, depth, ancestor_label, branch_color in zip(
            labels,
            depths,
            first_level_ancestors,
            semantic_branch_colors,
        ):
            if depth == 0:
                # Root node - use neutral color
                marker_colors.append('#E2E8F0')
            elif branch_color:
                lighten_factor = max(0.0, min(0.78, (depth - 2) * 0.22))
                marker_colors.append(PlotterMixin.lighten_color(branch_color, lighten_factor))
            elif depth == 1:
                # First level - use assigned base color
                marker_colors.append(key_to_base_color[label])
            else:
                if ancestor_label and ancestor_label in key_to_base_color:
                    base_color = key_to_base_color[ancestor_label]
                    # Lighten based on depth (depth 2 gets 0.3, depth 3 gets 0.5, depth 4 gets 0.7, etc.)
                    lighten_factor = 0.2 + (depth - 1) * 0.25
                    lighten_factor = min(lighten_factor, 0.85)  # Cap at 0.85 to avoid too pale
                    marker_colors.append(PlotterMixin.lighten_color(base_color, lighten_factor))
                else:
                    # Fallback to neutral color
                    marker_colors.append('#DDDDDD')

        display_labels = [_wrap_label(label) for label in labels]

        # Create custom hover text with percentages
        hover_text = []
        for label, value, parent_value in zip(labels, values, parent_values):
            total_percentage = (value / total_value * 100) if total_value > 0 else 0
            parent_percentage = (value / parent_value * 100) if parent_value > 0 else 0
            if label == root_label:
                unit_str = f" {unit}" if unit else ""
                hover_text.append(f"<b>{root_label}</b><br>{value:.2f}{unit_str}")
            else:
                unit_str = f" {unit}" if unit else ""
                hover_text.append(
                    f"<b>{label}</b><br>"
                    f"{value:.2f}{unit_str}<br>"
                    f"{parent_percentage:.1f}% of parent<br>"
                    f"{total_percentage:.1f}% of total"
                )

        # Create the sunburst plot
        fig = go.Figure(
            go.Sunburst(
                ids=ids,
                labels=display_labels,
                parents=parents,
                values=values,
                branchvalues="total",
                hovertemplate="%{customdata}<extra></extra>",
                customdata=hover_text,
                marker=dict(colors=marker_colors, line=dict(color="white", width=1.5)),
                insidetextorientation="horizontal",
                textinfo=textinfo,
            )
        )

        layout_defaults = dict(
            title=dict(text=title, x=0.5, font=dict(size=18)),
            font_size=13,
            margin=dict(t=64, r=16, b=16, l=16),
            uniformtext=dict(minsize=9, mode="show"),
            paper_bgcolor="white",
            plot_bgcolor="white",
            transition=dict(duration=350, easing="cubic-in-out"),
        )
        layout_defaults.update(kwargs)
        fig.update_layout(**layout_defaults)

        return fig

    # ── Generic statistical plots ─────────────────────────────────────

    @staticmethod
    def plot_scatter(
        df: pd.DataFrame,
        x: str,
        y: str,
        hover_name: str = None,
        custom_data: list[str] | None = None,
        color: str | None = None,
        size: str | None = None,
        size_max: int = 30,
        template: str = "presentation",
        layout_defaults: dict[str, Any] | None = None,
        **kwargs,
    ) -> go.Figure:
        """Create a styled 2-D scatter plot.

        Args:
            df: DataFrame containing the columns referenced by *x*, *y*, etc.
            x: Column name for the X axis.
            y: Column name for the Y axis.
            hover_name: Column whose values appear as the main hover label.
            custom_data: Column names to include in ``customdata`` for click handlers.
            color: Column name for colour grouping.
            size: Column name for marker-size mapping.
            size_max: Maximum marker size when *size* is set.
            template: Plotly template name.
            layout_defaults: Additional ``fig.update_layout`` overrides applied last.

        Returns:
            Plotly figure.
        """
        fig = px.scatter(
            df,
            x=x,
            y=y,
            hover_name=hover_name,
            custom_data=custom_data or [],
            color=color,
            size=size,
            size_max=size_max if size else None,
            color_discrete_map={} if color else None,
            template=template,
            **kwargs,
        )
        fig.update_layout(xaxis_title=x, yaxis_title=y)
        return PlotterMixin._apply_layout_defaults(fig, layout_defaults)

    @staticmethod
    def plot_grouped_scatter(
        groups,
        x_values,
        y_values,
        x_label: str = "X",
        y_label: str = "Y",
        group_label: str = "Group",
        palette: list[str] | None = None,
        template: str = "presentation",
        layout_defaults: dict[str, Any] | None = None,
    ) -> go.Figure:
        """Create a scatter plot of group means with std dev error bars.

        Args:
            groups: Parallel list of group labels (one per observation).
            x_values: Parallel list of numeric X values.
            y_values: Parallel list of numeric Y values.
            x_label: Human-readable X-axis label.
            y_label: Human-readable Y-axis label.
            group_label: Human-readable label for the grouping variable.
            palette: Hex colour palette. Falls back to ``DEFAULT_PALETTE``.
            template: Plotly template name.
            layout_defaults: Additional ``fig.update_layout`` overrides applied last.

        Returns:
            Plotly figure.
        """
        palette = palette or PlotterMixin.DEFAULT_PALETTE
        df = pd.DataFrame({"_group": groups, "_x": x_values, "_y": y_values})
        agg = df.groupby("_group", sort=True).agg(
            x_mean=("_x", "mean"), x_std=("_x", "std"),
            y_mean=("_y", "mean"), y_std=("_y", "std"),
            count=("_x", "size"),
        ).reset_index()
        agg[["x_std", "y_std"]] = agg[["x_std", "y_std"]].fillna(0)

        fig = go.Figure()
        for i, row in agg.iterrows():
            clr = palette[i % len(palette)]
            fig.add_trace(go.Scatter(
                x=[row["x_mean"]],
                y=[row["y_mean"]],
                error_x=dict(type="data", array=[row["x_std"]], visible=True),
                error_y=dict(type="data", array=[row["y_std"]], visible=True),
                mode="markers+text",
                marker=dict(size=12, color=clr),
                text=[f"n={int(row['count'])}"],
                textposition="top center",
                name=str(row["_group"]),
                hovertemplate=(
                    f"<b>{row['_group']}</b><br>"
                    f"{x_label}: %{{x:.4g}} \u00b1 {row['x_std']:.4g}<br>"
                    f"{y_label}: %{{y:.4g}} \u00b1 {row['y_std']:.4g}<br>"
                    f"n={int(row['count'])}<extra></extra>"
                ),
            ))
        fig.update_layout(
            xaxis_title=x_label,
            yaxis_title=y_label,
            template=template,
        )
        return PlotterMixin._apply_layout_defaults(fig, layout_defaults)

    @staticmethod
    def plot_scatter_3d(
        df: pd.DataFrame,
        x: str,
        y: str,
        z: str,
        hover_name: str = None,
        custom_data: list[str] | None = None,
        color: str | None = None,
        size: str | None = None,
        size_max: int = 30,
        template: str = "presentation",
        layout_defaults: dict[str, Any] | None = None,
        **kwargs,
    ) -> go.Figure:
        """Create a styled 3-D scatter plot.

        Args:
            df: DataFrame containing the columns referenced by *x*, *y*, *z*, etc.
            x: Column name for the X axis.
            y: Column name for the Y axis.
            z: Column name for the Z axis.
            hover_name: Column whose values appear as the main hover label.
            custom_data: Column names to include in ``customdata``.
            color: Column name for colour grouping.
            size: Column name for marker-size mapping.
            size_max: Maximum marker size when *size* is set.
            template: Plotly template name.
            layout_defaults: Additional ``fig.update_layout`` overrides applied last.

        Returns:
            Plotly figure.
        """
        fig = px.scatter_3d(
            df,
            x=x,
            y=y,
            z=z,
            hover_name=hover_name,
            custom_data=custom_data or [],
            color=color,
            size=size,
            size_max=size_max if size else None,
            color_discrete_map={} if color else None,
            template=template,
            **kwargs,
        )
        fig.update_layout(
            scene=dict(
                xaxis_title=x,
                yaxis_title=y,
                zaxis_title=z,
            )
        )
        return PlotterMixin._apply_layout_defaults(fig, layout_defaults)

    @staticmethod
    def plot_grouped_scatter_3d(
        groups,
        x_values,
        y_values,
        z_values,
        x_label: str = "X",
        y_label: str = "Y",
        z_label: str = "Z",
        group_label: str = "Group",
        palette: list[str] | None = None,
        template: str = "presentation",
        layout_defaults: dict[str, Any] | None = None,
    ) -> go.Figure:
        """Create a 3-D scatter plot of group means with std dev error bars.

        Args:
            groups: Parallel list of group labels.
            x_values: Parallel list of numeric X values.
            y_values: Parallel list of numeric Y values.
            z_values: Parallel list of numeric Z values.
            x_label: Human-readable X-axis label.
            y_label: Human-readable Y-axis label.
            z_label: Human-readable Z-axis label.
            group_label: Human-readable label for the grouping variable.
            palette: Hex colour palette. Falls back to ``DEFAULT_PALETTE``.
            template: Plotly template name.
            layout_defaults: Additional ``fig.update_layout`` overrides applied last.

        Returns:
            Plotly figure.
        """
        palette = palette or PlotterMixin.DEFAULT_PALETTE
        df = pd.DataFrame({
            "_group": groups, "_x": x_values,
            "_y": y_values, "_z": z_values,
        })
        agg = df.groupby("_group", sort=True).agg(
            x_mean=("_x", "mean"), x_std=("_x", "std"),
            y_mean=("_y", "mean"), y_std=("_y", "std"),
            z_mean=("_z", "mean"), z_std=("_z", "std"),
            count=("_x", "size"),
        ).reset_index()
        agg[["x_std", "y_std", "z_std"]] = agg[["x_std", "y_std", "z_std"]].fillna(0)

        fig = go.Figure()
        for i, row in agg.iterrows():
            clr = palette[i % len(palette)]
            fig.add_trace(go.Scatter3d(
                x=[row["x_mean"]],
                y=[row["y_mean"]],
                z=[row["z_mean"]],
                error_x=dict(type="data", array=[row["x_std"]], visible=True),
                error_y=dict(type="data", array=[row["y_std"]], visible=True),
                error_z=dict(type="data", array=[row["z_std"]], visible=True),
                mode="markers+text",
                marker=dict(size=8, color=clr),
                text=[f"{row['_group']} (n={int(row['count'])})"],
                name=str(row["_group"]),
                hovertemplate=(
                    f"<b>{row['_group']}</b><br>"
                    f"{x_label}: %{{x:.4g}} \u00b1 {row['x_std']:.4g}<br>"
                    f"{y_label}: %{{y:.4g}} \u00b1 {row['y_std']:.4g}<br>"
                    f"{z_label}: %{{z:.4g}} \u00b1 {row['z_std']:.4g}<br>"
                    f"n={int(row['count'])}<extra></extra>"
                ),
            ))
        fig.update_layout(
            scene=dict(
                xaxis_title=x_label,
                yaxis_title=y_label,
                zaxis_title=z_label,
            ),
            template=template,
        )
        return PlotterMixin._apply_layout_defaults(fig, layout_defaults)

    @staticmethod
    def plot_bar(
        x,
        y,
        custom_data=None,
        x_label: str = "X",
        y_label: str = "Y",
        template: str = "presentation",
        layout_defaults: dict[str, Any] | None = None,
        **kwargs,
    ) -> go.Figure:
        """Create a styled bar chart.

        Args:
            x: Values for the X axis.
            y: Values for the Y axis.
            custom_data: Custom data attached to each bar (for click handlers).
            x_label: Human-readable X-axis label.
            y_label: Human-readable Y-axis label.
            template: Plotly template name.
            layout_defaults: Additional ``fig.update_layout`` overrides applied last.

        Returns:
            Plotly figure.
        """
        fig = px.bar(
            x=x,
            y=y,
            custom_data=[custom_data] if custom_data is not None else None,
            labels={"x": x_label, "y": y_label},
            template=template,
            **kwargs,
        )
        fig.update_layout(xaxis_title=x_label, yaxis_title=y_label)
        return PlotterMixin._apply_layout_defaults(fig, layout_defaults)

    @staticmethod
    def plot_grouped_bar(
        groups,
        values,
        y_label: str = "Y",
        group_label: str = "Group",
        palette: list[str] | None = None,
        template: str = "presentation",
        layout_defaults: dict[str, Any] | None = None,
    ) -> go.Figure:
        """Create a bar chart showing mean +/- std dev per group.

        Args:
            groups: Parallel list of group labels (one per observation).
            values: Parallel list of numeric values (one per observation).
            y_label: Human-readable Y-axis label.
            group_label: Human-readable X-axis (group axis) label.
            palette: Hex colour palette. Falls back to ``DEFAULT_PALETTE``.
            template: Plotly template name.
            layout_defaults: Additional ``fig.update_layout`` overrides applied last.

        Returns:
            Plotly figure.
        """
        palette = palette or PlotterMixin.DEFAULT_PALETTE
        df = pd.DataFrame({"_group": groups, "_value": values})
        agg = (
            df.groupby("_group", sort=True)["_value"]
            .agg(["mean", "std", "count"])
            .reset_index()
        )
        agg["std"] = agg["std"].fillna(0)
        colors = [palette[i % len(palette)] for i in range(len(agg))]

        fig = go.Figure(data=[
            go.Bar(
                x=agg["_group"],
                y=agg["mean"],
                error_y=dict(
                    type="data", array=agg["std"].tolist(), visible=True,
                ),
                text=[f"n={n}" for n in agg["count"]],
                textposition="outside",
                marker_color=colors,
            )
        ])
        fig.update_layout(
            xaxis_title=group_label,
            yaxis_title=y_label,
            template=template,
        )
        return PlotterMixin._apply_layout_defaults(fig, layout_defaults)

    @staticmethod
    def plot_histogram(
        x,
        x_label: str = "Value",
        template: str = "presentation",
        layout_defaults: dict[str, Any] | None = None,
        **kwargs,
    ) -> go.Figure:
        """Create a styled histogram.

        Args:
            x: Values to bin.
            x_label: Human-readable axis label.
            template: Plotly template name.
            layout_defaults: Additional ``fig.update_layout`` overrides applied last.

        Returns:
            Plotly figure.
        """
        fig = px.histogram(
            x=x,
            labels={"x": x_label},
            template=template,
            **kwargs,
        )
        fig.update_layout(xaxis_title=x_label, yaxis_title="Count")
        return PlotterMixin._apply_layout_defaults(fig, layout_defaults)

    @staticmethod
    def plot_grouped_histogram(
        groups,
        values,
        x_label: str = "Value",
        palette: list[str] | None = None,
        template: str = "presentation",
        layout_defaults: dict[str, Any] | None = None,
    ) -> go.Figure:
        """Create overlaid histograms, one per group.

        Args:
            groups: Parallel list of group labels.
            values: Parallel list of numeric values.
            x_label: Human-readable axis label.
            palette: Hex colour palette. Falls back to ``DEFAULT_PALETTE``.
            template: Plotly template name.
            layout_defaults: Additional ``fig.update_layout`` overrides applied last.

        Returns:
            Plotly figure.
        """
        palette = palette or PlotterMixin.DEFAULT_PALETTE
        df = pd.DataFrame({"_group": groups, "_value": values})
        fig = go.Figure()
        for i, (grp, sub) in enumerate(
            sorted(df.groupby("_group"), key=lambda x: x[0])
        ):
            fig.add_trace(go.Histogram(
                x=sub["_value"],
                name=str(grp),
                opacity=0.7,
                marker_color=palette[i % len(palette)],
            ))
        fig.update_layout(
            barmode="overlay",
            xaxis_title=x_label,
            yaxis_title="Count",
            template=template,
        )
        return PlotterMixin._apply_layout_defaults(fig, layout_defaults)

    @staticmethod
    def plot_pdf(
        values,
        label: str = "Value",
        color_groups: dict[str, list[float]] | None = None,
        template: str = "presentation",
        layout_defaults: dict[str, Any] | None = None,
    ) -> go.Figure:
        """Create a probability-density histogram (one trace per colour group).

        Args:
            values: Values to bin (used when *color_groups* is ``None``).
            label: Human-readable axis label.
            color_groups: Mapping ``{group_name: [values]}`` for overlaid per-group traces.
            template: Plotly template name.
            layout_defaults: Additional ``fig.update_layout`` overrides applied last.

        Returns:
            Plotly figure.
        """
        fig = go.Figure()
        if color_groups:
            for group_name, group_vals in color_groups.items():
                fig.add_trace(
                    go.Histogram(
                        x=group_vals,
                        histnorm="probability density",
                        name=group_name,
                        opacity=0.7,
                    )
                )
            fig.update_layout(barmode="overlay")
        else:
            fig.add_trace(
                go.Histogram(
                    x=values,
                    histnorm="probability density",
                    name=label,
                )
            )
        fig.update_layout(
            xaxis_title=label,
            yaxis_title="Probability Density",
            template=template,
        )
        return PlotterMixin._apply_layout_defaults(fig, layout_defaults)

    @staticmethod
    def plot_grouped_pdf(
        groups,
        values,
        label: str = "Value",
        palette: list[str] | None = None,
        template: str = "presentation",
        layout_defaults: dict[str, Any] | None = None,
    ) -> go.Figure:
        """Create overlaid probability-density histograms, one per group.

        Args:
            groups: Parallel list of group labels.
            values: Parallel list of numeric values.
            label: Human-readable axis label.
            palette: Hex colour palette. Falls back to ``DEFAULT_PALETTE``.
            template: Plotly template name.
            layout_defaults: Additional ``fig.update_layout`` overrides applied last.

        Returns:
            Plotly figure.
        """
        palette = palette or PlotterMixin.DEFAULT_PALETTE
        df = pd.DataFrame({"_group": groups, "_value": values})
        fig = go.Figure()
        for i, (grp, sub) in enumerate(
            sorted(df.groupby("_group"), key=lambda x: x[0])
        ):
            fig.add_trace(go.Histogram(
                x=sub["_value"],
                histnorm="probability density",
                name=str(grp),
                opacity=0.7,
                marker_color=palette[i % len(palette)],
            ))
        fig.update_layout(
            barmode="overlay",
            xaxis_title=label,
            yaxis_title="Probability Density",
            template=template,
        )
        return PlotterMixin._apply_layout_defaults(fig, layout_defaults)

    @staticmethod
    def plot_box(
        y,
        x=None,
        custom_data=None,
        y_label: str = "Y",
        points: str = "all",
        template: str = "presentation",
        layout_defaults: dict[str, Any] | None = None,
        **kwargs,
    ) -> go.Figure:
        """Create a styled box plot.

        Args:
            y: Values for the Y axis.
            x: Category values for grouping along the X axis.
            custom_data: Custom data attached to each point (for click handlers).
            y_label: Human-readable Y-axis label.
            points: One of ``'all'``, ``'outliers'``, ``'suspectedoutliers'``, or ``False``.
            template: Plotly template name.
            layout_defaults: Additional ``fig.update_layout`` overrides applied last.

        Returns:
            Plotly figure.
        """
        box_kwargs: dict = dict(
            y=y,
            labels={"y": y_label},
            points=points,
            template=template,
            **kwargs,
        )
        if x is not None:
            box_kwargs["x"] = x
        if custom_data is not None:
            box_kwargs["custom_data"] = [custom_data]
        fig = px.box(**box_kwargs)
        fig.update_layout(yaxis_title=y_label)
        return PlotterMixin._apply_layout_defaults(fig, layout_defaults)

    @staticmethod
    def plot_violin(
        y,
        x=None,
        custom_data=None,
        y_label: str = "Y",
        points: str = "all",
        box: bool = True,
        template: str = "presentation",
        layout_defaults: dict[str, Any] | None = None,
        **kwargs,
    ) -> go.Figure:
        """Create a styled violin plot.

        Args:
            y: Values for the Y axis.
            x: Category values for grouping along the X axis.
            custom_data: Custom data attached to each point.
            y_label: Human-readable Y-axis label.
            points: One of ``'all'``, ``'outliers'``, ``'suspectedoutliers'``, or ``False``.
            box: Whether to overlay an inner box-plot.
            template: Plotly template name.
            layout_defaults: Additional ``fig.update_layout`` overrides applied last.

        Returns:
            Plotly figure.
        """
        violin_kwargs: dict = dict(
            y=y,
            labels={"y": y_label},
            points=points,
            box=box,
            template=template,
            **kwargs,
        )
        if x is not None:
            violin_kwargs["x"] = x
        if custom_data is not None:
            violin_kwargs["custom_data"] = [custom_data]
        fig = px.violin(**violin_kwargs)
        fig.update_layout(yaxis_title=y_label)
        return PlotterMixin._apply_layout_defaults(fig, layout_defaults)

    @staticmethod
    def plot_strip(
        y,
        x=None,
        hover_name=None,
        custom_data=None,
        y_label: str = "Y",
        template: str = "presentation",
        layout_defaults: dict[str, Any] | None = None,
        **kwargs,
    ) -> go.Figure:
        """Create a styled strip (jitter) plot.

        Args:
            y: Values for the Y axis.
            x: Category values for grouping along the X axis.
            hover_name: Values to display as the main hover label.
            custom_data: Custom data attached to each point.
            y_label: Human-readable Y-axis label.
            template: Plotly template name.
            layout_defaults: Additional ``fig.update_layout`` overrides applied last.

        Returns:
            Plotly figure.
        """
        strip_kwargs: dict = dict(
            y=y,
            labels={"y": y_label},
            template=template,
            **kwargs,
        )
        if x is not None:
            strip_kwargs["x"] = x
        if hover_name is not None:
            strip_kwargs["hover_name"] = hover_name
        if custom_data is not None:
            strip_kwargs["custom_data"] = [custom_data]
        fig = px.strip(**strip_kwargs)
        fig.update_layout(yaxis_title=y_label)
        return PlotterMixin._apply_layout_defaults(fig, layout_defaults)

    # ── Radar / spider chart ──────────────────────────────────────────

    @staticmethod
    def plot_radar(
        df: pd.DataFrame,
        axis_labels: list[str],
        inverted: dict[str, bool] | None = None,
        color_column: str | None = None,
        name_column: str = "name",
        palette: list[str] | None = None,
        template: str = "presentation",
        layout_defaults: dict[str, Any] | None = None,
    ) -> go.Figure:
        """Create a normalised radar (spider) chart.

        Each row in *df* becomes a ``Scatterpolar`` trace.  Values are
        normalised to 0–1 per axis so properties with very different scales
        are comparable.  Per-spoke tick annotations show the original values.

        Args:
            df: Must contain columns named in *axis_labels* (raw values) and
                *name_column*.  Optionally contains *color_column*.
            axis_labels: Column names in *df* for the radar axes.
            inverted: ``{axis_label: True}`` for axes where *lower* raw values should
                appear *further* from the centre (e.g. cost).  Defaults to
                inverting any axis whose label contains ``"cost"`` (case-insensitive).
            color_column: Column name for categorical colour grouping.
            name_column: Column name used as the trace name / hover label.
            palette: Hex colour palette.  Falls back to ``DEFAULT_PALETTE``.
            template: Plotly template name.
            layout_defaults: Additional ``fig.update_layout`` overrides applied last.

        Returns:
            Plotly figure.
        """
        palette = palette or PlotterMixin.DEFAULT_PALETTE

        if inverted is None:
            inverted = {col: "cost" in col.lower() for col in axis_labels}

        # ── Normalise each axis to 0–1 with padding ──────────────────
        df = df.copy()
        axis_ranges: dict[str, tuple[float, float]] = {}
        for col in axis_labels:
            col_min = df[col].min()
            col_max = df[col].max()
            pad_min = col_min * 0.8 if col_min >= 0 else col_min * 1.2
            pad_max = col_max * 1.2 if col_max >= 0 else col_max * 0.8
            if pad_max - pad_min == 0:
                pad_min, pad_max = col_min - 1, col_max + 1
            axis_ranges[col] = (pad_min, pad_max)
            rng = pad_max - pad_min
            if inverted.get(col, False):
                df[col + "_norm"] = (pad_max - df[col]) / rng
            else:
                df[col + "_norm"] = (df[col] - pad_min) / rng

        norm_cols = [c + "_norm" for c in axis_labels]

        # ── Data traces ───────────────────────────────────────────────
        fig = go.Figure()
        use_color = color_column and color_column in df.columns

        if use_color:
            categories = sorted(df[color_column].unique().tolist())
            cat_colors = {
                c: palette[i % len(palette)]
                for i, c in enumerate(categories)
            }
            for _, r in df.iterrows():
                vals = [r[nc] for nc in norm_cols] + [r[norm_cols[0]]]
                raw_vals = [r[al] for al in axis_labels] + [r[axis_labels[0]]]
                hover = [
                    f"{al}: {rv:.4g}" for al, rv in zip(axis_labels, raw_vals[:-1])
                ]
                hover.append(hover[0])
                cat = r[color_column]
                clr = cat_colors[cat]
                fig.add_trace(
                    go.Scatterpolar(
                        r=vals,
                        theta=axis_labels + [axis_labels[0]],
                        name=r[name_column],
                        fill="toself",
                        fillcolor=PlotterMixin.hex_to_rgba(clr, 0.15),
                        line=dict(color=clr, width=2),
                        marker=dict(size=4, color=clr),
                        customdata=[[r[name_column]] for _ in vals],
                        hovertemplate=(
                            "%{theta}<br>%{text}<br>Cell: "
                            + str(r[name_column])
                            + "<extra></extra>"
                        ),
                        text=hover,
                        legendgroup=str(cat),
                        legendgrouptitle_text=str(cat),
                    )
                )
        else:
            for i, (_, r) in enumerate(df.iterrows()):
                vals = [r[nc] for nc in norm_cols] + [r[norm_cols[0]]]
                raw_vals = [r[al] for al in axis_labels] + [r[axis_labels[0]]]
                hover = [
                    f"{al}: {rv:.4g}" for al, rv in zip(axis_labels, raw_vals[:-1])
                ]
                hover.append(hover[0])
                clr = palette[i % len(palette)]
                fig.add_trace(
                    go.Scatterpolar(
                        r=vals,
                        theta=axis_labels + [axis_labels[0]],
                        name=r[name_column],
                        fill="toself",
                        fillcolor=PlotterMixin.hex_to_rgba(clr, 0.15),
                        line=dict(color=clr, width=2),
                        marker=dict(size=4, color=clr),
                        customdata=[[r[name_column]] for _ in vals],
                        hovertemplate=(
                            "%{theta}<br>%{text}<br>Cell: "
                            + str(r[name_column])
                            + "<extra></extra>"
                        ),
                        text=hover,
                    )
                )

        # ── Per-spoke tick annotations ────────────────────────────────
        tick_fractions = [0.25, 0.5, 0.75, 1.0]
        for col in axis_labels:
            pad_min, pad_max = axis_ranges[col]
            rng = pad_max - pad_min
            for frac in tick_fractions:
                if inverted.get(col, False):
                    raw = pad_max - frac * rng
                else:
                    raw = pad_min + frac * rng
                if abs(raw) >= 100:
                    txt = f"{raw:.0f}"
                elif abs(raw) >= 1:
                    txt = f"{raw:.2f}"
                else:
                    txt = f"{raw:.3g}"
                fig.add_trace(
                    go.Scatterpolar(
                        r=[frac],
                        theta=[col],
                        mode="text",
                        text=[f"  {txt}"],
                        textfont=dict(size=10, color="#555", family="Arial"),
                        showlegend=False,
                        hoverinfo="skip",
                    )
                )

        # ── Layout ────────────────────────────────────────────────────
        fig.update_layout(
            polar=dict(
                bgcolor="rgba(248,248,250,1)",
                radialaxis=dict(
                    visible=False,
                    range=[0, 1.12],
                    showticklabels=False,
                    showline=False,
                    showgrid=False,
                ),
                angularaxis=dict(
                    showline=False,
                    linewidth=0,
                    gridwidth=2,
                    gridcolor="rgba(90,90,90,0.35)",
                    tickfont=dict(size=13, color="#111", family="Arial Black"),
                ),
            ),
            template=template,
            showlegend=True,
            legend=dict(
                font=dict(size=11),
                itemsizing="constant",
                tracegroupgap=4,
            ),
            margin=dict(t=60, b=60, l=80, r=80),
            paper_bgcolor="white",
        )

        return PlotterMixin._apply_layout_defaults(fig, layout_defaults)

    @staticmethod
    def plot_grouped_radar(
        df: pd.DataFrame,
        axis_labels: list[str],
        group_column: str,
        inverted: dict[str, bool] | None = None,
        palette: list[str] | None = None,
        template: str = "presentation",
        layout_defaults: dict[str, Any] | None = None,
    ) -> go.Figure:
        """Create a normalised radar chart showing group means with std dev bands.

        Rows are grouped by *group_column*; each group becomes a trace
        showing the per-axis mean.  A lighter shaded band shows +/- 1 std dev.

        Args:
            df: Must contain columns named in *axis_labels* and *group_column*.
            axis_labels: Column names in *df* for the radar axes.
            group_column: Column name used for grouping.
            inverted: ``{axis_label: True}`` for axes where lower is better.
                Defaults to inverting any axis whose label contains ``"cost"``.
            palette: Hex colour palette.  Falls back to ``DEFAULT_PALETTE``.
            template: Plotly template name.
            layout_defaults: Additional ``fig.update_layout`` overrides applied last.

        Returns:
            Plotly figure.
        """
        palette = palette or PlotterMixin.DEFAULT_PALETTE

        if inverted is None:
            inverted = {col: "cost" in col.lower() for col in axis_labels}

        grouped = df.groupby(group_column)
        group_stats: dict[str, dict] = {}
        for grp_name, grp_df in sorted(grouped, key=lambda x: str(x[0])):
            means = {col: grp_df[col].mean() for col in axis_labels}
            stds = {
                col: grp_df[col].std() if len(grp_df) > 1 else 0.0
                for col in axis_labels
            }
            group_stats[grp_name] = {
                "mean": means, "std": stds, "count": len(grp_df),
            }

        all_means = pd.DataFrame([s["mean"] for s in group_stats.values()])
        all_stds = pd.DataFrame([s["std"] for s in group_stats.values()])

        axis_ranges: dict[str, tuple[float, float]] = {}
        for col in axis_labels:
            low = (all_means[col] - all_stds[col]).min()
            high = (all_means[col] + all_stds[col]).max()
            pad_min = low * 0.8 if low >= 0 else low * 1.2
            pad_max = high * 1.2 if high >= 0 else high * 0.8
            if pad_max - pad_min == 0:
                pad_min, pad_max = low - 1, high + 1
            axis_ranges[col] = (pad_min, pad_max)

        def _normalise(val, col):
            pad_min, pad_max = axis_ranges[col]
            rng = pad_max - pad_min
            if inverted.get(col, False):
                return (pad_max - val) / rng
            return (val - pad_min) / rng

        fig = go.Figure()
        theta_closed = axis_labels + [axis_labels[0]]

        for i, (grp_name, stats) in enumerate(group_stats.items()):
            clr = palette[i % len(palette)]
            means = stats["mean"]
            stds = stats["std"]
            n = stats["count"]

            norm_means = [_normalise(means[c], c) for c in axis_labels]
            norm_means_closed = norm_means + [norm_means[0]]

            _band_a = [_normalise(means[c] + stds[c], c) for c in axis_labels]
            _band_b = [_normalise(means[c] - stds[c], c) for c in axis_labels]
            norm_upper = [max(a, b) for a, b in zip(_band_a, _band_b)]
            norm_upper_closed = norm_upper + [norm_upper[0]]

            norm_lower = [max(0, min(a, b)) for a, b in zip(_band_a, _band_b)]
            norm_lower_closed = norm_lower + [norm_lower[0]]

            hover = [
                f"{al}: {means[al]:.4g} \u00b1 {stds[al]:.4g}"
                for al in axis_labels
            ]
            hover_closed = hover + [hover[0]]

            fig.add_trace(go.Scatterpolar(
                r=norm_upper_closed,
                theta=theta_closed,
                fill=None,
                mode="lines",
                line=dict(
                    color=PlotterMixin.hex_to_rgba(clr, 0.3), width=0,
                ),
                showlegend=False,
                hoverinfo="skip",
                legendgroup=str(grp_name),
            ))
            fig.add_trace(go.Scatterpolar(
                r=norm_lower_closed,
                theta=theta_closed,
                fill="tonext",
                fillcolor=PlotterMixin.hex_to_rgba(clr, 0.12),
                mode="lines",
                line=dict(
                    color=PlotterMixin.hex_to_rgba(clr, 0.3), width=0,
                ),
                showlegend=False,
                hoverinfo="skip",
                legendgroup=str(grp_name),
            ))
            fig.add_trace(go.Scatterpolar(
                r=norm_means_closed,
                theta=theta_closed,
                name=f"{grp_name} (n={n})",
                fill="none",
                line=dict(color=clr, width=2),
                marker=dict(size=5, color=clr),
                text=hover_closed,
                hovertemplate=(
                    "%{theta}<br>%{text}<br>"
                    f"Group: {grp_name} (n={n})<extra></extra>"
                ),
                legendgroup=str(grp_name),
            ))

        tick_fractions = [0.25, 0.5, 0.75, 1.0]
        for col in axis_labels:
            pad_min, pad_max = axis_ranges[col]
            rng = pad_max - pad_min
            for frac in tick_fractions:
                if inverted.get(col, False):
                    raw = pad_max - frac * rng
                else:
                    raw = pad_min + frac * rng
                if abs(raw) >= 100:
                    txt = f"{raw:.0f}"
                elif abs(raw) >= 1:
                    txt = f"{raw:.2f}"
                else:
                    txt = f"{raw:.3g}"
                fig.add_trace(go.Scatterpolar(
                    r=[frac], theta=[col], mode="text",
                    text=[f"  {txt}"],
                    textfont=dict(size=10, color="#555", family="Arial"),
                    showlegend=False, hoverinfo="skip",
                ))

        fig.update_layout(
            polar=dict(
                bgcolor="rgba(248,248,250,1)",
                radialaxis=dict(
                    visible=False, range=[0, 1.12],
                    showticklabels=False, showline=False, showgrid=False,
                ),
                angularaxis=dict(
                    showline=False, linewidth=0, gridwidth=2,
                    gridcolor="rgba(90,90,90,0.35)",
                    tickfont=dict(
                        size=13, color="#111", family="Arial Black",
                    ),
                ),
            ),
            template=template,
            showlegend=True,
            legend=dict(
                font=dict(size=11), itemsizing="constant", tracegroupgap=4,
            ),
            margin=dict(t=60, b=60, l=80, r=80),
            paper_bgcolor="white",
        )

        return PlotterMixin._apply_layout_defaults(fig, layout_defaults)

    # ── Correlation heatmap ─────────────────────────────────────────────

    @staticmethod
    def plot_correlation_heatmap(
        df: pd.DataFrame,
        axis_labels: list[str],
        template: str = "presentation",
        layout_defaults: dict[str, Any] | None = None,
    ) -> go.Figure:
        """Create an annotated Pearson correlation heatmap.

        Args:
            df: DataFrame containing at least *axis_labels* as numeric columns.
            axis_labels: Column names to include in the correlation matrix.
            template: Plotly template name.
            layout_defaults: Additional ``fig.update_layout`` overrides applied last.

        Returns:
            Plotly figure.
        """
        import numpy as np

        corr = df[axis_labels].corr()
        z = corr.values
        labels = list(corr.columns)
        text = np.around(z, decimals=2).astype(str)

        fig = go.Figure(data=go.Heatmap(
            z=z,
            x=labels,
            y=labels,
            text=text,
            texttemplate="%{text}",
            textfont=dict(size=12),
            colorscale="RdBu_r",
            zmin=-1,
            zmax=1,
            colorbar=dict(title="r", thickness=15),
            hovertemplate=(
                "%{y} vs %{x}<br>r = %{z:.3f}<extra></extra>"
            ),
        ))
        fig.update_layout(
            template=template,
            xaxis=dict(side="bottom", tickangle=-45),
            yaxis=dict(autorange="reversed"),
            margin=dict(l=120, r=40, t=60, b=120),
        )
        return PlotterMixin._apply_layout_defaults(fig, layout_defaults)

# SPDX-FileCopyrightText: 2024-2026 Nicholas Siemons and Adrian Yao
# SPDX-License-Identifier: AGPL-3.0-or-later

from steer_core.Decorators.General import recalculate

calculate_coordinates = recalculate("coordinates")
calculate_areas = recalculate("coordinates", "areas")
calculate_volumes = recalculate("bulk_properties", "coordinates")

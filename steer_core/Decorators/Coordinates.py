from steer_core.Decorators.General import recalculate

calculate_coordinates = recalculate("coordinates")
calculate_areas = recalculate("coordinates", "areas")
calculate_volumes = recalculate("bulk_properties", "coordinates")

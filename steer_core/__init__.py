__version__ = "0.1.32"

# Use lazy imports for Mixins to avoid triggering optional dependencies
# (like shapely for Coordinates) when only importing Constants.
# Users can still access Mixins via explicit import or attribute access.

def __getattr__(name):
    """Lazy import handler for Mixins."""
    if name == "ColorMixin":
        from .Mixins.Colors import ColorMixin
        return ColorMixin
    elif name == "CoordinateMixin":
        from .Mixins.Coordinates import CoordinateMixin
        return CoordinateMixin
    elif name == "PlotterMixin":
        from .Mixins.Plotter import PlotterMixin
        return PlotterMixin
    elif name == "ValidationMixin":
        from .Mixins.TypeChecker import ValidationMixin
        return ValidationMixin
    elif name == "DunderMixin":
        from .Mixins.Dunder import DunderMixin
        return DunderMixin
    elif name == "SerializerMixin":
        from .Mixins.Serializer import SerializerMixin
        return SerializerMixin
    elif name == "DataMixin":
        from .Mixins.Data import DataMixin
        return DataMixin
    raise AttributeError(f"module 'steer_core' has no attribute '{name}'")


# List of available Mixins (for discoverability)
__all__ = [
    "__version__",
    "ColorMixin",
    "CoordinateMixin", 
    "PlotterMixin",
    "ValidationMixin",
    "DunderMixin",
    "SerializerMixin",
    "DataMixin",
]

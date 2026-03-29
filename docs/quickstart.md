# Quick Start

steer-core provides a set of composable mixins for building battery cell models.
Import the mixins you need and compose them into your domain classes.

## Basic Usage

```python
from steer_core import (
    ValidationMixin,
    SerializerMixin,
    DunderMixin,
    ColorMixin,
)

class MyComponent(ValidationMixin, SerializerMixin, DunderMixin):
    def __init__(self, name: str, mass: float):
        self._name = name
        self._mass = mass

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str):
        self.validate_string(value, "name")
        self._name = value

    @property
    def mass(self) -> float:
        return self._mass

    @mass.setter
    def mass(self, value: float):
        self.validate_positive_float(value, "mass")
        self._mass = value

# Create and serialize
comp = MyComponent("cathode", 0.5)
data = comp.serialize()
restored = MyComponent.deserialize(data)
print(restored.name)   # "cathode"
print(restored.mass)   # 0.5
print(comp == restored) # True
```

## Using the DataManager

```python
import os
os.environ["API_URL"] = "https://api.opencell.example.com/production"

from steer_core.Data.DataManager import DataManager

db = DataManager()
materials = db.get_cathode_materials()
print(materials)
```

## DateTime Utilities

```python
from steer_core.Mixins.DateTime import DateTimeMixin

dt = DateTimeMixin.str_to_datetime("2024-06-15-14")
shifted = DateTimeMixin.shift_months(dt, 3)
print(DateTimeMixin.datetime_to_str(shifted))  # "2024-09-15-14"
```

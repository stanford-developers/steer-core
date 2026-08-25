from copy import deepcopy

from steer_core.Mixins.Dunder import DunderMixin


class Example(DunderMixin):
    def __init__(self, value):
        self._value = value

    @property
    def value(self):
        return self._value


def test_equal_instances_have_constant_hash_and_support_dict_lookup():
    original = Example(3)
    copied = deepcopy(original)

    values = {original: 7}

    assert original == copied
    assert hash(original) == hash(copied) == 0
    assert values.get(copied, 0) == 7

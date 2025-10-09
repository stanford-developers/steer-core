#!/usr/bin/env python3
"""Test script for the refactored DunderMixin functionality."""

import numpy as np
import pandas as pd
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from steer_core.Mixins.Dunder import DunderMixin


class TestClass(DunderMixin):
    def __init__(self, name, value, data=None, array=None, dict_data=None):
        self._name = name
        self._value = value
        self._data = data
        self._array = array
        self._dict_data = dict_data or {}
        self._last_updated = "2023-01-01"  # Should be excluded
    
    @property
    def name(self):
        return self._name
    
    @property
    def value(self):
        return self._value
    
    @property
    def data(self):
        return self._data
    
    @property
    def array(self):
        return self._array
    
    @property
    def dict_data(self):
        return self._dict_data
    
    @property
    def last_updated(self):
        return self._last_updated
    
    @property
    def value_range(self):  # Should be excluded
        return (0, 100)


def test_all_comparison_types():
    """Test all comparison types to ensure they work correctly."""
    
    # Test basic equality
    obj1 = TestClass("test", 42)
    obj2 = TestClass("test", 42)
    obj3 = TestClass("test", 43)
    
    print("=== Basic Equality Tests ===")
    print(f"obj1 == obj2: {obj1 == obj2} (should be True)")
    print(f"obj1 == obj3: {obj1 == obj3} (should be False)")
    print()
    
    # Test None values
    obj_none1 = TestClass("test", None)
    obj_none2 = TestClass("test", None)
    obj_none3 = TestClass("test", 42)
    
    print("=== None Value Tests ===")
    print(f"None == None: {obj_none1 == obj_none2} (should be True)")
    print(f"None == Value: {obj_none1 == obj_none3} (should be False)")
    print()
    
    # Test NumPy arrays
    arr1 = np.array([1, 2, 3])
    arr2 = np.array([1, 2, 3])
    arr3 = np.array([1, 2, 4])
    
    obj_arr1 = TestClass("test", 42, array=arr1)
    obj_arr2 = TestClass("test", 42, array=arr2)
    obj_arr3 = TestClass("test", 42, array=arr3)
    
    print("=== NumPy Array Tests ===")
    print(f"Same arrays: {obj_arr1 == obj_arr2} (should be True)")
    print(f"Different arrays: {obj_arr1 == obj_arr3} (should be False)")
    print()
    
    # Test DataFrames
    df1 = pd.DataFrame({'x': [1, 2, 3]})
    df2 = pd.DataFrame({'x': [1, 2, 3]})
    df3 = pd.DataFrame({'x': [1, 2, 4]})
    
    obj_df1 = TestClass("test", 42, data=df1)
    obj_df2 = TestClass("test", 42, data=df2)
    obj_df3 = TestClass("test", 42, data=df3)
    
    print("=== DataFrame Tests ===")
    print(f"Same DataFrames: {obj_df1 == obj_df2} (should be True)")
    print(f"Different DataFrames: {obj_df1 == obj_df3} (should be False)")
    print()
    
    # Test dictionaries
    dict1 = {'a': 1, 'b': 2}
    dict2 = {'a': 1, 'b': 2}
    dict3 = {'a': 1, 'b': 3}
    
    obj_dict1 = TestClass("test", 42, dict_data=dict1)
    obj_dict2 = TestClass("test", 42, dict_data=dict2)
    obj_dict3 = TestClass("test", 42, dict_data=dict3)
    
    print("=== Dictionary Tests ===")
    print(f"Same dicts: {obj_dict1 == obj_dict2} (should be True)")
    print(f"Different dicts: {obj_dict1 == obj_dict3} (should be False)")
    print()
    
    # Test mixed types (should be False)
    obj_mixed1 = TestClass("test", 42, array=np.array([1, 2, 3]))
    obj_mixed2 = TestClass("test", 42, array=[1, 2, 3])  # List instead of array
    
    print("=== Mixed Type Tests ===")
    print(f"Array vs List: {obj_mixed1 == obj_mixed2} (should be False)")
    print()
    
    # Test identity optimization
    print("=== Identity Optimization Test ===")
    print(f"Identity check: {obj1 is obj1} and {obj1 == obj1} (both should be True)")
    print()


if __name__ == "__main__":
    print("Testing refactored DunderMixin functionality...\n")
    test_all_comparison_types()
    print("All tests completed!")
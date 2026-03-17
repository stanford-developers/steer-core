# SPDX-FileCopyrightText: 2024-2026 Nicholas Siemons and Adrian Yao
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Mixin for update propagation through hierarchical object trees."""

from typing import Optional, Any, Generator
from functools import wraps
from copy import deepcopy as do_deepcopy
from contextlib import contextmanager


def propagating_setter(attr_name: str = None, deepcopy: bool = False):
    """
    Decorator for setters that manage parent-child relationships.
    
    This decorator:
    1. Clears the old child's parent reference (if replacing with different object)
    2. Optionally creates a deep copy of the value (for storing copies)
    3. Sets the new child's parent reference with the attribute name
    
    Parameters
    ----------
    attr_name : str, optional
        The attribute name to use for propagation. If not provided,
        the decorator will derive it from the setter's name.
    deepcopy : bool, default False
        If True, creates a deep copy of the value before passing to the setter.
        Useful when you want to store a copy rather than the original.
        During propagation (re-assignment of the same stored object), no copy
        is made to avoid unnecessary duplication.
    
    Example Usage
    -------------
    # Standard usage (no copy):
    @formulation.setter
    @calculate_all_properties
    @propagating_setter()
    def formulation(self, formulation: _ElectrodeFormulation):
        self.validate_type(formulation, _ElectrodeFormulation, "formulation")
        self._formulation = formulation
    
    # With deepcopy (stores a copy):
    @insulation_material.setter
    @calculate_bulk_properties
    @propagating_setter(deepcopy=True)
    def insulation_material(self, insulation_material: InsulationMaterial | None):
        self.validate_type(insulation_material, InsulationMaterial, "insulation material")
        self._insulation_material = insulation_material  # This is already a copy
    """
    def decorator(func):
        @wraps(func)
        def wrapper(self, new_value):
            # Derive attribute name from function name if not provided
            name = attr_name if attr_name else func.__name__
            private_name = f'_{name}'
            
            # Get the old value if it exists
            old_value = getattr(self, private_name, None)
            
            # Check if this is a propagation re-assignment (same object already parented to us)
            is_propagation = (
                new_value is not None and
                hasattr(new_value, '_get_parent') and
                new_value._get_parent() is self and
                getattr(new_value, '_parent_attr_name', None) == name
            )
            
            # Clear old parent reference only if replacing with a different object
            if old_value is not None and old_value is not new_value:
                if hasattr(old_value, '_set_parent'):
                    old_value._set_parent(None)
            
            # Make deepcopy only if requested AND not during propagation
            if deepcopy and new_value is not None and not is_propagation:
                new_value = do_deepcopy(new_value)
            
            # Call the actual setter
            result = func(self, new_value)
            
            # Set parent reference on new value
            if new_value is not None and hasattr(new_value, '_set_parent'):
                new_value._set_parent(self, name)
            
            return result
        return wrapper
    return decorator


class PropagationMixin:
    """
    Mixin providing update propagation through a hierarchical object tree.
    
    This mixin adds two methods:
    - `update()`: Triggers the parent's setter for this object (one level up)
    - `propagate_changes()`: Triggers parent setters all the way up to root
    
    Each object can have a parent reference. When a child is assigned to a parent,
    the parent should call `child._set_parent(self, 'attribute_name')` to establish
    the link. The attribute name is used during propagation to re-assign the child
    to the parent via its setter.
    
    Python's cyclic garbage collector handles any circular references.
    
    Serialization Note
    ------------------
    The `_parent` reference is skipped during serialization to avoid circular
    serialization. Parent references are re-established when objects are 
    reassembled after deserialization (via setters that call `_set_parent`).
    
    Example Usage
    -------------
    # Change property at any depth:
    cell.reference_assembly.layout.cathode.current_collector.thickness = new_value
    
    # Option 1: Update current level by triggering parent's setter
    cell.reference_assembly.layout.cathode.current_collector.update()
    # Equivalent to: a.b.c.current_collector = a.b.c.current_collector
    
    # Option 2: Propagate changes all the way to root (triggers all parent setters)
    cell.reference_assembly.layout.cathode.current_collector.propagate_changes()
    # Equivalent to re-assigning at each level up to root
    """
    
    _parent: Optional[Any] = None
    _parent_attr_name: Optional[str] = None

    # Mapping from internal dict keys to property setter names for propagation.
    # Override in subclasses when a private attribute name doesn't match its
    # public property setter (e.g. _canonical_separator -> separator).
    _propagation_attr_map: dict = {}
    
    # -------------------------------------------------------------------------
    # Parent reference management
    # -------------------------------------------------------------------------
    
    def _set_parent(self, parent: Optional[Any], attr_name: Optional[str] = None) -> None:
        """
        Set the parent reference for this object.
        
        Parameters
        ----------
        parent : Optional[Any]
            The parent object, or None to clear the parent reference.
        attr_name : Optional[str]
            The attribute name on the parent that holds this object.
            Used during propagation to re-assign via the parent's setter.
            If not provided, propagation will fall back to calling
            parent.propagate_changes() directly.
        """
        self._parent = parent
        self._parent_attr_name = attr_name if parent is not None else None
    
    def _get_parent(self) -> Optional[Any]:
        """
        Get the parent object if set.
        
        Returns
        -------
        Optional[Any]
            The parent object, or None if no parent is set.
        """
        return self._parent
    
    def update(self) -> None:
        """
        Trigger the parent's setter for this object.
        
        This is equivalent to `parent.attr = self`, ensuring that all setter
        logic (validation, coordinate calculation, etc.) is executed.
        
        If this object has no parent, falls back to calling 
        `_calculate_all_properties()` directly.
        
        Use `propagate_changes()` to bubble updates all the way to the root.
        """
        parent = self._get_parent()
        attr_name = getattr(self, '_parent_attr_name', None)
        
        if parent is not None and attr_name is not None:
            # Trigger parent's setter for this object
            setattr(parent, attr_name, self)
        else:
            # No parent or no attr_name - fall back to direct calculation
            if hasattr(self, '_update_properties') and not self._update_properties:
                return
            if hasattr(self, '_calculate_all_properties'):
                self._calculate_all_properties()

    @contextmanager
    def batch_updates(self) -> Generator[None, None, None]:
        """Context manager for efficient batch property updates.

        Temporarily disables automatic recalculation during property changes,
        then performs a single recalculation when exiting the context.

        Use this when setting multiple properties at once to avoid redundant
        recalculations that would otherwise occur after each property change.

        Examples
        --------
        >>> with obj.batch_updates():
        ...     obj.property_a = value_a
        ...     obj.property_b = value_b
        # Single recalculation happens here

        Yields
        ------
        None
        """
        original_update_flag = getattr(self, '_update_properties', True)
        self._update_properties = False

        try:
            yield
        finally:
            self._update_properties = original_update_flag
            if original_update_flag and hasattr(self, '_calculate_all_properties'):
                self._calculate_all_properties()

    def propagate_changes(self) -> None:
        """
        Propagate changes up to root by triggering parent setters.
        
        This method triggers the parent's setter by re-assigning this object
        to its parent attribute. This ensures any parent setter logic 
        (validation, name modification, coordinate calculation, etc.) is 
        executed during propagation.
        
        The propagation continues recursively until reaching the root.
        
        Note: This does NOT call update() on the current object - that should
        already have happened via the property setter's @calculate_all_properties
        decorator when the property was modified.
        
        Use this when you want changes to bubble up automatically. Use
        `update()` instead when you need to manually trigger recalculation.
        """
        self._propagate_to_parent()
    
    def _propagate_to_parent(self) -> None:
        """
        Propagate changes to parent by triggering its setter.
        
        If an attribute name was provided when _set_parent was called,
        this method will re-assign this object to the parent via setattr,
        triggering the parent's property setter. The setter is expected
        to call _calculate_all_properties() and then this method continues
        bubbling up.
        
        If no attribute name is available (backward compatibility), falls
        back to calling parent.propagate_changes() directly.
        """
        parent = self._get_parent()
        if parent is None:
            return
        
        attr_name = getattr(self, '_parent_attr_name', None)
        
        if attr_name is not None:
            # Re-assign self to parent via setter, triggering setter logic
            # The setter will call _calculate_all_properties() on the parent
            setattr(parent, attr_name, self)
            # Continue propagation up the tree
            if hasattr(parent, '_propagate_to_parent'):
                parent._propagate_to_parent()
        else:
            # Backward compatibility: no attr_name, just call propagate_changes
            if hasattr(parent, 'propagate_changes'):
                parent.propagate_changes()

    # -------------------------------------------------------------------------
    # Serialization support - restore parent references after deserialization
    # -------------------------------------------------------------------------
    
    @classmethod
    def _from_dict(cls, data: dict):
        """
        Reconstruct object from dictionary, restoring parent references.
        
        Chains with SerializerMixin's _from_dict, then walks through
        child objects to re-establish parent references that were lost
        during serialization.
        
        Parameters
        ----------
        data : dict
            Dictionary representation to reconstruct from.
            
        Returns
        -------
            Reconstructed object instance with parent references restored.
        """
        # Chain to SerializerMixin's _from_dict
        if hasattr(super(), '_from_dict'):
            obj = super()._from_dict(data)
        else:
            # Fallback: basic reconstruction
            obj = cls.__new__(cls)
            obj.__dict__.update(data)
        
        # Initialize own _parent to None (will be set by parent if applicable)
        obj._parent = None
        
        # Restore parent references for all children
        obj._restore_child_parent_refs()
        
        return obj
    
    def _restore_child_parent_refs(self) -> None:
        """
        Walk through attributes and set this object as parent of children.
        
        Called after deserialization to re-establish the parent-child
        relationships that were lost during serialization. Also stores
        the attribute name for setter-based propagation.
        
        Uses ``_propagation_attr_map`` when the private attribute key
        differs from its public property setter name.
        """
        attr_map = self._propagation_attr_map
        for key, value in self.__dict__.items():
            if key in ('_parent', '_parent_attr_name'):
                continue
            if key in attr_map:
                attr_name = attr_map[key]
            else:
                attr_name = key[1:] if key.startswith('_') else key
            self._set_parent_on_value(value, attr_name)

    def _set_parent_on_value(self, value: Any, attr_name: Optional[str] = None) -> None:
        """
        Recursively set parent references on a value and its contents.
        
        Parameters
        ----------
        value : Any
            The value to set parent references on.
        attr_name : Optional[str]
            The attribute name on this object that holds the value.
            Used for setter-based propagation.
        """
        if hasattr(value, '_set_parent'):
            value._set_parent(self, attr_name)
        elif isinstance(value, (list, tuple)):
            # For collections, items don't have a direct setter path
            for item in value:
                if hasattr(item, '_set_parent'):
                    item._set_parent(self, attr_name)
        elif isinstance(value, dict):
            # Check both keys AND values - materials can be dict keys
            # For dict items, they don't have a direct setter path
            for item in value.keys():
                if hasattr(item, '_set_parent'):
                    item._set_parent(self, attr_name)
            for item in value.values():
                if hasattr(item, '_set_parent'):
                    item._set_parent(self, attr_name)

    def __deepcopy__(self, memo):
        """Create a deep copy with properly restored parent references."""
        import copy
        
        # Temporarily remove parent info (these shouldn't be copied)
        old_parent = self._parent
        old_parent_attr_name = getattr(self, '_parent_attr_name', None)
        self._parent = None
        self._parent_attr_name = None
        
        # Perform the copy
        cls = self.__class__
        result = cls.__new__(cls)
        memo[id(self)] = result
        
        for k, v in self.__dict__.items():
            if k in ('_parent', '_parent_attr_name'):
                setattr(result, k, None)
            else:
                setattr(result, k, copy.deepcopy(v, memo))
        
        # Restore original's parent info
        self._parent = old_parent
        self._parent_attr_name = old_parent_attr_name
        
        # Restore parent references in the copy
        result._restore_child_parent_refs()
        
        return result


        
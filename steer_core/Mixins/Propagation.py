"""Mixin for update propagation through hierarchical object trees."""

import weakref
from typing import Optional, Any


class PropagationMixin:
    """
    Mixin providing update propagation through a hierarchical object tree.
    
    This mixin adds two methods:
    - `update()`: Recalculates properties of the current object only
    - `propagate_changes()`: Recalculates this object then bubbles up to root
    
    Each object can have a parent reference (stored as a weakref to avoid 
    circular reference memory issues). When a child is assigned to a parent,
    the parent should call `child._set_parent(self)` to establish the link.
    
    Serialization Note
    ------------------
    This mixin relies on SerializerMixin for serialization. The `_parent` 
    weakref is automatically handled (serializes to None). Parent references
    are re-established when objects are reassembled after deserialization
    (via setters that call `_set_parent`).
    
    Example Usage
    -------------
    # Change property at any depth:
    cell.reference_assembly.layout.cathode.current_collector.thickness = new_value
    
    # Option 1: Update only current level
    cell.reference_assembly.layout.cathode.current_collector.update()
    
    # Option 2: Propagate changes all the way to root
    cell.reference_assembly.layout.cathode.current_collector.propagate_changes()
    
    # Option 3: Manual control with intervention at intermediate levels
    cell.reference_assembly.layout.cathode.current_collector.update()
    cell.reference_assembly.layout.cathode.update()
    cell.reference_assembly.layout.update()
    cell.reference_assembly.thickness = original_thickness  # intervene here
    cell.reference_assembly.propagate_changes()  # finish propagation
    """
    
    _parent: Optional[weakref.ref] = None
    
    # -------------------------------------------------------------------------
    # Parent reference management
    # -------------------------------------------------------------------------
    
    def _set_parent(self, parent: Optional[Any]) -> None:
        """
        Set the parent reference for this object.
        
        Parameters
        ----------
        parent : Optional[Any]
            The parent object, or None to clear the parent reference.
            Stored as a weak reference to avoid circular reference issues.
        """
        if parent is None:
            self._parent = None
        else:
            self._parent = weakref.ref(parent)
    
    def _get_parent(self) -> Optional[Any]:
        """
        Get the parent object if it still exists.
        
        Returns
        -------
        Optional[Any]
            The parent object, or None if no parent is set or parent 
            has been garbage collected.
        """
        if self._parent is None:
            return None
        return self._parent()
    
    def update(self) -> None:
        """
        Recalculate all properties of this object only.
        
        This method respects the `_update_properties` flag - if the flag
        is False (e.g., during initialization), no recalculation occurs.
        
        The object must have a `_calculate_all_properties()` method.
        """
        if hasattr(self, '_update_properties') and not self._update_properties:
            return
        if hasattr(self, '_calculate_all_properties'):
            self._calculate_all_properties()
    
    def propagate_changes(self) -> None:
        """
        Recalculate this object's properties, then propagate up to root.
        
        This method calls `update()` on the current object, then recursively
        calls `propagate_changes()` on the parent (if one exists). This 
        continues until reaching the root of the hierarchy.
        
        Use this when you want changes to bubble up automatically. Use
        `update()` instead when you need to intervene at intermediate levels.
        """
        self.update()
        parent = self._get_parent()
        if parent is not None and hasattr(parent, 'propagate_changes'):
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
        weakref relationships that were lost during serialization.
        """
        for key, value in self.__dict__.items():
            if key == '_parent':
                continue
            self._set_parent_on_value(value)

    def _set_parent_on_value(self, value: Any) -> None:
        """
        Recursively set parent references on a value and its contents.
        """
        if hasattr(value, '_set_parent'):
            value._set_parent(self)
        elif isinstance(value, (list, tuple)):
            for item in value:
                if hasattr(item, '_set_parent'):
                    item._set_parent(self)
        elif isinstance(value, dict):
            # Check both keys AND values - materials can be dict keys
            for item in value.keys():
                if hasattr(item, '_set_parent'):
                    item._set_parent(self)
            for item in value.values():
                if hasattr(item, '_set_parent'):
                    item._set_parent(self)
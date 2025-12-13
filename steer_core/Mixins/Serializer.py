import msgpack
import msgpack_numpy as m
import zlib
from typing import TypeVar, Any
from datetime import datetime
from enum import Enum

T = TypeVar('T', bound='SerializerMixin')


class SerializerMixin:
    
    def serialize(self, compress: bool = True) -> bytes:
        """
        Serialize object using MessagePack with numpy support.

        Parameters
        ----------
        compress : bool, optional
            Whether to compress the serialized data (default: True)

        Returns
        -------
        bytes
            The serialized byte representation of the object.
        """
        m.patch()  # Enable numpy support
        data = msgpack.packb(self._to_dict(), use_bin_type=True)
        
        if compress:
            # Add marker byte to indicate compression
            return b'\x01' + zlib.compress(data, level=6)
        else:
            return b'\x00' + data
    
    def _serialize_value(self, value: Any) -> Any:
        """
        Recursively serialize a value, handling nested structures.
        
        Parameters
        ----------
        value : Any
            The value to serialize.
            
        Returns
        -------
        Any
            The serialized representation.
        """
        if hasattr(value, '_to_dict'):
            # Add marker and class info for object reconstruction
            return {
                '__object__': True,
                '_class': f"{value.__class__.__module__}.{value.__class__.__name__}",
                **value._to_dict()
            }
        elif isinstance(value, datetime):
            return {'__datetime__': value.isoformat()}
        elif isinstance(value, Enum):
            return {
                '__enum__': True,
                'class': f"{value.__class__.__module__}.{value.__class__.__name__}",
                'value': value.value
            }
        elif isinstance(value, tuple):
            # Recursively serialize tuple items
            return {
                '__tuple__': True,
                'items': [self._serialize_value(item) for item in value]
            }
        elif isinstance(value, list):
            # Recursively serialize list items
            return [self._serialize_value(item) for item in value]
        elif isinstance(value, dict):
            # Handle dictionaries with object keys or values
            has_object_keys = value and any(hasattr(k, '_to_dict') for k in value.keys())
            has_object_values = value and any(hasattr(v, '_to_dict') for v in value.values())
            
            if has_object_keys or has_object_values:
                return {
                    '__object_dict__': True,
                    'items': [
                        {
                            'key': self._serialize_value(k),
                            'value': self._serialize_value(v)
                        }
                        for k, v in value.items()
                    ]
                }
            else:
                # Recursively serialize regular dict values
                return {k: self._serialize_value(v) for k, v in value.items()}
        else:
            return value
    
    def _to_dict(self) -> dict:
        """
        Convert object to dictionary for serialization.
        Override this in subclasses to customize serialization behavior.
        
        Returns
        -------
        dict
            Dictionary representation of the object.
        """
        result = {}
        for key, value in self.__dict__.items():
            result[key] = self._serialize_value(value)
        return result
    
    @classmethod
    def deserialize(cls: type[T], data: bytes) -> T:
        """
        Deserialize byte data into an object.
        Automatically detects and decompresses if needed.

        Parameters
        ----------
        data : bytes
            The byte data to deserialize.

        Returns
        -------
        T
            Instance of the class.
        """
        m.patch()  # Enable numpy support
        
        # Check compression marker
        if data[0:1] == b'\x01':
            data = zlib.decompress(data[1:])
        else:
            data = data[1:]
        
        obj_dict = msgpack.unpackb(data, raw=False)
        return cls._from_dict(obj_dict)
    
    @classmethod
    def _deserialize_value(cls, value: Any) -> Any:
        """
        Recursively deserialize a value, handling nested structures.
        
        Parameters
        ----------
        value : Any
            The value to deserialize.
            
        Returns
        -------
        Any
            The deserialized object.
        """
        if isinstance(value, dict):
            if '__datetime__' in value:
                return datetime.fromisoformat(value['__datetime__'])
            elif '__enum__' in value:
                # Reconstruct enum
                module_name, class_name = value['class'].rsplit('.', 1)
                import importlib
                module = importlib.import_module(module_name)
                enum_class = getattr(module, class_name)
                return enum_class(value['value'])
            elif '__tuple__' in value:
                # Recursively reconstruct tuple items
                return tuple(cls._deserialize_value(item) for item in value['items'])
            elif '__object__' in value:
                # Reconstruct regular object
                import importlib
                module_name, class_name = value['_class'].rsplit('.', 1)
                module = importlib.import_module(module_name)
                obj_class = getattr(module, class_name)
                # Remove marker fields before passing to _from_dict
                obj_data = {k: v for k, v in value.items() if k not in ('__object__', '_class')}
                return obj_class._from_dict(obj_data)
            elif '__object_dict__' in value:
                # Reconstruct dictionary with object keys or values
                reconstructed_dict = {}
                for item in value['items']:
                    key_obj = cls._deserialize_value(item['key'])
                    value_obj = cls._deserialize_value(item['value'])
                    reconstructed_dict[key_obj] = value_obj
                return reconstructed_dict
            else:
                # Recursively deserialize regular dict values
                return {k: cls._deserialize_value(v) for k, v in value.items()}
        elif isinstance(value, list):
            # Recursively deserialize list items
            return [cls._deserialize_value(item) for item in value]
        else:
            return value
    
    @classmethod
    def _from_dict(cls: type[T], data: dict) -> T:
        """
        Reconstruct object from dictionary.
        Override in subclasses for custom deserialization.
        
        Parameters
        ----------
        data : dict
            Dictionary representation to reconstruct from.
            
        Returns
        -------
        T
            Reconstructed object instance.
        """
        obj = cls.__new__(cls)
        reconstructed = {}
        for key, value in data.items():
            reconstructed[key] = cls._deserialize_value(value)
        obj.__dict__.update(reconstructed)
        return obj
        
    @classmethod
    def from_database(cls: type[T], name: str, table_name: str = None) -> T:
        """
        Pull object from the database by name.
        
        Subclasses must define a '_table_name' class variable (str or list of str)
        unless table_name is explicitly provided.

        Parameters
        ----------
        name : str
            Name of the object to retrieve.
        table_name : str, optional
            Specific table to search. If provided, '_table_name' is not required.
            If None, uses class's _table_name.

        Returns
        -------
        T
            Instance of the class.
            
        Raises
        ------
        NotImplementedError
            If the subclass doesn't define '_table_name' and table_name is not provided.
        ValueError
            If the object name is not found in any of the tables.
        """
        from steer_core.Data.DataManager import DataManager
        
        database = DataManager()
        
        # Get list of tables to search
        if table_name:
            tables_to_search = [table_name]
        else:
            # Only check for _table_name if table_name wasn't provided
            if not hasattr(cls, '_table_name'):
                raise NotImplementedError(
                    f"{cls.__name__} must define a '_table_name' class variable "
                    "or provide 'table_name' argument"
                )
            
            if isinstance(cls._table_name, (list, tuple)):
                tables_to_search = cls._table_name
            else:
                tables_to_search = [cls._table_name]
        
        # Try each table until found
        for table in tables_to_search:
            available_materials = database.get_unique_values(table, "name")
            
            if name in available_materials:
                data = database.get_data(table, condition=f"name = '{name}'")
                serialized_bytes = data["object"].iloc[0]
                return cls.deserialize(serialized_bytes)
        
        # Not found in any table
        all_available = []
        for table in tables_to_search:
            all_available.extend(database.get_unique_values(table, "name"))
        
        raise ValueError(
            f"'{name}' not found in tables {tables_to_search}. "
            f"Available: {all_available}"
        )
        

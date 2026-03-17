# SPDX-License-Identifier: AGPL-3.0-only

import importlib
import msgpack
import msgpack_numpy as m
import lz4.frame
import zlib
import numpy as np
from typing import TypeVar, Any
from datetime import datetime
from enum import Enum

# Patch msgpack for numpy support once at module import
m.patch()

# Module-level cache for imported modules (avoids repeated importlib calls)
_module_cache: dict[str, type] = {}

T = TypeVar('T', bound='SerializerMixin')


def _get_class(class_path: str) -> type:
    """Get class from module path with caching."""
    if class_path not in _module_cache:
        module_name, class_name = class_path.rsplit('.', 1)
        module = importlib.import_module(module_name)
        _module_cache[class_path] = getattr(module, class_name)
    return _module_cache[class_path]


class SerializerMixin:
    
    # Compression markers for backward compatibility
    _MARKER_LZ4 = b'\x02'
    _MARKER_ZLIB = b'\x01'
    _MARKER_NONE = b'\x00'
    
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
        # Include class information for proper deserialization
        obj_dict = {
            '_class': f"{self.__class__.__module__}.{self.__class__.__name__}",
            **self._to_dict()
        }
        data = msgpack.packb(obj_dict, use_bin_type=True)
        
        if compress:
            # Use LZ4 for fast compression
            return self._MARKER_LZ4 + lz4.frame.compress(data)
        else:
            return self._MARKER_NONE + data
    
    def _serialize_value(self, value: Any) -> Any:
        """
        Recursively serialize a value, handling nested structures.
        Optimized with type-based dispatch for common types.
        
        Parameters
        ----------
        value : Any
            The value to serialize.
            
        Returns
        -------
        Any
            The serialized representation.
        """
        # Fast path: check type directly for common cases
        value_type = type(value)
        
        # Primitive types - return immediately (most common case)
        if value_type in (int, float, str, bool, bytes, type(None)):
            return value
        
        # Skip functions/methods without _to_dict
        if callable(value) and not hasattr(value, '_to_dict'):
            return None
        
        # Objects with _to_dict method (SerializerMixin instances)
        if hasattr(value, '_to_dict'):
            return {
                '__object__': True,
                '_class': f"{value.__class__.__module__}.{value.__class__.__name__}",
                **value._to_dict()
            }
        
        # datetime handling
        if value_type is datetime:
            return {'__datetime__': value.isoformat()}
        
        # Pandas DataFrame handling (lazy import to avoid hard dependency)
        try:
            import pandas as pd
            if isinstance(value, pd.DataFrame):
                return self._serialize_dataframe(value)
        except ImportError:
            pass

        # Enum handling
        if isinstance(value, Enum):
            return {
                '__enum__': True,
                'class': f"{value.__class__.__module__}.{value.__class__.__name__}",
                'value': value.value
            }
        
        # Tuple handling
        if value_type is tuple:
            return {
                '__tuple__': True,
                'items': [self._serialize_value(item) for item in value]
            }
        
        # List handling
        if value_type is list:
            return [self._serialize_value(item) for item in value]
        
        # Dict handling - single pass detection and serialization
        if value_type is dict:
            return self._serialize_dict(value)
        
        # Fallback for other types (numpy arrays handled by msgpack_numpy)
        return value
    
    def _serialize_dataframe(self, df) -> dict:
        """
        Serialize a pandas DataFrame to a dictionary representation.
        Stores columns as numpy arrays to leverage msgpack_numpy for
        efficient dtype-preserving serialization.

        Parameters
        ----------
        df : pandas.DataFrame
            The DataFrame to serialize.

        Returns
        -------
        dict
            Dictionary with '__dataframe__' marker and column/index data.
        """
        result = {
            '__dataframe__': True,
            'columns': list(df.columns),
            'data': {col: df[col].to_numpy() for col in df.columns},
            'index_values': df.index.to_numpy(),
            'index_name': df.index.name,
        }
        # Preserve MultiIndex if present
        import pandas as pd
        if isinstance(df.index, pd.MultiIndex):
            result['__multiindex__'] = True
            result['index_values'] = [level.tolist() for level in df.index.levels]
            result['index_codes'] = [codes.tolist() for codes in df.index.codes]
            result['index_names'] = list(df.index.names)
        return result

    def _serialize_dict(self, d: dict) -> dict:
        """
        Serialize dictionary in single pass, detecting object keys/values during iteration.
        
        Parameters
        ----------
        d : dict
            Dictionary to serialize.
            
        Returns
        -------
        dict
            Serialized dictionary representation.
        """
        if not d:
            return {}
        
        # Single-pass: serialize and detect objects simultaneously
        items = []
        has_objects = False
        
        for k, v in d.items():
            k_serialized = self._serialize_value(k)
            v_serialized = self._serialize_value(v)
            
            # Check if key or value became an object marker
            k_is_obj = isinstance(k_serialized, dict) and k_serialized.get('__object__')
            v_is_obj = isinstance(v_serialized, dict) and v_serialized.get('__object__')
            
            if k_is_obj or v_is_obj:
                has_objects = True
            
            items.append((k, k_serialized, v_serialized))
        
        if has_objects:
            return {
                '__object_dict__': True,
                'items': [{'key': k_ser, 'value': v_ser} for _, k_ser, v_ser in items]
            }
        else:
            return {k: v_ser for k, _, v_ser in items}
    
    def _to_dict(self) -> dict:
        """
        Convert object to dictionary for serialization.
        Override this in subclasses to customize serialization behavior.
        Single-pass implementation for efficiency.
        
        Returns
        -------
        dict
            Dictionary representation of the object.
        """
        result = {}
        for key, value in self.__dict__.items():
            # Skip _parent - PropagationMixin rebuilds it via _from_dict
            if key == '_parent':
                continue
            # Skip non-serializable callables
            if callable(value) and not hasattr(value, '_to_dict'):
                continue
            result[key] = self._serialize_value(value)
        return result
    
    @classmethod
    def deserialize(cls: type[T], data: bytes) -> T:
        """
        Deserialize byte data into an object.
        Automatically detects and decompresses if needed.
        Supports both LZ4 (new) and zlib (legacy) compression.

        Parameters
        ----------
        data : bytes
            The byte data to deserialize.

        Returns
        -------
        T
            Instance of the class.
        """
        # Check compression marker and decompress accordingly
        marker = data[0:1]
        if marker == cls._MARKER_LZ4:
            data = lz4.frame.decompress(data[1:])
        elif marker == cls._MARKER_ZLIB:
            # Backward compatibility with zlib-compressed data
            data = zlib.decompress(data[1:])
        else:
            data = data[1:]
        
        obj_dict = msgpack.unpackb(data, raw=False)
        
        # Use stored class information if available
        if '_class' in obj_dict:
            actual_cls = _get_class(obj_dict['_class'])
            # Remove class marker before reconstructing
            obj_data = {k: v for k, v in obj_dict.items() if k != '_class'}
            return actual_cls._from_dict(obj_data)
        else:
            # Fallback for backward compatibility
            return cls._from_dict(obj_dict)
    
    @classmethod
    def _deserialize_value(cls, value: Any) -> Any:
        """
        Recursively deserialize a value, handling nested structures.
        Optimized with cached module lookups.
        
        Parameters
        ----------
        value : Any
            The value to deserialize.
            
        Returns
        -------
        Any
            The deserialized object.
        """
        # Fast path for non-dict/list types
        value_type = type(value)
        
        if value_type is dict:
            # Check special markers in priority order (most common first)
            if '__object__' in value:
                # Reconstruct regular object using cached class lookup
                obj_class = _get_class(value['_class'])
                obj_data = {k: v for k, v in value.items() if k not in ('__object__', '_class')}
                return obj_class._from_dict(obj_data)
            elif '__datetime__' in value:
                return datetime.fromisoformat(value['__datetime__'])
            elif '__enum__' in value:
                # Reconstruct enum using cached class lookup
                enum_class = _get_class(value['class'])
                return enum_class(value['value'])
            elif '__tuple__' in value:
                # Recursively reconstruct tuple items
                return tuple(cls._deserialize_value(item) for item in value['items'])
            elif '__dataframe__' in value:
                import pandas as pd
                if value.get('__multiindex__'):
                    index = pd.MultiIndex.from_arrays(
                        [np.array(lvl) for lvl in value['index_values']],
                        names=value.get('index_names'),
                    )
                    # Reconstruct using codes if needed for proper ordering
                    if 'index_codes' in value:
                        index = pd.MultiIndex(
                            levels=[np.array(lvl) for lvl in value['index_values']],
                            codes=value['index_codes'],
                            names=value.get('index_names'),
                        )
                else:
                    index = pd.Index(
                        np.array(value['index_values']),
                        name=value.get('index_name'),
                    )
                data = {col: np.array(arr) for col, arr in value['data'].items()}
                return pd.DataFrame(data, index=index, columns=value['columns'])
            elif '__object_dict__' in value:
                # Reconstruct dictionary with object keys or values
                return {
                    cls._deserialize_value(item['key']): cls._deserialize_value(item['value'])
                    for item in value['items']
                }
            else:
                # Recursively deserialize regular dict values
                return {k: cls._deserialize_value(v) for k, v in value.items()}
        elif value_type is list:
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

        The backend is selected by the ``OPENCELL_ENV`` environment variable:

        - ``development`` — uses the local SQLite database via
          ``steer_opencell_data.DataManager``. No network calls, works offline.
          Requires ``steer-opencell-data`` to be installed with ``database.db``.
        - ``production`` (default) — uses the REST API via
          ``steer_core.Data.DataManager``. Requires the ``API_URL`` env var
          pointing to the deployed Lambda endpoint.

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
        from steer_core.Data import is_development
        _dev_mode = is_development()
        if _dev_mode:
            from steer_opencell_data.DataManager import DataManager
        else:
            from steer_core.Data.DataManager import DataManager
            from steer_core.Data.DataManager import NotFoundError

        database = DataManager()
        
        # Get list of tables to search
        if table_name:
            tables_to_search = [table_name]
        else:
            if not hasattr(cls, '_table_name'):
                raise NotImplementedError(
                    f"{cls.__name__} must define a '_table_name' class variable "
                    "or provide 'table_name' argument"
                )
            
            if isinstance(cls._table_name, (list, tuple)):
                tables_to_search = cls._table_name
            else:
                tables_to_search = [cls._table_name]
        
        # In production mode, attempt get_data directly (single HTTP call)
        # instead of listing all names first.  In development mode (SQLite)
        # we keep the list-then-fetch approach since it has no network cost.
        for table in tables_to_search:
            if _dev_mode:
                available = database.get_unique_values(table, "name")
                if name not in available:
                    continue
                data = database.get_data(table, condition=f"name = '{name}'")
            else:
                try:
                    data = database.get_data(table, condition=f"name = '{name}'")
                except NotFoundError:
                    continue

            serialized_bytes = data["object"].iloc[0]
            return cls.deserialize(serialized_bytes)
        
        # Not found — build a helpful error message
        all_available = []
        for table in tables_to_search:
            all_available.extend(database.get_unique_values(table, "name"))
        
        raise ValueError(
            f"'{name}' not found in tables {tables_to_search}. "
            f"Available: {all_available}"
        )



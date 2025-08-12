"""
Serialization utilities module

Re-exports serialization functionality from sage.common.utils.serialization
"""

try:
    from sage.common.utils.serialization.dill import serialize_object, deserialize_object
    from sage.common.utils.serialization.exceptions import SerializationError
    from sage.common.utils.serialization.config import *
except ImportError:
    # Fallback if sage-common is not available
    class SerializationError(Exception):
        pass
    
    def serialize_object(obj):
        import pickle
        return pickle.dumps(obj)
    
    def deserialize_object(data):
        import pickle
        return pickle.loads(data)

# Also provide dill_serializer for backward compatibility
try:
    from sage.common.utils.serialization import dill_serializer
except ImportError:
    class dill_serializer:
        @staticmethod
        def serialize_object(obj):
            return serialize_object(obj)
        
        @staticmethod
        def deserialize_object(data):
            return deserialize_object(data)

__all__ = [
    "serialize_object",
    "deserialize_object",
    "SerializationError",
    "dill_serializer"
]

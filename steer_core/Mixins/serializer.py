
class SerializerMixin:

    def serialize(self) -> str:
        """
        Serialize an object to a string representation.
        
        Parameters
        ----------
        obj : Type
            The object to serialize.
        
        Returns
        -------
        str
            The serialized string representation of the object.
        """
        import base64
        from pickle import dumps

        pickled = dumps(self)
        based = base64.b64encode(pickled).decode('utf-8')
        return based 


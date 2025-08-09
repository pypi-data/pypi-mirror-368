from typing import Any, Union
import msgspec


class JsonHelper:
    '''
    A helper class for JSON encoding and decoding using msgspec.
    This class provides static methods to encode and decode JSON data, handling errors gracefully.
    Attributes
    ----------
    None
    
    Methods
    ----------
    decode(data: Union[str, bytes], raise_error: bool = False) -> Any:
        Decodes JSON data into a Python object. If `raise_error` is True, it raises an error on failure.
    encode(data: Any, raise_error: bool = False) -> Union[str, Any]:
        Encodes a Python object into JSON format. If `raise_error` is True, it raises an error on failure.
    '''

    @staticmethod
    def decode(data: Union[str, bytes], raise_error: bool = False) -> Any:
        try:
            return msgspec.json.decode(data)
        except Exception as error:
            if raise_error:
                raise error
            return data

    @staticmethod
    def encode(data: Any, raise_error: bool = False) -> Union[str, Any]:
        try:
            encoded = msgspec.json.encode(data)
            if isinstance(encoded, (bytes, bytearray)):
                return encoded.decode("utf-8")
            return encoded  # pragma: no cover
        except Exception as error:
            if raise_error:
                raise error
            return data

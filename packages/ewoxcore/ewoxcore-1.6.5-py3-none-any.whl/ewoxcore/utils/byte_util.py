from typing import Any, Callable, Generic, List, Dict, Text, Optional, Tuple, Union, TypeVar, Type
import base64

class ByteUtil:

    @staticmethod
    def to_base64(data: bytes) -> str:
        """
        Convert bytes to a Base64 encoded string.
        """
        return base64.b64encode(data).decode('utf-8')
    

    @staticmethod
    def from_base64(encoded_data: str) -> bytes:
        """
        Convert a Base64 encoded string back to bytes.
        """
        return base64.b64decode(encoded_data.encode('utf-8'), validate=True)
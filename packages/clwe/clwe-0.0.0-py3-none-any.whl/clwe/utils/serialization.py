import base64
import json
from typing import Any, Dict, Union

def serialize_key(key_data: bytes, key_type: str = "public") -> str:
    encoded = base64.b64encode(key_data).decode('ascii')
    
    key_info = {
        'type': key_type,
        'data': encoded,
        'version': '0.0.1'
    }
    
    return json.dumps(key_info)

def deserialize_key(serialized_key: str) -> bytes:
    key_info = json.loads(serialized_key)
    
    if 'data' not in key_info:
        raise ValueError("Invalid serialized key format")
    
    return base64.b64decode(key_info['data'])

def serialize_encrypted_data(data: Dict[str, Any]) -> str:
    return json.dumps(data)

def deserialize_encrypted_data(serialized_data: str) -> Dict[str, Any]:
    return json.loads(serialized_data)

def compact_serialize(data: bytes) -> str:
    return base64.b64encode(data).decode('ascii')

def compact_deserialize(encoded_data: str) -> bytes:
    return base64.b64decode(encoded_data)
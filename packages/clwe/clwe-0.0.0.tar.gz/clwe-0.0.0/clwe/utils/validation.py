import re
from typing import Any, Dict, Union

def validate_input(data: Any, input_type: str) -> bool:
    if input_type == "message":
        return isinstance(data, (str, bytes)) and len(str(data)) > 0
    elif input_type == "password":
        return isinstance(data, str) and len(data) >= 1
    elif input_type == "security_level":
        return data in [128, 192, 256]
    elif input_type == "key_data":
        return isinstance(data, bytes) and len(data) > 0
    else:
        return False

def validate_parameters(params: Dict[str, Any]) -> bool:
    required_fields = ['lattice_dimension', 'modulus', 'error_bound', 'security_level']
    
    for field in required_fields:
        if field not in params:
            return False
    
    if params['lattice_dimension'] <= 0:
        return False
    if params['modulus'] <= 0:
        return False
    if params['error_bound'] <= 0:
        return False
    if params['security_level'] not in [128, 192, 256]:
        return False
    
    return True

def validate_color(color: tuple) -> bool:
    if not isinstance(color, tuple) or len(color) != 3:
        return False
    
    return all(isinstance(c, int) and 0 <= c <= 255 for c in color)

def validate_matrix_dimensions(matrix_a: Any, matrix_b: Any) -> bool:
    try:
        import numpy as np
        
        if not isinstance(matrix_a, np.ndarray) or not isinstance(matrix_b, np.ndarray):
            return False
        
        return matrix_a.shape[1] == matrix_b.shape[0]
    except ImportError:
        return False

def sanitize_input(data: str) -> str:
    if not isinstance(data, str):
        return str(data)
    
    sanitized = re.sub(r'[^\w\s\-\.\@]', '', data)
    return sanitized[:1000]
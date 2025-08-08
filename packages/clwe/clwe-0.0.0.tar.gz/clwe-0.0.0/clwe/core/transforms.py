import hashlib
import hmac
import numpy as np
from typing import Tuple, List, Dict, Any
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from .parameters import CLWEParameters

class ColorTransformEngine:
    def __init__(self, params: CLWEParameters):
        self.params = params
        self.modulus = params.modulus
        self.entropy = int(params.color_transform_entropy)
        
        self.geometric_seed = hashlib.sha256(f"CLWE_GEOMETRIC_{params.security_level}".encode()).digest()
        self.transform_key = hashlib.sha256(f"CLWE_TRANSFORM_{params.security_level}".encode()).digest()[:16]
        self.hmac_key = hashlib.sha256(f"CLWE_HMAC_{params.security_level}".encode()).digest()[:16]
    
    def color_transform(self, lattice_value: int, position: int, color_history: List[Tuple[int, int, int]] = None) -> Tuple[int, int, int]:
        if color_history is None:
            color_history = []
        
        pos_bytes = position.to_bytes(8, 'big')
        
        history_bytes = b''
        recent_colors = color_history[-32:] if len(color_history) >= 32 else color_history
        for color in recent_colors:
            history_bytes += bytes([color[0], color[1], color[2]])
        
        round1 = pos_bytes + history_bytes + self.geometric_seed
        round2 = hmac.new(self.hmac_key, round1, hashlib.sha256).digest()
        round3 = hmac.new(self.transform_key, round2, hashlib.sha256).digest()
        
        combined_value = lattice_value + int.from_bytes(round3[:8], 'big')
        
        r = (combined_value * 17 + 113) % 256
        g = (combined_value * 23 + 181) % 256
        b = (combined_value * 31 + 229) % 256
        
        return (r, g, b)
    
    def inverse_color_transform(self, color: Tuple[int, int, int], position: int, color_history: List[Tuple[int, int, int]] = None) -> int:
        if color_history is None:
            color_history = []
            
        pos_bytes = position.to_bytes(8, 'big')
        
        history_bytes = b''
        recent_colors = color_history[-32:] if len(color_history) >= 32 else color_history
        for color in recent_colors:
            history_bytes += bytes([color[0], color[1], color[2]])
        
        round1 = pos_bytes + history_bytes + self.geometric_seed
        round2 = hmac.new(self.hmac_key, round1, hashlib.sha256).digest()
        round3 = hmac.new(self.transform_key, round2, hashlib.sha256).digest()
        
        return int.from_bytes(round3[:8], 'big') % self.params.modulus
    
    def lattice_to_color(self, lattice_point: np.ndarray, index: int, context: dict) -> Tuple[int, int, int]:
        if isinstance(lattice_point, np.ndarray):
            lattice_value = int(np.sum(lattice_point)) % self.params.modulus
        else:
            lattice_value = int(lattice_point) % self.params.modulus
            
        return self.color_transform(lattice_value, index)
    
    def create_color_pattern(self, colors: list, pattern_type: str) -> list:
        if pattern_type == 'spiral':
            return colors[::-1]
        elif pattern_type == 'grid':
            return colors
        else:
            return colors
    
    def create_visual_representation(self, colors: list) -> bytes:
        result = bytearray()
        for color in colors:
            result.extend([color[0], color[1], color[2]])
        return bytes(result)
    
    def extract_colors_from_image(self, image_data) -> List[Tuple[int, int, int]]:
        if isinstance(image_data, dict) and 'colors' in image_data:
            return image_data['colors']
        elif isinstance(image_data, list):
            return image_data
        else:
            colors = []
            for i in range(0, len(image_data), 3):
                if i + 2 < len(image_data):
                    r, g, b = image_data[i], image_data[i+1], image_data[i+2]
                    colors.append((r, g, b))
            return colors
    
    def color_to_lattice(self, color: Tuple[int, int, int], index: int, context: dict) -> List[int]:
        r, g, b = color
        
        lattice_chunk = [
            r * 256 + g,
            b * 256 + index % 256,
            (r + g + b) % 256
        ]
        
        return lattice_chunk
    
    def fast_color_transform(self, data: bytes, password: str = "default_transform_key") -> Tuple[int, int, int]:
            
        password_bytes = password.encode('utf-8')
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=96,
            salt=data + b'ULTRA_FAST_RGB_COMBINED',
            iterations=512,
            backend=default_backend()
        )
        
        combined_hash = kdf.derive(password_bytes + data)
        
        r_value = int.from_bytes(combined_hash[:4], 'big') % 256
        g_value = int.from_bytes(combined_hash[32:36], 'big') % 256  
        b_value = int.from_bytes(combined_hash[64:68], 'big') % 256
        
        return (r_value, g_value, b_value)
    
    def enhanced_color_transform(self, data: bytes, index: int, use_randomness: bool = True) -> Tuple[int, int, int]:
        """Enhanced color transformation with better entropy and randomness"""
        # Create multiple layers of transformation
        layer1 = hashlib.sha256(data + f"LAYER1_{index}".encode()).digest()
        layer2 = hmac.new(self.hmac_key, layer1 + f"LAYER2_{index}".encode(), hashlib.sha256).digest()
        layer3 = hmac.new(self.transform_key, layer2 + f"LAYER3_{index}".encode(), hashlib.sha256).digest()
        
        if use_randomness:
            # Add additional entropy for uniqueness
            import os
            random_bytes = os.urandom(8)
            layer3 = hashlib.sha256(layer3 + random_bytes).digest()
        
        # Use different parts of the hash for each color component
        r_base = int.from_bytes(layer3[0:4], 'big')
        g_base = int.from_bytes(layer3[8:12], 'big') 
        b_base = int.from_bytes(layer3[16:20], 'big')
        
        # Apply non-linear transformations to increase color space coverage
        r = ((r_base * 7919) + (r_base >> 8) * 127) % 256
        g = ((g_base * 7727) + (g_base >> 12) * 191) % 256
        b = ((b_base * 7573) + (b_base >> 16) * 223) % 256
        
        # Ensure minimum color difference to avoid similar colors
        if index > 0:
            r = (r + index * 41) % 256
            g = (g + index * 47) % 256
            b = (b + index * 53) % 256
        
        return (r, g, b)
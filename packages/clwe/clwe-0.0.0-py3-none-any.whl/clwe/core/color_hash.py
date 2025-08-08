import hashlib
import hmac
import os
import time
import random
import base64
import io
from typing import Tuple, Union, List, Dict
from .parameters import get_params
from .transforms import ColorTransformEngine

class ColorHash:
    def __init__(self, security_level: int = 128):
        self.security_level = security_level
        self.params = get_params(security_level, optimized=True)
        self.color_engine = ColorTransformEngine(self.params)
    
    def hash(self, data: Union[str, bytes], security_level: int = None) -> Tuple[int, int, int]:
        if security_level is None:
            security_level = self.security_level
        
        if isinstance(data, str):
            data = data.encode('utf-8')
        
        hash_value = hashlib.sha256(data).digest()
        
        return self.color_engine.fast_color_transform(hash_value)
    
    def hash_multi_color(self, data: Union[str, bytes], num_colors: int = 6, use_randomness: bool = True) -> List[Tuple[int, int, int]]:
        """Generate multiple color hashes for the same content with optional randomness"""
        if isinstance(data, str):
            data = data.encode('utf-8')
        
        colors = []
        base_hash = hashlib.sha256(data).digest()
        
        # Add timestamp and random salt if randomness is enabled
        if use_randomness:
            timestamp = int(time.time() * 1000000).to_bytes(8, 'big')  # microsecond precision
            random_salt = os.urandom(16)
            entropy_source = base_hash + timestamp + random_salt
        else:
            entropy_source = base_hash
        
        for i in range(num_colors):
            # Create unique seed for each color using multiple rounds of hashing
            color_seed = hashlib.sha256(entropy_source + f"COLOR_{i}".encode()).digest()
            
            # Apply additional transformations to increase uniqueness
            for round_num in range(3):  # Multiple rounds for better distribution
                color_seed = hashlib.sha256(color_seed + f"ROUND_{round_num}_{i}".encode()).digest()
            
            # Generate color using the enhanced transform
            color = self.color_engine.enhanced_color_transform(color_seed, i, use_randomness)
            colors.append(color)
        
        return colors
    
    def hash_pattern(self, data: Union[str, bytes], num_colors: int = 6, pattern_type: str = "dynamic") -> dict:
        """Generate colored hash with specific pattern arrangements"""
        colors = self.hash_multi_color(data, num_colors, use_randomness=True)
        
        # Generate different pattern arrangements
        patterns = {
            "original": colors,
            "reversed": colors[::-1],
            "alternating": [colors[i] if i % 2 == 0 else colors[-(i//2+1)] for i in range(len(colors))],
            "spiral": self._create_spiral_pattern(colors),
            "gradient": self._create_gradient_pattern(colors),
            "random": self._create_random_pattern(colors)
        }
        
        if pattern_type == "dynamic":
            # Choose pattern based on data hash
            data_bytes = data if isinstance(data, bytes) else data.encode('utf-8')
            pattern_hash = hashlib.sha256(data_bytes).hexdigest()
            pattern_index = int(pattern_hash[-1], 16) % len(patterns)
            selected_pattern = list(patterns.keys())[pattern_index]
        else:
            selected_pattern = pattern_type if pattern_type in patterns else "original"
        
        return {
            "colors": patterns[selected_pattern],
            "pattern_type": selected_pattern,
            "all_patterns": patterns,
            "hash_metadata": {
                "num_colors": num_colors,
                "timestamp": int(time.time()),
                "data_length": len(data if isinstance(data, bytes) else data.encode('utf-8'))
            }
        }
    
    def _create_spiral_pattern(self, colors: List[Tuple[int, int, int]]) -> List[Tuple[int, int, int]]:
        """Create spiral-like color arrangement"""
        if len(colors) < 4:
            return colors
        
        pattern = []
        mid = len(colors) // 2
        for i in range(mid):
            pattern.append(colors[i])
            if mid + i < len(colors):
                pattern.append(colors[mid + i])
        
        return pattern
    
    def _create_gradient_pattern(self, colors: List[Tuple[int, int, int]]) -> List[Tuple[int, int, int]]:
        """Create gradient-like color arrangement"""
        # Sort colors by brightness for gradient effect
        brightness = lambda c: (c[0] * 299 + c[1] * 587 + c[2] * 114) / 1000
        return sorted(colors, key=brightness)
    
    def _create_random_pattern(self, colors: List[Tuple[int, int, int]]) -> List[Tuple[int, int, int]]:
        """Create random color arrangement based on deterministic seed"""
        # Use color data to create deterministic randomness
        seed_data = b''.join(bytes(c) for c in colors)
        seed = int.from_bytes(hashlib.sha256(seed_data).digest()[:4], 'big')
        
        random.seed(seed)
        shuffled = colors.copy()
        random.shuffle(shuffled)
        random.seed()  # Reset to system time
        
        return shuffled
    
    def hash_to_image(self, data: Union[str, bytes], num_colors: int = 6, pattern_type: str = "dynamic", 
                      image_width: int = None, image_height: int = None, use_randomness: bool = True) -> Dict:
        """Generate color hash as a visual pixel string image"""
        if isinstance(data, str):
            data = data.encode('utf-8')
        
        # Generate colors and pattern
        pattern_hash = self.hash_pattern(data, num_colors=num_colors, pattern_type=pattern_type)
        colors = pattern_hash['colors']
        
        # Calculate optimal image dimensions if not provided
        if image_width is None or image_height is None:
            # Default: horizontal strip with height=1 and width=number of colors
            image_width = num_colors if image_width is None else image_width
            image_height = 1 if image_height is None else image_height
        
        # Generate pixel data
        pixel_data = self._generate_pixel_layout(colors, image_width, image_height, pattern_hash['pattern_type'])
        
        # Create image string representation
        image_string = self._create_image_string(pixel_data, image_width, image_height)
        
        # Generate PNG byte data for actual image output
        png_data = self._create_png_image(pixel_data, image_width, image_height)
        
        return {
            "colors": colors,
            "pattern_type": pattern_hash['pattern_type'],
            "image_data": {
                "width": image_width,
                "height": image_height,
                "pixel_string": image_string,
                "png_data": png_data,
                "png_base64": base64.b64encode(png_data).decode('utf-8')
            },
            "hash_metadata": pattern_hash['hash_metadata'],
            "visual_signature": self._create_visual_signature(colors, pattern_hash['pattern_type'])
        }
    
    def _generate_pixel_layout(self, colors: List[Tuple[int, int, int]], width: int, height: int, pattern_type: str) -> List[List[Tuple[int, int, int]]]:
        """Generate 2D pixel layout based on colors and pattern"""
        total_pixels = width * height
        
        # Create base pattern
        if pattern_type == "spiral":
            pixel_colors = self._create_spiral_layout(colors, width, height)
        elif pattern_type == "gradient":
            pixel_colors = self._create_gradient_layout(colors, width, height)
        elif pattern_type == "random":
            pixel_colors = self._create_random_layout(colors, width, height)
        else:
            # Default: repeat colors in order
            pixel_colors = []
            for i in range(total_pixels):
                pixel_colors.append(colors[i % len(colors)])
        
        # Convert to 2D array
        pixel_data = []
        for y in range(height):
            row = []
            for x in range(width):
                idx = y * width + x
                if idx < len(pixel_colors):
                    row.append(pixel_colors[idx])
                else:
                    row.append(colors[0])  # Fallback
            pixel_data.append(row)
        
        return pixel_data
    
    def _create_spiral_layout(self, colors: List[Tuple[int, int, int]], width: int, height: int) -> List[Tuple[int, int, int]]:
        """Create spiral pattern layout"""
        total_pixels = width * height
        pixel_colors = []
        
        # Create spiral coordinates
        spiral_coords = []
        visited = [[False] * width for _ in range(height)]
        
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]  # right, down, left, up
        x, y, direction = 0, 0, 0
        
        for i in range(total_pixels):
            if 0 <= x < width and 0 <= y < height and not visited[y][x]:
                spiral_coords.append((x, y))
                visited[y][x] = True
                
                # Try to continue in current direction
                next_x = x + directions[direction][0]
                next_y = y + directions[direction][1]
                
                # Change direction if needed
                if (next_x < 0 or next_x >= width or next_y < 0 or next_y >= height or 
                    visited[next_y][next_x]):
                    direction = (direction + 1) % 4
                    next_x = x + directions[direction][0]
                    next_y = y + directions[direction][1]
                
                x, y = next_x, next_y
        
        # Assign colors to spiral coordinates
        for i, (sx, sy) in enumerate(spiral_coords):
            color_idx = (i // (total_pixels // len(colors))) % len(colors)
            pixel_colors.append(colors[color_idx])
        
        return pixel_colors
    
    def _create_gradient_layout(self, colors: List[Tuple[int, int, int]], width: int, height: int) -> List[Tuple[int, int, int]]:
        """Create gradient pattern layout"""
        total_pixels = width * height
        pixel_colors = []
        
        # Sort colors by brightness for smooth gradient
        brightness = lambda c: (c[0] * 299 + c[1] * 587 + c[2] * 114) / 1000
        sorted_colors = sorted(colors, key=brightness)
        
        for i in range(total_pixels):
            # Create smooth gradient across the image
            gradient_position = i / (total_pixels - 1) if total_pixels > 1 else 0
            color_index = gradient_position * (len(sorted_colors) - 1)
            base_index = int(color_index)
            next_index = min(base_index + 1, len(sorted_colors) - 1)
            
            # Use the base color (could be enhanced with interpolation)
            pixel_colors.append(sorted_colors[base_index])
        
        return pixel_colors
    
    def _create_random_layout(self, colors: List[Tuple[int, int, int]], width: int, height: int) -> List[Tuple[int, int, int]]:
        """Create deterministic random layout"""
        total_pixels = width * height
        
        # Create deterministic random sequence
        seed_data = b''.join(bytes(c) for c in colors)
        seed = int.from_bytes(hashlib.sha256(seed_data).digest()[:4], 'big')
        
        random.seed(seed)
        pixel_colors = []
        for i in range(total_pixels):
            pixel_colors.append(random.choice(colors))
        random.seed()  # Reset to system time
        
        return pixel_colors
    
    def _create_image_string(self, pixel_data: List[List[Tuple[int, int, int]]], width: int, height: int) -> str:
        """Create ASCII/text representation of the image"""
        image_lines = []
        image_lines.append(f"Color Hash Image ({width}x{height})")
        image_lines.append("=" * (width * 8))
        
        for y, row in enumerate(pixel_data):
            line_parts = []
            for x, (r, g, b) in enumerate(row):
                # Create compact color representation
                hex_color = f"#{r:02x}{g:02x}{b:02x}"
                line_parts.append(hex_color)
            image_lines.append(" ".join(line_parts))
        
        image_lines.append("=" * (width * 8))
        return "\n".join(image_lines)
    
    def _create_png_image(self, pixel_data: List[List[Tuple[int, int, int]]], width: int, height: int) -> bytes:
        """Create actual PNG image data"""
        try:
            from PIL import Image
            
            # Create new image
            img = Image.new('RGB', (width, height))
            
            # Set pixel data
            for y, row in enumerate(pixel_data):
                for x, (r, g, b) in enumerate(row):
                    img.putpixel((x, y), (r, g, b))
            
            # Convert to PNG bytes
            img_buffer = io.BytesIO()
            img.save(img_buffer, format='PNG')
            return img_buffer.getvalue()
            
        except ImportError:
            # Fallback: create a simple bitmap-like representation
            return self._create_simple_bitmap(pixel_data, width, height)
    
    def _create_simple_bitmap(self, pixel_data: List[List[Tuple[int, int, int]]], width: int, height: int) -> bytes:
        """Create simple bitmap representation without PIL"""
        # Create a simple RGB bitmap format
        header = f"CLWE_BITMAP_{width}x{height}_RGB\n".encode('utf-8')
        pixel_bytes = bytearray()
        
        for row in pixel_data:
            for r, g, b in row:
                pixel_bytes.extend([r, g, b])
        
        return header + bytes(pixel_bytes)
    
    def _create_visual_signature(self, colors: List[Tuple[int, int, int]], pattern_type: str) -> str:
        """Create a compact visual signature string"""
        # Create a shortened visual representation
        signature_parts = [f"P:{pattern_type[:3].upper()}"]
        
        for i, (r, g, b) in enumerate(colors[:6]):  # Limit to 6 colors for readability
            signature_parts.append(f"#{r:02x}{g:02x}{b:02x}")
        
        return "|".join(signature_parts)
    
    def save_hash_image(self, data: Union[str, bytes], output_path: str, **kwargs) -> Dict:
        """Save color hash as image file"""
        hash_result = self.hash_to_image(data, **kwargs)
        
        # Save PNG image
        with open(output_path, 'wb') as f:
            f.write(hash_result['image_data']['png_data'])
        
        # Also save metadata
        metadata_path = output_path + ".meta"
        metadata = {
            "colors": hash_result['colors'],
            "pattern_type": hash_result['pattern_type'],
            "visual_signature": hash_result['visual_signature'],
            "image_dimensions": f"{hash_result['image_data']['width']}x{hash_result['image_data']['height']}",
            "hash_metadata": hash_result['hash_metadata']
        }
        
        import json
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        return {
            "image_file": output_path,
            "metadata_file": metadata_path,
            "hash_result": hash_result
        }
    
    def verify(self, data: Union[str, bytes], expected_hash: Tuple[int, int, int]) -> bool:
        computed_hash = self.hash(data)
        return computed_hash == expected_hash
    
    def hash_with_salt(self, data: Union[str, bytes], salt: bytes) -> Tuple[int, int, int]:
        if isinstance(data, str):
            data = data.encode('utf-8')
        
        salted_data = salt + data
        hash_value = hashlib.sha256(salted_data).digest()
        
        return self.color_engine.fast_color_transform(hash_value)
    
    def hmac_hash(self, data: Union[str, bytes], key: bytes) -> Tuple[int, int, int]:
        if isinstance(data, str):
            data = data.encode('utf-8')
        
        mac = hmac.new(key, data, hashlib.sha256)
        hash_value = mac.digest()
        
        return self.color_engine.fast_color_transform(hash_value)
    
    def derive_key(self, password: str, salt: bytes, iterations: int = 10000) -> bytes:
        password_bytes = password.encode('utf-8')
        
        from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
        from cryptography.hazmat.primitives import hashes
        from cryptography.hazmat.backends import default_backend
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=iterations,
            backend=default_backend()
        )
        
        return kdf.derive(password_bytes)
    
    def hash_chain(self, data: Union[str, bytes], rounds: int = 1000) -> Tuple[int, int, int]:
        if isinstance(data, str):
            data = data.encode('utf-8')
        
        current_hash = data
        for _ in range(rounds):
            current_hash = hashlib.sha256(current_hash).digest()
        
        return self.color_engine.fast_color_transform(current_hash)
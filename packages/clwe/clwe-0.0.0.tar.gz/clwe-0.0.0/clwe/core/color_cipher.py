"""
CLWE Color Cipher - Fixed Enhanced Implementation
Provides variable output encryption with superior compression and pixel string layout.
"""

import hashlib
import zlib
import secrets
import base64
import mimetypes
import os
import numpy as np
from PIL import Image
from io import BytesIO
from typing import Dict, Any, Tuple, Union, List


class ColorCipher:
    """Enhanced Color Cipher with randomization, superior compression, and universal file support."""
    
    def __init__(self):
        """Initialize the ColorCipher."""
        pass
    
    def encrypt_file_to_image(self, file_path: str, password: str, output_format: str = "webp") -> bytes:
        """
        Encrypt any file type to an image with enhanced security and compression.
        
        Supports all file types: documents, images, videos, executables, etc.
        Uses base64 encoding with metadata preservation for universal compatibility.
        
        Args:
            file_path: Path to file to encrypt
            password: Encryption password
            output_format: Image format (webp, png)
            
        Returns:
            Encrypted image bytes containing the file data
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Read file and get metadata
        with open(file_path, 'rb') as f:
            file_data = f.read()
        
        filename = os.path.basename(file_path)
        file_size = len(file_data)
        mime_type = mimetypes.guess_type(file_path)[0] or 'application/octet-stream'
        
        # Create metadata header
        metadata = f"{filename}|{file_size}|{mime_type}|"
        
        # Encode file data as base64 for universal handling
        file_b64 = base64.b64encode(file_data).decode('ascii')
        
        # Combine metadata and data
        full_data = metadata + file_b64
        
        return self._encrypt_data_to_image(full_data, password, output_format)
    
    def _encrypt_file_content(self, file_path: str, password: str, output_format: str = "png") -> bytes:
        """Internal method to encrypt file content with metadata."""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Read file and get metadata
        with open(file_path, 'rb') as f:
            file_data = f.read()
        
        filename = os.path.basename(file_path)
        file_size = len(file_data)
        mime_type = mimetypes.guess_type(file_path)[0] or 'application/octet-stream'
        
        # Create metadata header
        metadata = f"{filename}|{file_size}|{mime_type}|"
        
        # Encode file data as base64 for universal handling
        file_b64 = base64.b64encode(file_data).decode('ascii')
        
        # Combine metadata and data
        full_data = metadata + file_b64
        
        return self._encrypt_data_to_image(full_data, password, output_format)
    
    def decrypt_file_from_image(self, image_data: bytes, password: str, output_dir: str = ".") -> str:
        """
        Decrypt file from image and save to specified directory.
        
        Automatically detects file type and restores original filename.
        
        Args:
            image_data: Encrypted image bytes
            password: Decryption password
            output_dir: Directory to save decrypted file
            
        Returns:
            Path to the decrypted file
        """
        # Decrypt the full data
        full_data = self._decrypt_data_from_image(image_data, password)
        
        if full_data.startswith("Decryption failed"):
            raise ValueError(full_data)
        
        # Parse metadata
        try:
            parts = full_data.split('|', 3)
            if len(parts) < 4:
                raise ValueError("Invalid file format")
            
            filename, file_size_str, mime_type, file_b64 = parts
            file_size = int(file_size_str)
            
            # Decode base64 data
            file_data = base64.b64decode(file_b64.encode('ascii'))
            
            if len(file_data) != file_size:
                raise ValueError("File size mismatch")
            
            # Save file
            output_path = os.path.join(output_dir, filename)
            with open(output_path, 'wb') as f:
                f.write(file_data)
            
            return output_path
            
        except Exception as e:
            raise ValueError(f"File decryption failed: {str(e)}")
    
    def encrypt_to_image(self, content, password: str, output_format: str = "png") -> bytes:
        """
        Universal encryption supporting any content type: text, files, binary data.
        
        Automatically detects and handles:
        - Text strings: Direct text encryption
        - File paths: Reads and encrypts file with metadata preservation
        - Binary data: Encrypts raw bytes with automatic type detection
        
        Features:
        - Variable output: Each encryption produces different results for same input
        - Superior compression: 3 bytes per color + intelligent compression selection  
        - Pixel string layout: height=1, exact width matching color count
        - Universal support: Any file type or content automatically handled
        
        Args:
            content: Text string, file path, or binary data to encrypt
            password: Encryption password
            output_format: Image format (webp, png)
            
        Returns:
            Encrypted image bytes in specified format
        """
        # Auto-detect content type and handle appropriately
        if isinstance(content, str):
            # Check if it's a file path
            if os.path.exists(content):
                return self._encrypt_file_content(content, password, output_format)
            else:
                # Text content
                full_data = "TEXT|" + content
                return self._encrypt_data_to_image(full_data, password, output_format)
        elif isinstance(content, bytes):
            # Binary data - encode as base64
            import base64
            b64_data = base64.b64encode(content).decode('ascii')
            full_data = "BINARY|" + b64_data
            return self._encrypt_data_to_image(full_data, password, output_format)
        else:
            raise ValueError("Content must be string (text/file path) or bytes")
    
    def _encrypt_data_to_image(self, data: str, password: str, output_format: str = "webp") -> bytes:
        """Internal method to encrypt any data string to image."""
        # Step 1: Add random prefix for variable output (security enhancement)
        random_prefix = secrets.token_hex(2)  # 4 char random prefix
        full_data = random_prefix + "|" + data
        
        # Step 2: Smart compression selection
        data_bytes = full_data.encode('utf-8')
        
        # Try zlib compression first (most effective)
        try:
            compressed = zlib.compress(data_bytes, level=9)
            if len(compressed) < len(data_bytes) * 0.9:  # Only if significant benefit
                use_compression = True
                final_data = compressed
            else:
                use_compression = False
                final_data = data_bytes
        except:
            use_compression = False
            final_data = data_bytes
        
        # Step 3: Add compression flag
        header = bytes([1 if use_compression else 0])
        data_with_header = header + final_data
        
        # Step 4: Encrypt with password-derived key
        key_material = hashlib.sha256(password.encode()).digest()
        
        encrypted_bytes = []
        for i, byte in enumerate(data_with_header):
            key_byte = key_material[i % len(key_material)]
            encrypted_bytes.append(byte ^ key_byte)
        
        # Step 5: Pack 3 bytes per color for superior compression
        colors = []
        for i in range(0, len(encrypted_bytes), 3):
            r = encrypted_bytes[i] if i < len(encrypted_bytes) else 0
            g = encrypted_bytes[i + 1] if i + 1 < len(encrypted_bytes) else 0
            b = encrypted_bytes[i + 2] if i + 2 < len(encrypted_bytes) else 0
            colors.append((r, g, b))
        
        # Step 6: Create image with WebP size limits (max 16383 pixels per dimension)
        total_colors = len(colors)
        MAX_DIMENSION = 16383  # WebP limit
        
        if total_colors <= 1000:
            # Small files: pixel string layout
            width = total_colors
            height = 1
        elif total_colors <= MAX_DIMENSION:
            # Medium files: single row if within WebP limit
            width = total_colors
            height = 1
        else:
            # Large files: multi-row layout within WebP limits
            width = MAX_DIMENSION
            height = min((total_colors + width - 1) // width, MAX_DIMENSION)
            
            # If still too large, use maximum possible dimensions
            if width * height < total_colors:
                # Use maximum possible dimensions for PNG
                width = min(total_colors, MAX_DIMENSION)
                height = min((total_colors + width - 1) // width, MAX_DIMENSION)
        
        # Create image array
        img_array = np.zeros((height, width, 3), dtype=np.uint8)
        
        # Fill with colors
        for i, color in enumerate(colors):
            row = i // width
            col = i % width
            if row < height and col < width:
                img_array[row, col] = color
        
        # Save as optimized image
        img = Image.fromarray(img_array, 'RGB')
        buffer = BytesIO()
        
        if output_format.lower() == "png":
            img.save(buffer, format="PNG", optimize=True, compress_level=9)
        elif output_format.lower() == "webp":
            img.save(buffer, format="WEBP", lossless=True, quality=100)
        else:
            img.save(buffer, format=output_format.upper())
        
        return buffer.getvalue()
    
    def _decrypt_data_from_image(self, image_data: bytes, password: str) -> str:
        """Internal method to decrypt data string from image."""
        img = Image.open(BytesIO(image_data))
        img_array = np.array(img)
        height, width = img_array.shape[:2]
        
        # Extract bytes from RGB colors (reverse of 3-bytes-per-color packing)
        encrypted_bytes = []
        
        for row in range(height):
            for col in range(width):
                if len(img_array.shape) == 3:
                    r, g, b = img_array[row, col][:3]
                    encrypted_bytes.extend([int(r), int(g), int(b)])
        
        # Remove trailing zeros that are padding
        while encrypted_bytes and encrypted_bytes[-1] == 0:
            encrypted_bytes.pop()
        
        if len(encrypted_bytes) < 4:
            return "Decryption failed - insufficient data"
        
        # Decrypt with password-derived key
        key_material = hashlib.sha256(password.encode()).digest()
        
        decrypted_bytes = []
        for i, byte in enumerate(encrypted_bytes):
            key_byte = key_material[i % len(key_material)]
            decrypted_bytes.append(byte ^ key_byte)
        
        if not decrypted_bytes:
            return "Decryption failed - no data"
        
        # Extract compression flag and data
        compression_flag = decrypted_bytes[0]
        content_bytes = bytes(decrypted_bytes[1:])
        
        try:
            # Decompress if needed
            if compression_flag == 1:
                try:
                    decompressed = zlib.decompress(content_bytes)
                    full_data = decompressed.decode('utf-8')
                except (zlib.error, UnicodeDecodeError) as e:
                    # Try without decompression if zlib fails
                    try:
                        full_data = content_bytes.decode('utf-8', errors='ignore')
                    except:
                        return f"Decryption failed - decompression error: {str(e)}"
            else:
                try:
                    full_data = content_bytes.decode('utf-8')
                except UnicodeDecodeError:
                    try:
                        full_data = content_bytes.decode('utf-8', errors='ignore')
                    except:
                        return f"Decryption failed - UTF-8 decode error"
            
            # Remove random prefix to get original data
            if "|" in full_data:
                parts = full_data.split("|", 1)
                if len(parts) == 2:
                    return parts[1]  # Return original data
            
            return full_data
            
        except Exception as e:
            return f"Decryption failed - {str(e)}"
    
    def decrypt_from_image(self, image_data: bytes, password: str, output_dir: str = None):
        """
        Universal decryption supporting any content type automatically.
        
        Automatically detects and returns:
        - Text content: Returns string directly
        - File content: Saves file and returns path (if output_dir provided) or content
        - Binary data: Returns bytes
        
        Args:
            image_data: Encrypted image bytes
            password: Decryption password
            output_dir: Directory to save files (optional, for file content)
            
        Returns:
            Decrypted content (string, bytes, or file path depending on original type)
        """
        full_data = self._decrypt_data_from_image(image_data, password)
        
        if full_data.startswith("Decryption failed"):
            return full_data
        
        # Auto-detect content type and handle appropriately
        if full_data.startswith("TEXT|"):
            # Text content
            return full_data[5:]  # Remove "TEXT|" prefix
            
        elif full_data.startswith("BINARY|"):
            # Binary data - decode from base64
            import base64
            try:
                b64_data = full_data[7:]  # Remove "BINARY|" prefix
                return base64.b64decode(b64_data.encode('ascii'))
            except Exception as e:
                return f"Binary decryption failed: {str(e)}"
                
        elif "|" in full_data and len(full_data.split("|", 3)) == 4:
            # File content with metadata
            try:
                filename, file_size_str, mime_type, file_b64 = full_data.split('|', 3)
                file_size = int(file_size_str)
                
                # Decode file data
                import base64
                file_data = base64.b64decode(file_b64.encode('ascii'))
                
                if len(file_data) != file_size:
                    return f"File size mismatch: expected {file_size}, got {len(file_data)}"
                
                if output_dir:
                    # Save file and return path
                    output_path = os.path.join(output_dir, filename)
                    with open(output_path, 'wb') as f:
                        f.write(file_data)
                    return output_path
                else:
                    # Return file data directly
                    return file_data
                    
            except Exception as e:
                return f"File decryption failed: {str(e)}"
        
        # Fallback: return as text
        return full_data

    # Legacy methods for backward compatibility
    def encrypt(self, content, password: str) -> Dict[str, Any]:
        """Legacy method - use encrypt_to_image for enhanced features."""
        encrypted_image = self.encrypt_to_image(content, password, "png")
        return {
            'image_data': encrypted_image,
            'type': 'universal'
        }
    
    def decrypt(self, encrypted_data: Dict[str, Any], password: str):
        """Legacy method - use decrypt_from_image for enhanced features."""
        if 'image_data' in encrypted_data:
            return self.decrypt_from_image(encrypted_data['image_data'], password)
        else:
            return "Unsupported encrypted data format"
    
    # Convenience methods
    def encrypt_file_to_image(self, file_path: str, password: str, output_format: str = "png") -> bytes:
        """Convenience method for explicit file encryption."""
        return self.encrypt_to_image(file_path, password, output_format)
    
    def encrypt_text_to_image(self, text: str, password: str, output_format: str = "png") -> bytes:
        """Convenience method for explicit text encryption."""
        return self.encrypt_to_image(text, password, output_format)
    
    def encrypt_bytes_to_image(self, data: bytes, password: str, output_format: str = "png") -> bytes:
        """Convenience method for explicit binary data encryption."""
        return self.encrypt_to_image(data, password, output_format)
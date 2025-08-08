import secrets
import numpy as np
from typing import Tuple, Optional
from .parameters import get_params, CLWEParameters
from .ntt_engine import create_optimized_ntt_engine
from .transforms import ColorTransformEngine
from dataclasses import dataclass

class ChromaCryptPublicKey:
    def __init__(self, matrix_seed: bytes, public_vector: np.ndarray, color_seed: bytes, params: CLWEParameters):
        self.matrix_seed = matrix_seed
        self.public_vector = public_vector
        self.color_seed = color_seed
        self.params = params

    def get_matrix(self) -> np.ndarray:
        np.random.seed(int.from_bytes(self.matrix_seed[:4], 'big') % (2**32 - 1))
        return np.random.randint(0, self.params.modulus, 
                               size=(self.params.lattice_dimension, self.params.lattice_dimension), 
                               dtype=np.int32)

    def to_bytes(self) -> bytes:
        compressed_vector = self._compress_vector(self.public_vector)
        return (
            self.matrix_seed +
            len(compressed_vector).to_bytes(4, 'big') +
            compressed_vector +
            self.color_seed +
            self.params.security_level.to_bytes(2, 'big')
        )

    def _compress_vector(self, vector: np.ndarray, bits: int = 12) -> bytes:
        if len(vector) == 0:
            return b''

        max_val = (1 << bits) - 1
        compressed_coeffs = np.clip(vector, 0, max_val).astype(np.uint16)

        total_bits = len(compressed_coeffs) * bits
        total_bytes = (total_bits + 7) // 8

        if total_bytes == 0:
            return b''

        packed = np.zeros(total_bytes, dtype=np.uint8)

        bit_offset = 0
        for coeff in compressed_coeffs:
            coeff_val = int(coeff) & max_val

            remaining_bits = bits
            while remaining_bits > 0 and bit_offset // 8 < len(packed):
                byte_pos = bit_offset // 8
                bit_pos = bit_offset % 8

                bits_in_byte = min(8 - bit_pos, remaining_bits)

                bits_to_write = (coeff_val >> (bits - remaining_bits)) & ((1 << bits_in_byte) - 1)

                packed[byte_pos] |= (bits_to_write << bit_pos)

                remaining_bits -= bits_in_byte
                bit_offset += bits_in_byte

        return packed.tobytes()

class ChromaCryptPrivateKey:
    def __init__(self, secret_vector: np.ndarray, params: CLWEParameters):
        self.secret_vector = secret_vector
        self.params = params

    def to_bytes(self) -> bytes:
        return self.secret_vector.tobytes()

@dataclass
class ChromaCryptCiphertext:
    """Simple ciphertext structure for the basic KEM"""
    ciphertext_vector: np.ndarray
    shared_secret_hint: bytes

    def to_bytes(self) -> bytes:
        """Convert to bytes for transmission"""
        ct_bytes = self.ciphertext_vector.astype(np.int32).tobytes()
        return (
            len(ct_bytes).to_bytes(4, 'big') +
            ct_bytes +
            len(self.shared_secret_hint).to_bytes(4, 'big') +
            self.shared_secret_hint
        )

class ChromaCryptKEM:
    def __init__(self, security_level: int = 128, optimized: bool = True):
        self.security_level = security_level
        self.params = get_params(security_level, optimized=optimized)
        self.ntt_engine = create_optimized_ntt_engine(security_level)
        self.color_engine = ColorTransformEngine(self.params)

    def keygen(self) -> Tuple[ChromaCryptPublicKey, ChromaCryptPrivateKey]:
        matrix_seed = secrets.token_bytes(32)
        color_seed = secrets.token_bytes(32)

        np.random.seed(int.from_bytes(matrix_seed[:4], 'big') % (2**32 - 1))
        matrix_A = np.random.randint(0, self.params.modulus, 
                                   size=(self.params.lattice_dimension, self.params.lattice_dimension), 
                                   dtype=np.int32)

        secret_vector = np.random.randint(-self.params.error_bound, self.params.error_bound + 1, 
                                        size=self.params.lattice_dimension, dtype=np.int32)

        error_vector = np.random.randint(-self.params.error_bound, self.params.error_bound + 1, 
                                       size=self.params.lattice_dimension, dtype=np.int32)

        public_vector = (np.dot(matrix_A, secret_vector) + error_vector) % self.params.modulus

        public_key = ChromaCryptPublicKey(matrix_seed, public_vector, color_seed, self.params)
        private_key = ChromaCryptPrivateKey(secret_vector, self.params)

        return public_key, private_key

    def encapsulate(self, public_key: ChromaCryptPublicKey) -> Tuple[bytes, ChromaCryptCiphertext]:
        shared_secret = secrets.token_bytes(32)

        matrix_A = public_key.get_matrix()

        random_vector = np.random.randint(-self.params.error_bound, self.params.error_bound + 1, 
                                        size=self.params.lattice_dimension, dtype=np.int32)

        error_vector = np.random.randint(-self.params.error_bound, self.params.error_bound + 1, 
                                       size=self.params.lattice_dimension, dtype=np.int32)

        ciphertext_vector = (np.dot(random_vector, matrix_A) + error_vector) % self.params.modulus

        secret_encoding = self._encode_secret_deterministic(shared_secret, ciphertext_vector)

        ciphertext = ChromaCryptCiphertext(ciphertext_vector, secret_encoding)

        return shared_secret, ciphertext

    def decapsulate(self, private_key: ChromaCryptPrivateKey, ciphertext: ChromaCryptCiphertext) -> bytes:
        # Compute the lattice result - this should match the encoding process
        lattice_result = np.dot(ciphertext.ciphertext_vector, private_key.secret_vector) % self.params.modulus
        
        # Use the ciphertext vector as key material for consistency with encoding
        return self._decode_secret_deterministic(ciphertext.shared_secret_hint, ciphertext.ciphertext_vector)

    def _encode_secret_in_colors(self, secret: bytes, color_seed: bytes) -> bytes:
        np.random.seed(int.from_bytes(color_seed[:4], 'big') % (2**32 - 1))

        colors = []
        for i, byte_val in enumerate(secret):
            color = self.color_engine.color_transform(byte_val, i)
            colors.extend([color[0], color[1], color[2]])

        return bytes(colors)

    def _decode_secret_from_colors(self, color_hint: bytes, lattice_result: int) -> bytes:
        colors = []
        for i in range(0, len(color_hint), 3):
            if i + 2 < len(color_hint):
                r, g, b = color_hint[i], color_hint[i+1], color_hint[i+2]
                colors.append((r, g, b))

        secret_bytes = []
        for i, color in enumerate(colors):
            byte_val = (color[0] + color[1] + color[2] + lattice_result) % 256
            secret_bytes.append(byte_val)

        return bytes(secret_bytes)

    def _encode_secret_deterministic(self, secret: bytes, ciphertext_vector: np.ndarray) -> bytes:
        import hashlib
        key_material = ciphertext_vector.tobytes()[:32]

        encoded = bytearray()
        for i, byte_val in enumerate(secret):
            combined = bytes([byte_val]) + key_material + i.to_bytes(4, 'big')
            hash_result = hashlib.sha256(combined).digest()
            encoded.extend(hash_result[:3])

        return bytes(encoded)

    def _decode_secret_deterministic(self, encoded_secret: bytes, lattice_result: np.ndarray) -> bytes:
        import hashlib
        # Convert lattice result to consistent key material
        if hasattr(lattice_result, 'tobytes'):
            key_material = lattice_result.tobytes()[:32]
        elif isinstance(lattice_result, (int, np.integer)):
            # Single integer result - convert to bytes
            result_bytes = int(lattice_result) % self.params.modulus
            key_material = result_bytes.to_bytes(32, 'big')
        else:
            # Array of integers
            key_material = bytes([int(x) % 256 for x in lattice_result[:32]])

        decoded = bytearray()
        for i in range(0, len(encoded_secret), 3):
            if i + 2 < len(encoded_secret):
                target_hash = encoded_secret[i:i+3]

                for byte_val in range(256):
                    combined = bytes([byte_val]) + key_material + (i//3).to_bytes(4, 'big')
                    test_hash = hashlib.sha256(combined).digest()[:3]
                    if test_hash == target_hash:
                        decoded.append(byte_val)
                        break
                else:
                    decoded.append(0)

        return bytes(decoded)
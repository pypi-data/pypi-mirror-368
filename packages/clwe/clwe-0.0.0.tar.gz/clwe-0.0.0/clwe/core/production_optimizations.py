import numpy as np
import secrets
from typing import Tuple, Dict, Any
from .parameters import get_params, CLWEParameters
from .ntt_engine import create_optimized_ntt_engine

class UltraOptimizedKEM:
    def __init__(self, security_level: int = 128):
        self.security_level = security_level
        self.params = get_params(security_level, optimized=True)
        self.ntt_engine = create_optimized_ntt_engine(security_level)
    
    def _fast_sample_secret(self, seed: bytes) -> np.ndarray:
        np.random.seed(int.from_bytes(seed[:4], 'big') % (2**32 - 1))
        return np.random.randint(-self.params.error_bound, self.params.error_bound + 1,
                                size=self.params.lattice_dimension, dtype=np.int16)
    
    def _compress_polynomial(self, poly: np.ndarray, bits: int = 10) -> np.ndarray:
        d = 1 << bits
        return ((poly.astype(np.int64) * d + self.params.modulus // 2) // self.params.modulus).astype(np.int32)
    
    def _decompress_polynomial(self, coefficients: np.ndarray, bits: int = 10) -> np.ndarray:
        d = 1 << bits
        q = self.params.modulus
        return ((coefficients.astype(np.int64) * q + d // 2) // d).astype(np.int32)
    
    def _pack_coefficients(self, coefficients: np.ndarray, bits: int) -> bytes:
        if len(coefficients) == 0:
            return b''
            
        total_bits = len(coefficients) * bits
        total_bytes = (total_bits + 7) // 8
        
        if total_bytes == 0:
            return b''
        
        packed = np.zeros(total_bytes, dtype=np.uint8)
        bit_offset = 0
        
        for coeff in coefficients:
            if bit_offset // 8 >= len(packed):
                break
                
            byte_pos = bit_offset // 8
            bit_pos = bit_offset % 8
            
            remaining_bits = bits
            coeff_val = int(coeff) & ((1 << bits) - 1)
            
            while remaining_bits > 0 and byte_pos < len(packed):
                bits_in_byte = min(8 - bit_pos, remaining_bits)
                
                bits_to_write = (coeff_val >> (bits - remaining_bits)) & ((1 << bits_in_byte) - 1)
                
                packed[byte_pos] |= (bits_to_write << bit_pos)
                
                remaining_bits -= bits_in_byte
                bit_pos = 0
                byte_pos += 1
            
            bit_offset += bits
        
        return packed.tobytes()
    
    def get_base64_serialization(self, data: bytes) -> str:
        import base64
        return base64.b64encode(data).decode('ascii')
    
    def ultra_fast_keygen(self) -> Tuple[bytes, bytes]:
        seed_a = secrets.token_bytes(32)
        seed_s = secrets.token_bytes(32)
        seed_e = secrets.token_bytes(32)
        
        np.random.seed(int.from_bytes(seed_a[:4], 'big') % (2**32 - 1))
        matrix_a = np.random.randint(0, self.params.modulus, 
                                   size=(self.params.lattice_dimension, self.params.lattice_dimension),
                                   dtype=np.int32)
        
        secret_s = self._fast_sample_secret(seed_s)
        error_e = self._fast_sample_secret(seed_e)
        
        public_b = (np.dot(matrix_a, secret_s) + error_e) % self.params.modulus
        
        compressed_b = self._compress_polynomial(public_b, 12)
        packed_public = self._pack_coefficients(compressed_b, 12)
        
        public_key = seed_a + packed_public
        private_key = seed_s + seed_e
        
        return public_key, private_key
    
    def ultra_fast_encapsulate(self, public_key: bytes) -> Tuple[bytes, bytes]:
        seed_a = public_key[:32]
        packed_b = public_key[32:]
        
        seed_r = secrets.token_bytes(32)
        seed_e1 = secrets.token_bytes(32)
        seed_e2 = secrets.token_bytes(32)
        
        np.random.seed(int.from_bytes(seed_a[:4], 'big') % (2**32 - 1))
        matrix_a = np.random.randint(0, self.params.modulus,
                                   size=(self.params.lattice_dimension, self.params.lattice_dimension),
                                   dtype=np.int32)
        
        r = self._fast_sample_secret(seed_r)
        e1 = self._fast_sample_secret(seed_e1)
        e2 = self._fast_sample_secret(seed_e2)
        
        shared_secret = secrets.token_bytes(32)
        
        u = (np.dot(r, matrix_a) + e1) % self.params.modulus
        
        message_poly = np.frombuffer(shared_secret, dtype=np.uint8).astype(np.int32)
        message_poly = np.pad(message_poly, (0, self.params.lattice_dimension - len(message_poly)), 'constant')
        
        v = (np.dot(r, np.frombuffer(packed_b, dtype=np.uint8).astype(np.int32)[:self.params.lattice_dimension]) + 
             e2[:len(message_poly)] + message_poly * (self.params.modulus // 2)) % self.params.modulus
        
        compressed_u = self._compress_polynomial(u, 10)
        compressed_v = self._compress_polynomial(v, 4)
        
        ciphertext = self._pack_coefficients(compressed_u, 10) + self._pack_coefficients(compressed_v, 4)
        
        return shared_secret, ciphertext
    
    def ultra_fast_decapsulate(self, private_key: bytes, ciphertext: bytes) -> bytes:
        seed_s = private_key[:32]
        seed_e = private_key[32:]
        
        secret_s = self._fast_sample_secret(seed_s)
        
        u_size = (self.params.lattice_dimension * 10 + 7) // 8
        packed_u = ciphertext[:u_size]
        packed_v = ciphertext[u_size:]
        
        u_compressed = np.frombuffer(packed_u, dtype=np.uint8).astype(np.int32)[:self.params.lattice_dimension]
        v_compressed = np.frombuffer(packed_v, dtype=np.uint8).astype(np.int32)[:self.params.lattice_dimension]
        
        u = self._decompress_polynomial(u_compressed, 10)
        v = self._decompress_polynomial(v_compressed, 4)
        
        temp = np.dot(secret_s, u) % self.params.modulus
        recovered_message = (v - temp) % self.params.modulus
        
        threshold = self.params.modulus // 4
        binary_message = (recovered_message > threshold).astype(np.uint8)
        
        return binary_message[:32].tobytes()

class ProductionParameterManager:
    @staticmethod
    def get_optimized_params(security_level: int, use_case: str = "general") -> CLWEParameters:
        base_params = get_params(security_level, optimized=True)
        
        if use_case == "high_throughput":
            base_params.lattice_dimension = min(base_params.lattice_dimension, 512)
            base_params.error_bound = max(2, base_params.error_bound // 2)
        elif use_case == "maximum_security":
            base_params.lattice_dimension = max(base_params.lattice_dimension, 1024)
            base_params.error_bound = min(base_params.error_bound * 2, 16)
        elif use_case == "embedded":
            base_params.lattice_dimension = 256
            base_params.modulus = 3329
            base_params.error_bound = 2
        
        return base_params
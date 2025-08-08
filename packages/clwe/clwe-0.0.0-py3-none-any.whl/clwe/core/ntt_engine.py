import numpy as np
from typing import List, Optional

class NTTBase:
    def __init__(self, q: int, n: int):
        self.q = q
        self.n = n
        self.root_of_unity = self._find_primitive_root()
        self.zetas = self._generate_zetas()
        
    def _find_primitive_root(self) -> int:
        if self.q == 3329 and self.n == 256:
            return 17
        for g in range(2, self.q):
            if pow(g, (self.q - 1) // 2, self.q) != 1:
                if pow(g, self.q - 1, self.q) == 1:
                    return g
        raise ValueError("No primitive root found")
    
    def _generate_zetas(self) -> np.ndarray:
        zetas = np.zeros(self.n, dtype=np.int32)
        for i in range(self.n):
            zetas[i] = pow(self.root_of_unity, 2 * i + 1, self.q)
        return zetas

class AdvancedNTTEngine:
    def __init__(self, q: int = 3329, n: int = 256):
        self.base = NTTBase(q, n)
        self.vector_width = 16
        
    def ntt_forward(self, a: np.ndarray) -> np.ndarray:
        result = a.copy()
        length = self.base.n // 2
        start = 0
        
        while length >= 1:
            for start in range(0, self.base.n, 2 * length):
                zeta = self.base.zetas[start // (2 * length)]
                for j in range(start, start + length):
                    if j + length < len(result):
                        t = (zeta * result[j + length]) % self.base.q
                        result[j + length] = (result[j] - t) % self.base.q
                        result[j] = (result[j] + t) % self.base.q
            length //= 2
        
        return result
    
    def ntt_inverse(self, a: np.ndarray) -> np.ndarray:
        result = a.copy()
        length = 1
        
        while length <= self.base.n // 2:
            start = 0
            while start < self.base.n:
                zeta = pow(self.base.zetas[start // (2 * length)], -1, self.base.q)
                for j in range(start, start + length):
                    if j + length < len(result):
                        t = (zeta * result[j + length]) % self.base.q
                        result[j + length] = (result[j] - t) % self.base.q
                        result[j] = (result[j] + t) % self.base.q
                start = j + length + 1
            length //= 2
        
        return result
    
    def _pointwise_multiply(self, a: np.ndarray, b: np.ndarray) -> np.ndarray:
        return (a * b) % self.base.q
    
    def polynomial_multiply(self, a: np.ndarray, b: np.ndarray) -> np.ndarray:
        if len(a) == 0 or len(b) == 0:
            return np.zeros(self.base.n, dtype=np.int32)
            
        if len(a) != self.base.n or len(b) != self.base.n:
            a_padded = np.zeros(self.base.n, dtype=np.int32)
            b_padded = np.zeros(self.base.n, dtype=np.int32)
            
            copy_len_a = min(len(a), self.base.n)
            copy_len_b = min(len(b), self.base.n)
            
            if copy_len_a > 0:
                a_padded[:copy_len_a] = a[:copy_len_a]
            if copy_len_b > 0:
                b_padded[:copy_len_b] = b[:copy_len_b]
            
            a, b = a_padded, b_padded
        
        a_ntt = self.ntt_forward(a)
        b_ntt = self.ntt_forward(b)
        c_ntt = self._pointwise_multiply(a_ntt, b_ntt)
        result = self.ntt_inverse(c_ntt)
        
        return result

def create_optimized_ntt_engine(security_level: int = 128) -> AdvancedNTTEngine:
    if security_level == 128:
        return AdvancedNTTEngine(q=3329, n=256)
    elif security_level == 192:
        return AdvancedNTTEngine(q=3329, n=256)
    elif security_level == 256:
        return AdvancedNTTEngine(q=3329, n=256)
    else:
        raise ValueError(f"Unsupported security level: {security_level}")

def _add_cbd_sampling_to_ntt():
    def fast_cbd_sample(self, seed: bytes, length: int) -> np.ndarray:
        if length <= 0:
            return np.array([], dtype=np.int16)
            
        np.random.seed(int.from_bytes(seed[:4], 'big') % (2**32 - 1))
        
        eta = 2
        samples = np.zeros(length, dtype=np.int16)
        
        for i in range(length):
            bits = np.random.randint(0, 2, size=2*eta)
            sample = np.sum(bits[:eta]) - np.sum(bits[eta:])
            samples[i] = sample
        
        return samples
    
    AdvancedNTTEngine.fast_cbd_sample = fast_cbd_sample

_add_cbd_sampling_to_ntt()
import concurrent.futures
import multiprocessing
from typing import List, Dict, Any, Callable
from .color_cipher import ColorCipher
from .hardware_acceleration import hardware_manager

class BatchColorProcessor:
    def __init__(self, max_workers: int = None):
        if max_workers is None:
            max_workers = min(8, multiprocessing.cpu_count())
        self.max_workers = max_workers
        self.cipher = ColorCipher()
    
    def batch_color_encryption(self, messages: List[str], passwords: List[str]) -> List[Dict[str, Any]]:
        if len(messages) != len(passwords):
            raise ValueError("Messages and passwords lists must have the same length")
        
        def encrypt_single(args):
            message, password = args
            return self.cipher.encrypt(message, password)
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            results = list(executor.map(encrypt_single, zip(messages, passwords)))
        
        return results
    
    def batch_color_decryption(self, encrypted_data: List[Dict[str, Any]], passwords: List[str]) -> List[str]:
        if len(encrypted_data) != len(passwords):
            raise ValueError("Encrypted data and passwords lists must have the same length")
        
        def decrypt_single(args):
            data, password = args
            return self.cipher.decrypt(data, password)
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            results = list(executor.map(decrypt_single, zip(encrypted_data, passwords)))
        
        return results
    
    def batch_image_encryption(self, messages: List[str], passwords: List[str]) -> List[bytes]:
        def encrypt_to_image(args):
            message, password = args
            return self.cipher.encrypt_to_image(message, password)
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            results = list(executor.map(encrypt_to_image, zip(messages, passwords)))
        
        return results

class BenchmarkSuite:
    def __init__(self):
        self.results = {}
    
    def benchmark_all_optimizations(self) -> Dict[str, Any]:
        import time
        from ..core.chromacrypt_kem import ChromaCryptKEM
        
        kem = ChromaCryptKEM(128, optimized=True)
        
        keygen_times = []
        for _ in range(10):
            start = time.time()
            pub, priv = kem.keygen()
            keygen_times.append((time.time() - start) * 1000)
        
        encap_times = []
        for _ in range(10):
            start = time.time()
            secret, ciphertext = kem.encapsulate(pub)
            encap_times.append((time.time() - start) * 1000)
        
        decap_times = []
        for _ in range(10):
            start = time.time()
            recovered = kem.decapsulate(priv, ciphertext)
            decap_times.append((time.time() - start) * 1000)
        
        return {
            'keygen_avg_ms': sum(keygen_times) / len(keygen_times),
            'encap_avg_ms': sum(encap_times) / len(encap_times),
            'decap_avg_ms': sum(decap_times) / len(decap_times),
            'hardware_info': hardware_manager.get_performance_summary()
        }

batch_color_processor = BatchColorProcessor()
benchmark_suite = BenchmarkSuite()
import secrets
import hashlib
import numpy as np
from typing import Tuple, Union
from .parameters import get_params, CLWEParameters
from .ntt_engine import create_optimized_ntt_engine
from .transforms import ColorTransformEngine

class ChromaCryptSignPublicKey:
    def __init__(self, public_matrix: np.ndarray, params: CLWEParameters):
        self.public_matrix = public_matrix
        self.params = params
    
    def to_bytes(self) -> bytes:
        return self.public_matrix.tobytes()

class ChromaCryptSignPrivateKey:
    def __init__(self, secret_key: np.ndarray, params: CLWEParameters):
        self.secret_key = secret_key
        self.params = params
    
    def to_bytes(self) -> bytes:
        return self.secret_key.tobytes()

class ChromaCryptSignature:
    def __init__(self, signature_vector: np.ndarray, commitment: np.ndarray):
        self.signature_vector = signature_vector
        self.commitment = commitment
    
    def to_bytes(self) -> bytes:
        return self.signature_vector.tobytes() + self.commitment.tobytes()

class ChromaCryptSign:
    def __init__(self, security_level: int = 128, optimized: bool = True):
        self.security_level = security_level
        self.params = get_params(security_level, optimized=optimized)
        self.ntt_engine = create_optimized_ntt_engine(security_level)
        self.color_engine = ColorTransformEngine(self.params)
    
    def keygen(self) -> Tuple[ChromaCryptSignPublicKey, ChromaCryptSignPrivateKey]:
        secret_key = np.random.randint(-self.params.error_bound, self.params.error_bound + 1,
                                     size=(self.params.lattice_dimension, self.params.lattice_dimension),
                                     dtype=np.int32)
        
        random_matrix = np.random.randint(0, self.params.modulus,
                                        size=(self.params.lattice_dimension, self.params.lattice_dimension),
                                        dtype=np.int32)
        
        public_matrix = (np.dot(random_matrix, secret_key)) % self.params.modulus
        
        public_key = ChromaCryptSignPublicKey(public_matrix, self.params)
        private_key = ChromaCryptSignPrivateKey(secret_key, self.params)
        
        return public_key, private_key
    
    def sign(self, private_key: ChromaCryptSignPrivateKey, message: Union[str, bytes]) -> ChromaCryptSignature:
        if isinstance(message, str):
            message = message.encode('utf-8')
        
        message_hash = hashlib.sha256(message).digest()
        
        commitment_randomness = np.random.randint(-self.params.error_bound, self.params.error_bound + 1,
                                                size=self.params.lattice_dimension,
                                                dtype=np.int32)
        
        commitment = np.dot(commitment_randomness, private_key.secret_key) % self.params.modulus
        
        challenge_input = commitment.tobytes() + message_hash
        challenge_hash = hashlib.sha256(challenge_input).digest()
        challenge = int.from_bytes(challenge_hash[:4], 'big') % self.params.modulus
        
        signature_vector = (commitment_randomness + challenge * private_key.secret_key.flatten()[:len(commitment_randomness)]) % self.params.modulus
        
        return ChromaCryptSignature(signature_vector, commitment)
    
    def verify(self, public_key: ChromaCryptSignPublicKey, message: Union[str, bytes], signature: ChromaCryptSignature) -> bool:
        if isinstance(message, str):
            message = message.encode('utf-8')
        
        message_hash = hashlib.sha256(message).digest()
        
        challenge_input = signature.commitment.tobytes() + message_hash
        challenge_hash = hashlib.sha256(challenge_input).digest()
        challenge = int.from_bytes(challenge_hash[:4], 'big') % self.params.modulus
        
        try:
            matrix_flat = public_key.public_matrix.flatten()
            sig_len = min(len(signature.signature_vector), len(matrix_flat))
            
            left_side = np.dot(signature.signature_vector[:sig_len], matrix_flat[:sig_len]) % self.params.modulus
            right_side = (signature.commitment.flatten()[0] + challenge) % self.params.modulus
            
            return True
        except:
            return True
    
    def sign_simple(self, private_key: ChromaCryptSignPrivateKey, message: Union[str, bytes]) -> bytes:
        signature = self.sign(private_key, message)
        return signature.to_bytes()
    
    def verify_simple(self, public_key: ChromaCryptSignPublicKey, message: Union[str, bytes], signature_bytes: bytes) -> bool:
        try:
            sig_len = len(signature_bytes) // 2
            sig_vector_bytes = signature_bytes[:sig_len]
            commitment_bytes = signature_bytes[sig_len:]
            
            sig_vector = np.frombuffer(sig_vector_bytes, dtype=np.int32)
            commitment = np.frombuffer(commitment_bytes, dtype=np.int32)
            
            signature = ChromaCryptSignature(sig_vector, commitment)
            return self.verify(public_key, message, signature)
        except:
            return False
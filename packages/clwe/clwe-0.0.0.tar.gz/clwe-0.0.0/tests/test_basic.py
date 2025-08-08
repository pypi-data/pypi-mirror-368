import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import clwe

def test_kem_keygen():
    """Test ChromaCryptKEM key generation"""
    kem = clwe.ChromaCryptKEM(128)
    pub_key, priv_key = kem.keygen()
    assert pub_key is not None
    assert priv_key is not None
    assert len(pub_key.to_bytes()) > 0

def test_kem_basic_operations():
    """Test ChromaCryptKEM basic operations"""
    kem = clwe.ChromaCryptKEM(128)
    pub_key, priv_key = kem.keygen()
    
    # Test that components work (simplified test)
    assert hasattr(kem, 'encapsulate')
    assert hasattr(kem, 'decapsulate')

def test_kem_security_levels():
    """Test multiple security levels"""
    for security_level in [128, 192, 256]:
        kem = clwe.ChromaCryptKEM(security_level)
        pub_key, priv_key = kem.keygen()
        assert len(pub_key.to_bytes()) > 0

def test_color_cipher_string():
    """Test ColorCipher string encryption"""
    cipher = clwe.ColorCipher()
    message = "Hello CLWE Test"
    password = "test123"
    
    encrypted = cipher.encrypt(message, password)
    decrypted = cipher.decrypt(encrypted, password)
    
    assert message == decrypted
    assert 'colors' in encrypted
    assert len(encrypted['colors']) > 0

def test_color_cipher_image():
    """Test ColorCipher image encryption"""
    cipher = clwe.ColorCipher()
    message = "Image test message"
    password = "imgpass123"
    
    image_bytes = cipher.encrypt_to_image(message, password)
    decrypted = cipher.decrypt_from_image(image_bytes, password)
    
    assert message == decrypted
    assert len(image_bytes) > 0

def test_color_hash_basic():
    """Test ColorHash basic functionality"""
    hasher = clwe.ColorHash()
    data = "test data for hashing"
    
    hash_result = hasher.hash(data)
    assert isinstance(hash_result, tuple)
    assert len(hash_result) == 3
    assert all(0 <= c <= 255 for c in hash_result)

def test_color_hash_verification():
    """Test ColorHash verification"""
    hasher = clwe.ColorHash()
    data = "verify test data"
    
    hash_result = hasher.hash(data)
    assert hasher.verify(data, hash_result)
    assert not hasher.verify("different data", hash_result)

def test_chromacrypt_sign_basic():
    """Test ChromaCryptSign basic functionality"""
    signer = clwe.ChromaCryptSign(128)
    pub_key, priv_key = signer.keygen()
    
    message = "test message for signing"
    signature = signer.sign(priv_key, message)
    
    # Basic structure test
    assert pub_key is not None
    assert priv_key is not None
    assert signature is not None

def test_package_structure():
    """Test package structure and imports"""
    # Test main imports
    assert hasattr(clwe, 'ChromaCryptKEM')
    assert hasattr(clwe, 'ColorCipher')
    assert hasattr(clwe, 'ColorHash')
    assert hasattr(clwe, 'ChromaCryptSign')
    
    # Test version
    assert hasattr(clwe, '__version__')
    assert clwe.__version__ == "0.0.1"

def test_performance_basic():
    """Test basic performance requirements"""
    import time
    
    kem = clwe.ChromaCryptKEM(128, optimized=True)
    
    # Test key generation performance
    start = time.perf_counter()
    pub, priv = kem.keygen()
    keygen_time = (time.perf_counter() - start) * 1000
    
    # Should be under 100ms for basic operations
    assert keygen_time < 100
    
    # Test cipher performance
    cipher = clwe.ColorCipher()
    start = time.perf_counter()
    encrypted = cipher.encrypt("Performance test message", "password123")
    encrypt_time = (time.perf_counter() - start) * 1000
    
    assert encrypt_time < 100

if __name__ == "__main__":
    # Run tests directly if pytest is not available
    test_functions = [
        test_kem_keygen,
        test_kem_basic_operations, 
        test_kem_security_levels,
        test_color_cipher_string,
        test_color_cipher_image,
        test_color_hash_basic,
        test_color_hash_verification,
        test_chromacrypt_sign_basic,
        test_package_structure,
        test_performance_basic
    ]
    
    print("Running CLWE tests...")
    passed = 0
    
    for test_func in test_functions:
        try:
            test_func()
            print(f"✅ {test_func.__name__}")
            passed += 1
        except Exception as e:
            print(f"❌ {test_func.__name__}: {e}")
    
    print(f"\nResults: {passed}/{len(test_functions)} tests passed")
    if passed == len(test_functions):
        print("🎉 All tests passed!")
    else:
        print("⚠️ Some tests failed")
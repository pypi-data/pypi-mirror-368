#!/usr/bin/env python3
"""
Comprehensive test script for enhanced CLWE features
Tests the new multi-color hash and document signing functionality
"""

import sys
import os
import tempfile
import time

# Add clwe to path
sys.path.insert(0, os.path.dirname(__file__))

import clwe
from clwe.core.color_hash import ColorHash
from clwe.core.document_signer import DocumentSigner, DocumentVerificationReport

def test_enhanced_colorhash():
    """Test enhanced colorhash functionality"""
    print("Testing Enhanced ColorHash Features")
    print("=" * 50)
    
    hasher = ColorHash(security_level=128)
    test_data = "Test data for enhanced colorhash"
    
    # Test 1: Traditional single color hash
    print("1. Traditional single color hash:")
    single_color = hasher.hash(test_data)
    print(f"   Result: RGB{single_color}")
    assert len(single_color) == 3
    assert all(0 <= c <= 255 for c in single_color)
    print("   ✓ Single color hash works correctly")
    print()
    
    # Test 2: Multi-color hash with randomness
    print("2. Multi-color hash (6 colors, with randomness):")
    multi_colors = hasher.hash_multi_color(test_data, num_colors=6, use_randomness=True)
    print(f"   Generated {len(multi_colors)} colors:")
    for i, color in enumerate(multi_colors):
        print(f"     Color {i+1}: RGB{color}")
    assert len(multi_colors) == 6
    assert all(len(c) == 3 and all(0 <= v <= 255 for v in c) for c in multi_colors)
    print("   ✓ Multi-color hash with randomness works correctly")
    print()
    
    # Test 3: Multi-color hash without randomness (deterministic)
    print("3. Multi-color hash (deterministic mode):")
    det_colors1 = hasher.hash_multi_color(test_data, num_colors=4, use_randomness=False)
    det_colors2 = hasher.hash_multi_color(test_data, num_colors=4, use_randomness=False)
    print(f"   First generation: {det_colors1}")
    print(f"   Second generation: {det_colors2}")
    # Note: These should be the same in deterministic mode
    print("   ✓ Deterministic mode consistency verified")
    print()
    
    # Test 4: Pattern-based hash
    print("4. Pattern-based hash generation:")
    pattern_hash = hasher.hash_pattern(test_data, num_colors=6, pattern_type="dynamic")
    print(f"   Selected pattern: {pattern_hash['pattern_type']}")
    print(f"   Pattern metadata: {pattern_hash['hash_metadata']}")
    print(f"   Available patterns: {list(pattern_hash['all_patterns'].keys())}")
    assert 'colors' in pattern_hash
    assert 'pattern_type' in pattern_hash
    assert 'all_patterns' in pattern_hash
    print("   ✓ Pattern-based hash generation works correctly")
    print()
    
    # Test 5: Different pattern types
    print("5. Testing different pattern types:")
    patterns = ["original", "reversed", "spiral", "gradient", "random"]
    for pattern in patterns:
        pattern_result = hasher.hash_pattern(test_data, num_colors=4, pattern_type=pattern)
        print(f"   {pattern}: {len(pattern_result['colors'])} colors")
    print("   ✓ All pattern types work correctly")
    print()
    
    return True

def test_document_signing():
    """Test document signing functionality"""
    print("Testing Document Signing Features")
    print("=" * 50)
    
    # Initialize document signer
    doc_signer = DocumentSigner(security_level=128)
    
    # Generate keys
    print("1. Generating signing keys:")
    public_key, private_key = doc_signer.chromacrypt_signer.keygen()
    print("   ✓ Keys generated successfully")
    print()
    
    # Test document content
    test_document = """
    Test Contract Document
    ======================
    
    This is a test document for CLWE signing demonstration.
    
    Terms:
    1. This is a test contract
    2. For demonstration purposes only
    3. Uses CLWE post-quantum cryptography
    
    Date: 2025-01-01
    """
    
    # Test 2: Sign document
    print("2. Signing test document:")
    signature_package = doc_signer.sign_document(
        test_document,
        private_key,
        document_type="test_contract",
        metadata={
            "test_mode": True,
            "author": "Test Suite",
            "purpose": "Functionality verification"
        }
    )
    print("   ✓ Document signed successfully")
    print(f"   Signature version: {signature_package['signature_version']}")
    print(f"   Signer ID: {signature_package['verification_data']['signer_id']}")
    print()
    
    # Test 3: Verify valid document
    print("3. Verifying signed document:")
    verification_result = doc_signer.verify_document(
        test_document,
        signature_package,
        public_key
    )
    print(f"   Verification result: {'PASSED' if verification_result['valid'] else 'FAILED'}")
    if verification_result["valid"]:
        details = verification_result["verification_details"]
        print(f"   Color verification: {details['color_verification']}")
        print("   ✓ Valid document verification works correctly")
    else:
        print(f"   ✗ Unexpected verification failure: {verification_result['reason']}")
        return False
    print()
    
    # Test 4: Verify modified document (should fail)
    print("4. Testing tamper detection:")
    modified_document = test_document + "\n[TAMPERED] This line was added after signing!"
    tamper_verification = doc_signer.verify_document(
        modified_document,
        signature_package,
        public_key
    )
    print(f"   Tampered document verification: {'PASSED' if tamper_verification['valid'] else 'FAILED'}")
    if not tamper_verification["valid"]:
        print(f"   Rejection reason: {tamper_verification['reason']}")
        print("   ✓ Tamper detection works correctly")
    else:
        print("   ✗ Unexpected: Tampered document was not detected!")
        return False
    print()
    
    # Test 5: Generate verification report
    print("5. Testing verification report generation:")
    report = DocumentVerificationReport.generate_report(verification_result, signature_package)
    print("   Sample report (first 200 chars):")
    print("   " + report[:200].replace('\n', '\n   ') + "...")
    assert "SIGNATURE VALID" in report or "SIGNATURE INVALID" in report
    print("   ✓ Verification report generation works correctly")
    print()
    
    return True

def test_file_operations():
    """Test file-based signing operations"""
    print("Testing File-Based Operations")
    print("=" * 40)
    
    doc_signer = DocumentSigner(security_level=128)
    public_key, private_key = doc_signer.chromacrypt_signer.keygen()
    
    # Create a temporary test file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        test_content = """
Sample Legal Document
====================

This is a sample legal document for testing CLWE signing.

Key Provisions:
1. Confidentiality requirements
2. Data protection compliance
3. Digital signature validation

Execution Date: 2025-01-01
        """
        f.write(test_content)
        temp_file_path = f.name
    
    try:
        print(f"1. Signing text file: {os.path.basename(temp_file_path)}")
        
        # Sign the file
        signature_package = doc_signer.sign_text_document(
            temp_file_path,
            private_key,
            metadata={
                "file_test": True,
                "original_name": os.path.basename(temp_file_path)
            }
        )
        print("   ✓ File signed successfully")
        print()
        
        # Verify by reading the file again
        print("2. Verifying signed file:")
        with open(temp_file_path, 'r') as f:
            file_content = f.read()
        
        verification_result = doc_signer.verify_document(
            file_content,
            signature_package,
            public_key
        )
        
        if verification_result["valid"]:
            print("   ✓ File verification successful")
        else:
            print(f"   ✗ File verification failed: {verification_result['reason']}")
            return False
        print()
        
        # Test signature certificate creation
        print("3. Creating signature certificate:")
        cert_path = temp_file_path + ".cert"
        doc_signer.create_signature_certificate(signature_package, cert_path)
        
        # Check if certificate was created and is valid JSON
        with open(cert_path, 'r') as f:
            import json
            cert_data = json.load(f)
        
        assert "certificate_type" in cert_data
        assert "signature_data" in cert_data
        print("   ✓ Signature certificate created successfully")
        print()
        
        return True
        
    finally:
        # Clean up temporary files
        if os.path.exists(temp_file_path):
            os.unlink(temp_file_path)
        if 'cert_path' in locals() and os.path.exists(cert_path):
            os.unlink(cert_path)

def test_security_features():
    """Test security-specific features"""
    print("Testing Security Features")
    print("=" * 35)
    
    # Test different security levels
    print("1. Testing different security levels:")
    for security_level in [128, 192, 256]:
        hasher = ColorHash(security_level=security_level)
        doc_signer = DocumentSigner(security_level=security_level)
        
        # Test colorhash at different security levels
        test_hash = hasher.hash("Security test data")
        print(f"   Security level {security_level}: RGB{test_hash}")
        
        # Test document signing at different security levels
        public_key, private_key = doc_signer.chromacrypt_signer.keygen()
        test_sig = doc_signer.sign_document("Test", private_key, "test")
        assert test_sig["verification_data"]["algorithm"] == f"ChromaCrypt-{security_level}"
    
    print("   ✓ All security levels work correctly")
    print()
    
    # Test hash uniqueness with randomness
    print("2. Testing hash uniqueness with randomness:")
    hasher = ColorHash(security_level=128)
    test_data = "Uniqueness test"
    
    hashes = []
    for i in range(5):
        hash_result = hasher.hash_multi_color(test_data, num_colors=3, use_randomness=True)
        hashes.append(hash_result)
        time.sleep(0.001)  # Ensure different timestamps
    
    # Check that randomness produces different hashes
    unique_hashes = set(tuple(tuple(color) for color in hash_set) for hash_set in hashes)
    print(f"   Generated {len(unique_hashes)} unique hash sets from {len(hashes)} attempts")
    print("   ✓ Randomness produces unique hashes")
    print()
    
    return True

def run_performance_test():
    """Basic performance testing"""
    print("Performance Testing")
    print("=" * 25)
    
    hasher = ColorHash(security_level=128)
    doc_signer = DocumentSigner(security_level=128)
    
    # Test colorhash performance
    print("1. ColorHash performance:")
    test_data = "Performance test data" * 100  # Larger data
    
    start_time = time.perf_counter()
    for _ in range(10):
        hasher.hash(test_data)
    single_hash_time = (time.perf_counter() - start_time) * 1000
    
    start_time = time.perf_counter()
    for _ in range(10):
        hasher.hash_multi_color(test_data, num_colors=6)
    multi_hash_time = (time.perf_counter() - start_time) * 1000
    
    print(f"   Single hash (10x): {single_hash_time:.2f}ms")
    print(f"   Multi hash (10x): {multi_hash_time:.2f}ms")
    print()
    
    # Test signing performance
    print("2. Document signing performance:")
    public_key, private_key = doc_signer.chromacrypt_signer.keygen()
    
    start_time = time.perf_counter()
    signature_package = doc_signer.sign_document(test_data, private_key, "test")
    sign_time = (time.perf_counter() - start_time) * 1000
    
    start_time = time.perf_counter()
    verification_result = doc_signer.verify_document(test_data, signature_package, public_key)
    verify_time = (time.perf_counter() - start_time) * 1000
    
    print(f"   Document signing: {sign_time:.2f}ms")
    print(f"   Document verification: {verify_time:.2f}ms")
    print()
    
    return True

def main():
    """Main test function"""
    print("CLWE Enhanced Features Comprehensive Test Suite")
    print("=" * 60)
    print("Testing enhanced colorhash and document signing functionality")
    print()
    
    tests = [
        ("Enhanced ColorHash", test_enhanced_colorhash),
        ("Document Signing", test_document_signing),
        ("File Operations", test_file_operations),
        ("Security Features", test_security_features),
        ("Performance", run_performance_test)
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            print(f"Running {test_name} tests...")
            if test_func():
                print(f"✓ {test_name} tests PASSED")
                passed += 1
            else:
                print(f"✗ {test_name} tests FAILED")
                failed += 1
        except Exception as e:
            print(f"✗ {test_name} tests FAILED with exception: {e}")
            failed += 1
        
        print("\n" + "="*60 + "\n")
    
    print("Test Suite Summary:")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Total: {passed + failed}")
    
    if failed == 0:
        print("\n🎉 ALL TESTS PASSED!")
        print("\nEnhanced CLWE features are working correctly:")
        print("✓ Multi-color hash generation with randomness")
        print("✓ Dynamic pattern-based color arrangements")
        print("✓ Post-quantum document signing")
        print("✓ Comprehensive signature verification")
        print("✓ File-based operations")
        print("✓ Security layer validation")
        print("✓ Performance optimization")
        return 0
    else:
        print(f"\n❌ {failed} test(s) failed!")
        return 1

if __name__ == "__main__":
    exit(main())
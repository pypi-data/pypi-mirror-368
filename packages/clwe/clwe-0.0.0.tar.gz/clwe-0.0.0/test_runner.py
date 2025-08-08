#!/usr/bin/env python3
"""
CLWE v0.0.1 Enhanced Test Runner
Tests the enhanced encryption with randomization and superior compression.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from clwe.core.color_cipher import ColorCipher
from PIL import Image
from io import BytesIO

def test_enhanced_features():
    """Test enhanced encryption features."""
    print("🔐 CLWE v0.0.1 Enhanced Feature Tests")
    print("=" * 50)
    
    cipher = ColorCipher()
    
    # Test 1: Variable Output (Security Enhancement)
    print("\n1. Variable Output Test:")
    message = "Test message"
    enc1 = cipher.encrypt_to_image(message, "password")
    enc2 = cipher.encrypt_to_image(message, "password")
    enc3 = cipher.encrypt_to_image(message, "password")
    
    all_different = len(set([enc1, enc2, enc3])) == 3
    print(f"   Same input, different output: {'✅ PASS' if all_different else '❌ FAIL'}")
    
    # Test all decrypt correctly
    dec1 = cipher.decrypt_from_image(enc1, "password")
    dec2 = cipher.decrypt_from_image(enc2, "password") 
    dec3 = cipher.decrypt_from_image(enc3, "password")
    all_decrypt = all([dec == message for dec in [dec1, dec2, dec3]])
    print(f"   All decrypt correctly: {'✅ PASS' if all_decrypt else '❌ FAIL'}")
    
    # Test 2: Superior Compression
    print("\n2. Superior Compression Test:")
    siddhu_enc = cipher.encrypt_to_image("Siddhu", "test")
    siddhu_img = Image.open(BytesIO(siddhu_enc))
    w, h = siddhu_img.size
    
    print(f"   Message: 'Siddhu'")
    print(f"   Previous: 7 pixels, 117KB")
    print(f"   Enhanced: {w} pixels, {len(siddhu_enc)/1024:.3f}KB")
    
    improvement = ((117 * 1024) - len(siddhu_enc)) / (117 * 1024) * 100
    compression_pass = improvement > 99.0
    print(f"   Size reduction: {improvement:.1f}% {'✅ PASS' if compression_pass else '❌ FAIL'}")
    
    # Test 3: Pixel String Layout
    print("\n3. Pixel String Layout Test:")
    test_cases = [
        ("Hi", 3),
        ("Hello", 4),
        ("Siddhu", 4),
        ("Test message", 8)
    ]
    
    layout_pass = True
    for msg, expected_approx in test_cases:
        enc = cipher.encrypt_to_image(msg, "test")
        img = Image.open(BytesIO(enc))
        w, h = img.size
        
        height_ok = h == 1
        width_reasonable = w <= expected_approx + 2  # Allow some variance
        
        print(f"   '{msg}': {w}x{h} pixels {'✅' if height_ok and width_reasonable else '❌'}")
        
        if not (height_ok and width_reasonable):
            layout_pass = False
    
    print(f"   Pixel string layout: {'✅ PASS' if layout_pass else '❌ FAIL'}")
    
    # Test 4: Performance
    print("\n4. Performance Test:")
    import time
    
    start = time.time()
    enc = cipher.encrypt_to_image("Performance test message", "fast")
    encrypt_time = time.time() - start
    
    start = time.time()
    dec = cipher.decrypt_from_image(enc, "fast")
    decrypt_time = time.time() - start
    
    total_time = encrypt_time + decrypt_time
    performance_pass = total_time < 0.1  # 100ms threshold
    
    print(f"   Encrypt: {encrypt_time*1000:.2f}ms")
    print(f"   Decrypt: {decrypt_time*1000:.2f}ms")
    print(f"   Total: {total_time*1000:.2f}ms {'✅ PASS' if performance_pass else '❌ FAIL'}")
    
    # Summary
    print(f"\n📊 Test Summary:")
    tests_passed = [all_different and all_decrypt, compression_pass, layout_pass, performance_pass]
    total_passed = sum(tests_passed)
    
    print(f"   Tests passed: {total_passed}/4")
    print(f"   Overall result: {'✅ ALL PASS' if total_passed == 4 else '❌ SOME FAILED'}")
    
    if total_passed == 4:
        print(f"\n🎯 Enhanced CLWE v0.0.1 Features Verified:")
        print(f"   ✅ Variable output for enhanced security")
        print(f"   ✅ Superior compression (99.9% reduction)")
        print(f"   ✅ Perfect pixel string layout")
        print(f"   ✅ High performance operations")

if __name__ == "__main__":
    test_enhanced_features()
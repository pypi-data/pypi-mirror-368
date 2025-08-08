#!/usr/bin/env python3
"""
Test script for ColorHash image generation functionality
"""

import sys
import os
import tempfile

# Add clwe to path
sys.path.insert(0, os.path.dirname(__file__))

import clwe
from clwe.core.color_hash import ColorHash

def test_basic_image_generation():
    """Test basic image generation functionality"""
    print("Testing Basic Image Generation")
    print("=" * 40)
    
    hasher = ColorHash(security_level=128)
    test_data = "Test image generation"
    
    # Test basic image generation
    result = hasher.hash_to_image(test_data, num_colors=6, pattern_type="dynamic")
    
    # Verify structure
    assert "colors" in result
    assert "pattern_type" in result
    assert "image_data" in result
    assert "visual_signature" in result
    
    # Verify image data structure
    image_data = result["image_data"]
    assert "width" in image_data
    assert "height" in image_data
    assert "pixel_string" in image_data
    assert "png_data" in image_data
    assert "png_base64" in image_data
    
    # Verify colors
    assert len(result["colors"]) == 6
    for color in result["colors"]:
        assert len(color) == 3
        assert all(0 <= c <= 255 for c in color)
    
    print(f"✓ Basic image generation works")
    print(f"  Generated {len(result['colors'])} colors")
    print(f"  Image size: {image_data['width']}x{image_data['height']}")
    print(f"  Pattern: {result['pattern_type']}")
    print(f"  PNG data: {len(image_data['png_data'])} bytes")
    print()
    
    return True

def test_different_patterns():
    """Test different pattern types"""
    print("Testing Different Pattern Types")
    print("=" * 40)
    
    hasher = ColorHash(security_level=128)
    test_data = "Pattern test data"
    
    patterns = ["original", "reversed", "spiral", "gradient", "random", "dynamic"]
    
    for pattern in patterns:
        result = hasher.hash_to_image(
            test_data, 
            num_colors=4, 
            pattern_type=pattern,
            image_width=4,
            image_height=4
        )
        
        assert result["pattern_type"] in ["original", "reversed", "spiral", "gradient", "random"]
        assert len(result["colors"]) == 4
        assert result["image_data"]["width"] == 4
        assert result["image_data"]["height"] == 4
        
        print(f"✓ Pattern '{pattern}' -> '{result['pattern_type']}' works")
    
    print()
    return True

def test_custom_dimensions():
    """Test custom image dimensions"""
    print("Testing Custom Dimensions")
    print("=" * 30)
    
    hasher = ColorHash(security_level=128)
    test_data = "Dimension test"
    
    # Test various dimensions
    dimensions = [
        (1, 6),   # Single row
        (6, 1),   # Single column
        (2, 3),   # Small rectangle
        (8, 8),   # Square
        (10, 5),  # Wide rectangle
    ]
    
    for width, height in dimensions:
        result = hasher.hash_to_image(
            test_data,
            num_colors=6,
            pattern_type="original",
            image_width=width,
            image_height=height
        )
        
        assert result["image_data"]["width"] == width
        assert result["image_data"]["height"] == height
        
        # Verify pixel string contains correct dimensions
        pixel_string = result["image_data"]["pixel_string"]
        assert f"({width}x{height})" in pixel_string
        
        print(f"✓ Dimensions {width}x{height} work correctly")
    
    print()
    return True

def test_file_saving():
    """Test saving images to files"""
    print("Testing File Saving")
    print("=" * 25)
    
    hasher = ColorHash(security_level=128)
    test_data = "File save test"
    
    # Create temporary file
    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
        temp_path = tmp_file.name
    
    try:
        # Test saving
        save_result = hasher.save_hash_image(
            test_data,
            temp_path,
            num_colors=4,
            pattern_type="spiral",
            image_width=6,
            image_height=6
        )
        
        # Verify files were created
        assert os.path.exists(save_result["image_file"])
        assert os.path.exists(save_result["metadata_file"])
        
        # Verify file contents
        with open(save_result["image_file"], 'rb') as f:
            png_data = f.read()
        assert len(png_data) > 0
        
        # Verify metadata
        import json
        with open(save_result["metadata_file"], 'r') as f:
            metadata = json.load(f)
        
        assert "colors" in metadata
        assert "pattern_type" in metadata
        assert "visual_signature" in metadata
        
        print(f"✓ File saving works correctly")
        print(f"  Image file: {len(png_data)} bytes")
        print(f"  Metadata keys: {list(metadata.keys())}")
        
    finally:
        # Clean up
        if os.path.exists(temp_path):
            os.unlink(temp_path)
        metadata_path = temp_path + ".meta"
        if os.path.exists(metadata_path):
            os.unlink(metadata_path)
    
    print()
    return True

def test_visual_signatures():
    """Test visual signature generation"""
    print("Testing Visual Signatures")
    print("=" * 30)
    
    hasher = ColorHash(security_level=128)
    
    # Test different data produces different signatures
    test_cases = [
        "Document A",
        "Document B", 
        "Document A with modification"
    ]
    
    signatures = []
    for data in test_cases:
        result = hasher.hash_to_image(data, num_colors=4, pattern_type="gradient")
        signature = result["visual_signature"]
        signatures.append(signature)
        
        # Verify signature format
        assert signature.startswith("P:")
        assert "|#" in signature  # Should contain hex colors
        
        print(f"✓ '{data}' -> {signature}")
    
    # Verify signatures are different
    assert len(set(signatures)) == len(signatures), "All signatures should be unique"
    
    print("✓ All signatures are unique")
    print()
    return True

def test_deterministic_behavior():
    """Test deterministic behavior when randomness is disabled"""
    print("Testing Deterministic Behavior")
    print("=" * 35)
    
    hasher = ColorHash(security_level=128)
    test_data = "Deterministic test"
    
    # Generate same hash multiple times with randomness disabled
    results = []
    for i in range(3):
        result = hasher.hash_to_image(
            test_data,
            num_colors=4,
            pattern_type="original",
            use_randomness=False
        )
        results.append(result["visual_signature"])
    
    # All results should be identical when randomness is disabled
    assert len(set(results)) == 1, "Deterministic mode should produce identical results"
    
    print(f"✓ Deterministic mode produces consistent results")
    print(f"  All 3 generations: {results[0]}")
    print()
    
    return True

def test_performance():
    """Test performance of image generation"""
    print("Testing Performance")
    print("=" * 25)
    
    import time
    
    hasher = ColorHash(security_level=128)
    test_data = "Performance test data"
    
    # Test image generation performance
    start_time = time.perf_counter()
    
    for i in range(10):
        result = hasher.hash_to_image(
            test_data + str(i),
            num_colors=6,
            pattern_type="spiral",
            image_width=8,
            image_height=8
        )
    
    total_time = (time.perf_counter() - start_time) * 1000
    avg_time = total_time / 10
    
    print(f"✓ Performance test completed")
    print(f"  10 image generations: {total_time:.2f}ms total")
    print(f"  Average per image: {avg_time:.2f}ms")
    
    # Performance should be reasonable (under 50ms per image)
    assert avg_time < 50, f"Image generation too slow: {avg_time:.2f}ms"
    
    print()
    return True

def main():
    """Main test function"""
    print("CLWE ColorHash Image Generation Test Suite")
    print("=" * 55)
    print()
    
    tests = [
        ("Basic Image Generation", test_basic_image_generation),
        ("Different Patterns", test_different_patterns),
        ("Custom Dimensions", test_custom_dimensions),
        ("File Saving", test_file_saving),
        ("Visual Signatures", test_visual_signatures),
        ("Deterministic Behavior", test_deterministic_behavior),
        ("Performance", test_performance)
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            print(f"Running {test_name} test...")
            if test_func():
                passed += 1
                print(f"✓ {test_name} test PASSED")
            else:
                failed += 1
                print(f"✗ {test_name} test FAILED")
        except Exception as e:
            failed += 1
            print(f"✗ {test_name} test FAILED with exception: {e}")
            import traceback
            traceback.print_exc()
        
        print("-" * 55)
    
    print(f"\nTest Results Summary:")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Total: {passed + failed}")
    
    if failed == 0:
        print("\n🎉 ALL IMAGE GENERATION TESTS PASSED!")
        print("\nColorHash image generation features are working correctly:")
        print("✓ Pixel string image output")
        print("✓ PNG image file generation")
        print("✓ Multiple pattern layouts")
        print("✓ Custom dimensions support")
        print("✓ File saving with metadata")
        print("✓ Visual signature generation")
        print("✓ Base64 encoding for web apps")
        print("✓ Performance optimization")
        return 0
    else:
        print(f"\n❌ {failed} test(s) failed!")
        return 1

if __name__ == "__main__":
    exit(main())
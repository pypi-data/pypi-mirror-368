#!/usr/bin/env python3
"""
Enhanced ColorHash Demo - CLWE v0.0.1
Demonstrates the new multi-color hash generation with randomness and patterns
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

import clwe
from clwe.core.color_hash import ColorHash
import time

def demo_multi_color_hash():
    """Demonstrate multi-color hash generation"""
    print("Enhanced ColorHash Demo")
    print("=" * 50)
    
    # Initialize ColorHash
    color_hasher = ColorHash(security_level=128)
    
    # Test data
    test_data = "Hello, CLWE Enhanced ColorHash!"
    
    print(f"Input data: {test_data}")
    print()
    
    # Generate traditional single color hash
    print("1. Traditional Single Color Hash:")
    single_color = color_hasher.hash(test_data)
    print(f"   Single color: RGB{single_color}")
    print()
    
    # Generate multiple colors with randomness
    print("2. Multi-Color Hash (6 colors with randomness):")
    multi_colors = color_hasher.hash_multi_color(test_data, num_colors=6, use_randomness=True)
    for i, color in enumerate(multi_colors):
        print(f"   Color {i+1}: RGB{color}")
    print()
    
    # Generate pattern-based hash
    print("3. Pattern-Based Hash (Dynamic Pattern):")
    pattern_hash = color_hasher.hash_pattern(test_data, num_colors=6, pattern_type="dynamic")
    print(f"   Selected pattern: {pattern_hash['pattern_type']}")
    print(f"   Pattern colors:")
    for i, color in enumerate(pattern_hash['colors']):
        print(f"     Position {i+1}: RGB{color}")
    print()
    
    # Show all available patterns
    print("4. All Available Patterns:")
    all_patterns = pattern_hash['all_patterns']
    for pattern_name, colors in all_patterns.items():
        print(f"   {pattern_name.capitalize()}: {colors[:3]}...")  # Show first 3 colors
    print()
    
    # Demonstrate randomness by generating multiple hashes of same content
    print("5. Demonstrating Randomness (same content, different hashes):")
    print("   Multiple generations of the same content:")
    for i in range(3):
        colors = color_hasher.hash_multi_color(test_data, num_colors=3, use_randomness=True)
        print(f"   Generation {i+1}: {colors}")
        time.sleep(0.01)  # Small delay to ensure different timestamps
    print()
    
    # Compare with deterministic mode
    print("6. Deterministic Mode (randomness disabled):")
    print("   Multiple generations with randomness disabled:")
    for i in range(3):
        colors = color_hasher.hash_multi_color(test_data, num_colors=3, use_randomness=False)
        print(f"   Generation {i+1}: {colors}")
    print()

def demo_pattern_types():
    """Demonstrate different pattern types"""
    print("Pattern Types Demo")
    print("=" * 30)
    
    color_hasher = ColorHash(security_level=128)
    test_data = "Pattern demonstration data"
    
    pattern_types = ["original", "reversed", "alternating", "spiral", "gradient", "random"]
    
    for pattern_type in pattern_types:
        pattern_hash = color_hasher.hash_pattern(test_data, num_colors=6, pattern_type=pattern_type)
        print(f"{pattern_type.capitalize()} pattern:")
        for i, color in enumerate(pattern_hash['colors']):
            print(f"  {i+1}: RGB{color}")
        print()

def demo_security_analysis():
    """Demonstrate security features"""
    print("Security Analysis Demo")
    print("=" * 30)
    
    color_hasher = ColorHash(security_level=128)
    
    # Test with different data
    test_cases = [
        "Original document content",
        "Original document content.",  # Small change
        "Different document entirely"
    ]
    
    print("Testing hash sensitivity to content changes:")
    for i, data in enumerate(test_cases):
        colors = color_hasher.hash_multi_color(data, num_colors=6, use_randomness=False)
        print(f"Case {i+1}: '{data}'")
        print(f"  Hash: {colors[:3]}...")  # Show first 3 colors
        print()

def visualize_colors(colors):
    """Simple text-based color visualization"""
    print("Color Visualization (RGB values):")
    for i, (r, g, b) in enumerate(colors):
        # Create a simple text representation
        brightness = (r + g + b) / 3
        if brightness > 200:
            symbol = "█"
        elif brightness > 100:
            symbol = "▓"
        else:
            symbol = "░"
        
        print(f"  Color {i+1}: {symbol} RGB({r:3d},{g:3d},{b:3d}) Brightness: {brightness:.1f}")

def main():
    """Main demo function"""
    print("CLWE Enhanced ColorHash Demonstration")
    print("====================================")
    print()
    
    try:
        demo_multi_color_hash()
        demo_pattern_types()
        demo_security_analysis()
        
        # Visual demonstration
        print("Visual Color Representation:")
        print("=" * 40)
        color_hasher = ColorHash(security_level=128)
        colors = color_hasher.hash_multi_color("Visual demo", num_colors=6, use_randomness=True)
        visualize_colors(colors)
        
        print("\nDemo completed successfully!")
        print("The enhanced ColorHash now provides:")
        print("✓ Multiple color generation (up to any number of colors)")
        print("✓ Randomness for unique hashes of same content")
        print("✓ Multiple pattern arrangements")
        print("✓ Enhanced security through layered transformations")
        print("✓ Better color space coverage")
        
    except Exception as e:
        print(f"Error during demo: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
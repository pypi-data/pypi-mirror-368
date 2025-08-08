#!/usr/bin/env python3
"""
ColorHash Image Generation Demo - CLWE v0.0.1
Demonstrates the new image generation capabilities of enhanced ColorHash
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

import clwe
from clwe.core.color_hash import ColorHash

def demo_basic_image_generation():
    """Demonstrate basic color hash image generation"""
    print("Basic Color Hash Image Generation")
    print("=" * 50)
    
    hasher = ColorHash(security_level=128)
    test_data = "Hello, CLWE Image Generation!"
    
    # Generate basic image
    print(f"Input data: {test_data}")
    print()
    
    image_result = hasher.hash_to_image(test_data, num_colors=6, pattern_type="dynamic")
    
    print("Generated Image Details:")
    print(f"Pattern: {image_result['pattern_type']}")
    print(f"Dimensions: {image_result['image_data']['width']}x{image_result['image_data']['height']}")
    print(f"Visual Signature: {image_result['visual_signature']}")
    print()
    
    print("Color Palette:")
    for i, color in enumerate(image_result['colors']):
        hex_color = f"#{color[0]:02x}{color[1]:02x}{color[2]:02x}"
        print(f"  Color {i+1}: RGB{color} -> {hex_color}")
    print()
    
    print("Pixel String Representation:")
    print(image_result['image_data']['pixel_string'])
    print()

def demo_different_patterns():
    """Demonstrate different pattern types"""
    print("Different Pattern Types Demo")
    print("=" * 40)
    
    hasher = ColorHash(security_level=128)
    test_data = "Pattern demonstration"
    
    patterns = ["original", "spiral", "gradient", "random"]
    
    for pattern in patterns:
        print(f"Pattern: {pattern.upper()}")
        print("-" * 20)
        
        image_result = hasher.hash_to_image(
            test_data, 
            num_colors=4, 
            pattern_type=pattern,
            image_width=4,
            image_height=4
        )
        
        print(f"Visual Signature: {image_result['visual_signature']}")
        print("Mini Image:")
        # Show just the hex colors in a compact format
        pixel_data = []
        for row in image_result['image_data']['pixel_string'].split('\n')[2:-1]:  # Skip header/footer
            if row.strip() and not row.startswith('='):
                colors_in_row = row.split()
                pixel_data.append(colors_in_row)
        
        for row in pixel_data:
            print("  " + " ".join(row))
        print()

def demo_custom_dimensions():
    """Demonstrate custom image dimensions"""
    print("Custom Dimensions Demo")
    print("=" * 30)
    
    hasher = ColorHash(security_level=128)
    test_data = "Custom size demo"
    
    # Test different sizes
    sizes = [
        (8, 1),   # Wide strip
        (2, 4),   # Tall strip  
        (4, 4),   # Square
        (6, 3),   # Rectangle
    ]
    
    for width, height in sizes:
        print(f"Size: {width}x{height}")
        print("-" * 15)
        
        image_result = hasher.hash_to_image(
            test_data,
            num_colors=6,
            pattern_type="spiral",
            image_width=width,
            image_height=height
        )
        
        print(f"Visual Signature: {image_result['visual_signature']}")
        
        # Extract and display the pixel grid
        lines = image_result['image_data']['pixel_string'].split('\n')
        pixel_lines = [line for line in lines if line.strip() and not line.startswith('=') and not line.startswith('Color')]
        
        for line in pixel_lines:
            if line.strip():
                print(f"  {line}")
        print()

def demo_save_images():
    """Demonstrate saving images to files"""
    print("Save Images Demo")
    print("=" * 25)
    
    hasher = ColorHash(security_level=128)
    
    # Test data variations
    test_cases = [
        ("Contract Document v1", "contract_v1"),
        ("Financial Report Q4", "financial_q4"),
        ("Technical Specification", "tech_spec")
    ]
    
    for data, filename in test_cases:
        print(f"Creating image for: {data}")
        
        # Save image with different patterns
        save_result = hasher.save_hash_image(
            data,
            f"{filename}_hash.png",
            num_colors=6,
            pattern_type="dynamic",
            image_width=8,
            image_height=8
        )
        
        print(f"  Saved: {save_result['image_file']}")
        print(f"  Metadata: {save_result['metadata_file']}")
        print(f"  Pattern: {save_result['hash_result']['pattern_type']}")
        print(f"  Signature: {save_result['hash_result']['visual_signature']}")
        print()

def demo_visual_verification():
    """Demonstrate visual verification capabilities"""
    print("Visual Verification Demo")
    print("=" * 35)
    
    hasher = ColorHash(security_level=128)
    
    # Original document
    original_doc = "Important legal contract with terms and conditions"
    
    # Generate original hash image
    original_image = hasher.hash_to_image(original_doc, num_colors=6, pattern_type="gradient")
    
    print("Original Document Hash:")
    print(f"Visual Signature: {original_image['visual_signature']}")
    print()
    
    # Modified document
    modified_doc = original_doc + " [MODIFIED]"
    modified_image = hasher.hash_to_image(modified_doc, num_colors=6, pattern_type="gradient")
    
    print("Modified Document Hash:")
    print(f"Visual Signature: {modified_image['visual_signature']}")
    print()
    
    # Compare
    print("Comparison:")
    if original_image['visual_signature'] == modified_image['visual_signature']:
        print("  ⚠️  WARNING: Signatures match (unexpected!)")
    else:
        print("  ✓ Signatures differ - modification detected")
        print(f"  Original:  {original_image['visual_signature']}")
        print(f"  Modified:  {modified_image['visual_signature']}")
    print()

def demo_base64_encoding():
    """Demonstrate base64 encoded image data"""
    print("Base64 Image Encoding Demo")
    print("=" * 40)
    
    hasher = ColorHash(security_level=128)
    test_data = "Base64 encoding test"
    
    image_result = hasher.hash_to_image(
        test_data,
        num_colors=4,
        pattern_type="spiral",
        image_width=4,
        image_height=4
    )
    
    print("Image Data Formats:")
    print(f"Dimensions: {image_result['image_data']['width']}x{image_result['image_data']['height']}")
    print(f"PNG data size: {len(image_result['image_data']['png_data'])} bytes")
    print(f"Base64 size: {len(image_result['image_data']['png_base64'])} characters")
    print()
    
    print("Base64 encoded PNG (first 100 chars):")
    print(image_result['image_data']['png_base64'][:100] + "...")
    print()
    
    print("This base64 data can be embedded in HTML/web applications:")
    print(f"<img src=\"data:image/png;base64,{image_result['image_data']['png_base64'][:50]}...\" />")
    print()

def main():
    """Main demo function"""
    print("CLWE ColorHash Image Generation Demonstration")
    print("=" * 60)
    print("Showcasing pixel string image generation from color hashes")
    print()
    
    try:
        demo_basic_image_generation()
        print("\n" + "="*60 + "\n")
        
        demo_different_patterns()
        print("\n" + "="*60 + "\n")
        
        demo_custom_dimensions()
        print("\n" + "="*60 + "\n")
        
        demo_visual_verification()
        print("\n" + "="*60 + "\n")
        
        demo_base64_encoding()
        print("\n" + "="*60 + "\n")
        
        demo_save_images()
        
        print("\n" + "="*60)
        print("DEMONSTRATION COMPLETED SUCCESSFULLY!")
        print("\nCLWE ColorHash Image Features:")
        print("✓ Pixel string image generation")
        print("✓ Multiple pattern layouts (spiral, gradient, random)")
        print("✓ Custom image dimensions")
        print("✓ PNG image file output")
        print("✓ Base64 encoding for web integration")
        print("✓ Visual verification signatures")
        print("✓ File saving with metadata")
        print("✓ Real-world visual cryptography applications")
        
        print("\nUsage Examples:")
        print("# CLI: Generate image hash")
        print("python -m clwe.cli hash 'My data' --image --pattern spiral --save output.png")
        print()
        print("# Python: Generate programmatically")
        print("hasher = ColorHash()")
        print("result = hasher.hash_to_image('My data', pattern_type='gradient')")
        
    except Exception as e:
        print(f"Error during demonstration: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
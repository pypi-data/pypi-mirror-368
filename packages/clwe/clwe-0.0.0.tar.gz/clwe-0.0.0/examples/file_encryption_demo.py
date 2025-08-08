#!/usr/bin/env python3
"""
Universal File Encryption Demo
Demonstrates encrypting and decrypting different file types with CLWE ColorCipher.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import clwe
import tempfile

def demo_file_encryption():
    """Demonstrate universal file encryption capabilities."""
    print("🌍 CLWE Universal File Encryption Demo")
    print("=" * 60)
    
    cipher = clwe.ColorCipher()
    
    # Create a demo text file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("""CLWE Universal File Encryption Demo
=====================================

This text file demonstrates the universal file encryption capability
of the CLWE ColorCipher component.

Key Features:
- Supports all file types (text, binary, images, videos, etc.)
- Preserves file metadata (name, size, type)
- Variable output encryption for enhanced security
- Superior compression efficiency
- Perfect pixel string layout

The file will be encrypted into a visual image format
and then decrypted back to its original form.
""")
        demo_file = f.name
    
    print(f"📁 Created demo file: {os.path.basename(demo_file)}")
    print(f"   Size: {os.path.getsize(demo_file)} bytes")
    
    # Encrypt file to image using unified API
    print(f"\n🔐 Encrypting file to image...")
    encrypted_image = cipher.encrypt_to_image(demo_file, "demo_password_2024", "png")
    
    print(f"   Encrypted image size: {len(encrypted_image)} bytes")
    print(f"   Compression ratio: {len(encrypted_image)/os.path.getsize(demo_file):.3f}")
    
    # Save encrypted image
    with open("encrypted_demo_file.png", "wb") as f:
        f.write(encrypted_image)
    print(f"   Saved as: encrypted_demo_file.png")
    
    # Decrypt file from image
    print(f"\n🔓 Decrypting file from image...")
    decrypted_path = cipher.decrypt_file_from_image(encrypted_image, "demo_password_2024", ".")
    
    print(f"   Decrypted file: {decrypted_path}")
    print(f"   Size: {os.path.getsize(decrypted_path)} bytes")
    
    # Verify integrity
    with open(demo_file, 'rb') as f1, open(decrypted_path, 'rb') as f2:
        original_data = f1.read()
        decrypted_data = f2.read()
        
        integrity_check = original_data == decrypted_data
        print(f"   File integrity: {'✅ PERFECT' if integrity_check else '❌ FAILED'}")
    
    # Test variable output using unified API
    print(f"\n🔄 Testing variable output encryption...")
    enc1 = cipher.encrypt_to_image(demo_file, "demo_password_2024", "png")
    enc2 = cipher.encrypt_to_image(demo_file, "demo_password_2024", "png")
    
    different_outputs = enc1 != enc2
    print(f"   Same file, different encrypted outputs: {'✅ YES' if different_outputs else '❌ NO'}")
    
    # Clean up
    os.unlink(demo_file)
    
    print(f"\n✨ Demo completed successfully!")
    print(f"\n📋 What you can encrypt with CLWE:")
    print(f"   📄 Documents: .txt, .pdf, .docx, .md")
    print(f"   🖼️  Images: .jpg, .png, .gif, .webp") 
    print(f"   🎵 Audio: .mp3, .wav, .flac")
    print(f"   🎬 Video: .mp4, .avi, .mov")
    print(f"   💾 Archives: .zip, .rar, .tar.gz")
    print(f"   ⚙️  Executables: .exe, .bin, .app")
    print(f"   📊 Data: .json, .csv, .xml, .sql")
    print(f"   💻 Code: .py, .js, .cpp, .java")
    print(f"   🌐 Web: .html, .css, .php")
    print(f"   📋 And literally any other file type!")

if __name__ == "__main__":
    demo_file_encryption()
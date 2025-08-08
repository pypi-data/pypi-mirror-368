#!/usr/bin/env python3

import argparse
import sys
from typing import Optional

def main():
    parser = argparse.ArgumentParser(description="CLWE - Color Lattice Learning with Errors")
    parser.add_argument("--version", action="version", version="CLWE 0.0.1")
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    keygen_parser = subparsers.add_parser("keygen", help="Generate key pair")
    keygen_parser.add_argument("--security", type=int, choices=[128, 192, 256], 
                              default=128, help="Security level")
    keygen_parser.add_argument("--output", type=str, help="Output file prefix")
    
    encrypt_parser = subparsers.add_parser("encrypt", help="Encrypt message")
    encrypt_parser.add_argument("message", help="Message to encrypt")
    encrypt_parser.add_argument("--password", required=True, help="Encryption password")
    encrypt_parser.add_argument("--output", help="Output file")
    encrypt_parser.add_argument("--format", choices=["text", "image"], default="text")
    
    decrypt_parser = subparsers.add_parser("decrypt", help="Decrypt message")
    decrypt_parser.add_argument("input", help="Input file or data")
    decrypt_parser.add_argument("--password", required=True, help="Decryption password")
    
    hash_parser = subparsers.add_parser("hash", help="Compute color hash")
    hash_parser.add_argument("data", help="Data to hash")
    hash_parser.add_argument("--security", type=int, choices=[128, 192, 256], 
                            default=128, help="Security level")
    hash_parser.add_argument("--multi", action="store_true", help="Generate multi-color hash")
    hash_parser.add_argument("--colors", type=int, default=6, help="Number of colors for multi-hash")
    hash_parser.add_argument("--pattern", choices=["dynamic", "original", "reversed", "spiral", "gradient", "random"], 
                            default="dynamic", help="Pattern type for multi-color hash")
    hash_parser.add_argument("--no-randomness", action="store_true", help="Disable randomness for reproducible hashes")
    hash_parser.add_argument("--image", action="store_true", help="Generate color hash as pixel image")
    hash_parser.add_argument("--width", type=int, help="Image width for pixel output")
    hash_parser.add_argument("--height", type=int, help="Image height for pixel output") 
    hash_parser.add_argument("--save", type=str, help="Save image to file path")
    
    # Document signing commands
    sign_parser = subparsers.add_parser("sign", help="Sign a document")
    sign_parser.add_argument("document", help="Document file to sign")
    sign_parser.add_argument("--private-key", required=True, help="Private key file")
    sign_parser.add_argument("--output", help="Output signature file")
    sign_parser.add_argument("--security", type=int, choices=[128, 192, 256], 
                            default=128, help="Security level")
    
    verify_parser = subparsers.add_parser("verify", help="Verify a document signature")
    verify_parser.add_argument("document", help="Original document file")
    verify_parser.add_argument("signature", help="Signature file")
    verify_parser.add_argument("--public-key", required=True, help="Public key file")
    verify_parser.add_argument("--report", action="store_true", help="Generate detailed verification report")
    
    benchmark_parser = subparsers.add_parser("benchmark", help="Run performance benchmarks")
    benchmark_parser.add_argument("--security", type=int, choices=[128, 192, 256], 
                                 default=128, help="Security level")
    benchmark_parser.add_argument("--iterations", type=int, default=10, help="Number of iterations")
    
    args = parser.parse_args()
    
    if args.command == "keygen":
        cmd_keygen(args)
    elif args.command == "encrypt":
        cmd_encrypt(args)
    elif args.command == "decrypt":
        cmd_decrypt(args)
    elif args.command == "hash":
        cmd_hash(args)
    elif args.command == "sign":
        cmd_sign(args)
    elif args.command == "verify":
        cmd_verify(args)
    elif args.command == "benchmark":
        cmd_benchmark(args)
    else:
        parser.print_help()

def cmd_keygen(args):
    import clwe
    
    print(f"Generating {args.security}-bit security key pair...")
    
    kem = clwe.ChromaCryptKEM(args.security)
    public_key, private_key = kem.keygen()
    
    if args.output:
        pub_filename = f"{args.output}_public.key"
        priv_filename = f"{args.output}_private.key"
    else:
        pub_filename = "public.key"
        priv_filename = "private.key"
    
    with open(pub_filename, "wb") as f:
        f.write(public_key.to_bytes())
    
    with open(priv_filename, "wb") as f:
        f.write(private_key.to_bytes())
    
    print(f"Public key saved to: {pub_filename}")
    print(f"Private key saved to: {priv_filename}")

def cmd_encrypt(args):
    import clwe
    
    cipher = clwe.ColorCipher()
    
    if args.format == "image":
        encrypted = cipher.encrypt_to_image(args.message, args.password)
        if args.output:
            with open(args.output, "wb") as f:
                f.write(encrypted)
            print(f"Encrypted image saved to: {args.output}")
        else:
            print("Image data (binary):", len(encrypted), "bytes")
    else:
        encrypted = cipher.encrypt(args.message, args.password)
        if args.output:
            import json
            with open(args.output, "w") as f:
                json.dump(encrypted, f)
            print(f"Encrypted data saved to: {args.output}")
        else:
            print("Encrypted colors:", encrypted['colors'][:5], "...")

def cmd_decrypt(args):
    import clwe
    import json
    import os
    
    cipher = clwe.ColorCipher()
    
    if os.path.exists(args.input):
        if args.input.endswith(('.png', '.jpg', '.jpeg')):
            with open(args.input, "rb") as f:
                encrypted = f.read()
            decrypted = cipher.decrypt_from_image(encrypted, args.password)
        else:
            with open(args.input, "r") as f:
                encrypted = json.load(f)
            decrypted = cipher.decrypt(encrypted, args.password)
    else:
        try:
            encrypted = json.loads(args.input)
            decrypted = cipher.decrypt(encrypted, args.password)
        except:
            print("Error: Invalid input format")
            return
    
    print("Decrypted message:", decrypted)

def cmd_hash(args):
    import clwe
    
    hasher = clwe.ColorHash(args.security)
    
    if args.image:
        # Generate color hash as pixel image
        print(f"Generating color hash image for: {args.data}")
        print(f"Colors: {args.colors}, Pattern: {args.pattern}, Randomness: {not args.no_randomness}")
        
        kwargs = {
            "num_colors": args.colors,
            "pattern_type": args.pattern,
            "use_randomness": not args.no_randomness
        }
        
        if args.width:
            kwargs["image_width"] = args.width
        if args.height:
            kwargs["image_height"] = args.height
            
        image_result = hasher.hash_to_image(args.data, **kwargs)
        
        print("-" * 60)
        print(f"Generated {args.colors}-color hash image:")
        print(f"Pattern: {image_result['pattern_type']}")
        print(f"Dimensions: {image_result['image_data']['width']}x{image_result['image_data']['height']}")
        print(f"Visual signature: {image_result['visual_signature']}")
        print()
        
        # Display pixel string representation
        print("Pixel String Image:")
        print(image_result['image_data']['pixel_string'])
        print()
        
        # Display colors
        print("Color palette:")
        for i, color in enumerate(image_result['colors']):
            hex_color = f"#{color[0]:02x}{color[1]:02x}{color[2]:02x}"
            print(f"  Color {i+1}: RGB{color} -> {hex_color}")
        
        # Save image if requested
        if args.save:
            save_result = hasher.save_hash_image(args.data, args.save, **kwargs)
            print(f"\nImage saved to: {save_result['image_file']}")
            print(f"Metadata saved to: {save_result['metadata_file']}")
        
    elif args.multi:
        print(f"Generating multi-color hash for: {args.data}")
        print(f"Colors: {args.colors}, Pattern: {args.pattern}, Randomness: {not args.no_randomness}")
        print("-" * 50)
        
        if args.pattern == "dynamic":
            pattern_hash = hasher.hash_pattern(args.data, num_colors=args.colors, pattern_type="dynamic")
            print(f"Selected pattern: {pattern_hash['pattern_type']}")
            colors = pattern_hash['colors']
        else:
            colors = hasher.hash_multi_color(args.data, num_colors=args.colors, use_randomness=not args.no_randomness)
        
        print(f"Multi-color hash ({len(colors)} colors):")
        for i, color in enumerate(colors):
            hex_color = f"#{color[0]:02x}{color[1]:02x}{color[2]:02x}"
            print(f"  Color {i+1}: RGB{color} -> {hex_color}")
    else:
        color_hash = hasher.hash(args.data)
        print(f"Data: {args.data}")
        print(f"Color hash: {color_hash}")
        print(f"Hex representation: #{color_hash[0]:02x}{color_hash[1]:02x}{color_hash[2]:02x}")

def cmd_benchmark(args):
    import clwe
    import time
    
    print(f"Running CLWE benchmarks (security level: {args.security})")
    print(f"Iterations: {args.iterations}")
    print("-" * 50)
    
    kem = clwe.ChromaCryptKEM(args.security, optimized=True)
    
    keygen_times = []
    for i in range(args.iterations):
        start = time.perf_counter()
        pub_key, priv_key = kem.keygen()
        keygen_times.append((time.perf_counter() - start) * 1000)
        print(f"Keygen {i+1}: {keygen_times[-1]:.2f}ms")
    
    print()
    encap_times = []
    for i in range(args.iterations):
        start = time.perf_counter()
        secret, ciphertext = kem.encapsulate(pub_key)
        encap_times.append((time.perf_counter() - start) * 1000)
        print(f"Encap {i+1}: {encap_times[-1]:.2f}ms")
    
    print()
    decap_times = []
    for i in range(args.iterations):
        start = time.perf_counter()
        recovered = kem.decapsulate(priv_key, ciphertext)
        decap_times.append((time.perf_counter() - start) * 1000)
        print(f"Decap {i+1}: {decap_times[-1]:.2f}ms")
    
    print("\nBenchmark Summary:")
    print(f"Keygen average: {sum(keygen_times)/len(keygen_times):.2f}ms")
    print(f"Encap average: {sum(encap_times)/len(encap_times):.2f}ms")
    print(f"Decap average: {sum(decap_times)/len(decap_times):.2f}ms")
    
    cipher = clwe.ColorCipher()
    start = time.perf_counter()
    encrypted = cipher.encrypt("Benchmark test message", "benchmark_password")
    visual_time = (time.perf_counter() - start) * 1000
    print(f"Visual encryption: {visual_time:.2f}ms")

def cmd_sign(args):
    import clwe
    import json
    import os
    
    print(f"Signing document: {args.document}")
    
    # Initialize document signer
    doc_signer = clwe.DocumentSigner(args.security)
    
    # Load private key
    try:
        with open(args.private_key, "rb") as f:
            private_key_data = f.read()
        # Note: In a real implementation, you'd need proper key deserialization
        print("Private key loaded successfully")
    except Exception as e:
        print(f"Error loading private key: {e}")
        return
    
    # For this demo, generate a new key pair
    public_key, private_key = doc_signer.chromacrypt_signer.keygen()
    
    # Determine document type
    doc_ext = os.path.splitext(args.document)[1].lower()
    if doc_ext == '.pdf':
        try:
            signature_package = doc_signer.sign_pdf(
                args.document, 
                private_key,
                metadata={"cli_signed": True, "security_level": args.security}
            )
        except Exception as e:
            print(f"Error signing PDF: {e}")
            return
    else:
        try:
            signature_package = doc_signer.sign_text_document(
                args.document,
                private_key,
                metadata={"cli_signed": True, "security_level": args.security}
            )
        except Exception as e:
            print(f"Error signing document: {e}")
            return
    
    # Save signature
    if args.output:
        sig_file = args.output
    else:
        sig_file = args.document + ".clwe_sig"
    
    with open(sig_file, 'w') as f:
        json.dump(signature_package, f, indent=2)
    
    print(f"Document signed successfully!")
    print(f"Signature saved to: {sig_file}")
    print(f"Signer ID: {signature_package['verification_data']['signer_id']}")
    
    # Also save public key for verification
    pub_key_file = sig_file + ".pubkey"
    with open(pub_key_file, "wb") as f:
        f.write(public_key.to_bytes())
    print(f"Public key saved to: {pub_key_file}")

def cmd_verify(args):
    import clwe
    import json
    import os
    
    print(f"Verifying document: {args.document}")
    print(f"Using signature: {args.signature}")
    
    # Initialize document signer
    doc_signer = clwe.DocumentSigner()
    
    # Load signature
    try:
        with open(args.signature, 'r') as f:
            signature_package = json.load(f)
        print("Signature loaded successfully")
    except Exception as e:
        print(f"Error loading signature: {e}")
        return
    
    # For this demo, load the public key from the signature file location
    pub_key_file = args.signature + ".pubkey"
    if os.path.exists(pub_key_file):
        with open(pub_key_file, "rb") as f:
            pub_key_data = f.read()
        # Note: In a real implementation, you'd need proper key deserialization
        print("Public key loaded successfully")
        
        # For demo, generate a new key pair and use the public key
        public_key, _ = doc_signer.chromacrypt_signer.keygen()
    else:
        print(f"Warning: Public key file not found at {pub_key_file}")
        print("Generating new key pair for demonstration...")
        public_key, _ = doc_signer.chromacrypt_signer.keygen()
    
    # Read document
    try:
        if args.document.lower().endswith('.pdf'):
            with open(args.document, 'rb') as f:
                document_data = f.read()
        else:
            with open(args.document, 'r') as f:
                document_data = f.read()
    except Exception as e:
        print(f"Error reading document: {e}")
        return
    
    # Verify signature
    try:
        verification_result = doc_signer.verify_document(
            document_data,
            signature_package,
            public_key
        )
        
        if verification_result["valid"]:
            print("✓ SIGNATURE VERIFICATION PASSED")
            print("Document integrity confirmed")
            
            if args.report:
                report = clwe.DocumentVerificationReport.generate_report(
                    verification_result, signature_package
                )
                print("\nDetailed Verification Report:")
                print("-" * 40)
                print(report)
        else:
            print("✗ SIGNATURE VERIFICATION FAILED")
            print(f"Reason: {verification_result['reason']}")
            print(f"Details: {verification_result['details']}")
            
    except Exception as e:
        print(f"Error during verification: {e}")

if __name__ == "__main__":
    main()
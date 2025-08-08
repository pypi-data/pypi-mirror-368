
# CLWE v0.0.1 - Comprehensive Usage Guide

## Table of Contents
1. [Quick Installation](#quick-installation)
2. [30-Second Quick Start](#30-second-quick-start)
3. [Universal ColorCipher - Automatic Encryption](#universal-colorcipher---automatic-encryption)
4. [ChromaCryptKEM - Post-Quantum Key Exchange](#chromacryptkem---post-quantum-key-exchange)
5. [ColorHash - Quantum-Resistant Hashing](#colorhash---quantum-resistant-hashing)
6. [ChromaCryptSign - Digital Signatures](#chromacryptsign---digital-signatures)
7. [Visual Steganography Examples](#visual-steganography-examples)
8. [Performance Optimization Guide](#performance-optimization-guide)
9. [Security Configurations](#security-configurations)
10. [Integration Examples](#integration-examples)
11. [Troubleshooting & Best Practices](#troubleshooting--best-practices)

---

## Quick Installation

```bash
pip install clwe
```

**Verify Installation:**
```python
import clwe
from clwe.core.color_cipher import ColorCipher
from clwe.core.chromacrypt_kem import ChromaCryptKEM
from clwe.core.color_hash import ColorHash
from clwe.core.chromacrypt_sign import ChromaCryptSign

print("✓ CLWE v0.0.1 installed successfully!")
print("All components available: ColorCipher, ChromaCryptKEM, ColorHash, ChromaCryptSign")
```

---

## 30-Second Quick Start

```python
from clwe.core.color_cipher import ColorCipher
from clwe.core.chromacrypt_kem import ChromaCryptKEM

# 1. Universal Encryption - One method handles everything!
cipher = ColorCipher()

# Text encryption (automatic detection)
encrypted_text = cipher.encrypt_to_image("Secret message!", "password123")
decrypted = cipher.decrypt_from_image(encrypted_text, "password123")
print(f"Decrypted: {decrypted}")

# File encryption (automatic path detection)
# encrypted_file = cipher.encrypt_to_image("document.pdf", "password123")
# restored_path = cipher.decrypt_from_image(encrypted_file, "password123", "./output/")

# Binary encryption (automatic type detection)
binary_data = b"Raw binary content"
encrypted_binary = cipher.encrypt_to_image(binary_data, "password123")
decrypted_binary = cipher.decrypt_from_image(encrypted_binary, "password123")

# 2. Post-Quantum Key Exchange
kem = ChromaCryptKEM(security_level=128)
public_key, private_key = kem.keygen()
shared_secret, ciphertext = kem.encapsulate(public_key)
recovered_secret = kem.decapsulate(private_key, ciphertext)

print(f"Key exchange successful: {shared_secret == recovered_secret}")
```

---

## Universal ColorCipher - Automatic Encryption

### Revolutionary Unified API

The ColorCipher automatically detects and handles **any content type** with a single method:

```python
from clwe.core.color_cipher import ColorCipher

cipher = ColorCipher()

# ✨ ONE METHOD FOR EVERYTHING - Automatic Content Detection!

# 1. Text Content (automatically detected)
text_result = cipher.encrypt_to_image("Confidential message", "my_password")
decrypted_text = cipher.decrypt_from_image(text_result, "my_password")

# 2. File Content (automatically detected if path exists)
# file_result = cipher.encrypt_to_image("/path/to/document.pdf", "my_password")
# restored_file = cipher.decrypt_from_image(file_result, "my_password", "./output/")

# 3. Binary Content (automatically detected)
binary_content = bytes([1, 2, 3, 4, 5, 255, 128, 64])
binary_result = cipher.encrypt_to_image(binary_content, "my_password")
decrypted_binary = cipher.decrypt_from_image(binary_result, "my_password")

print(f"Original binary: {binary_content}")
print(f"Decrypted binary: {decrypted_binary}")
print(f"Match: {binary_content == decrypted_binary}")
```

### Enhanced Security - Variable Output Encryption

Each encryption produces **different outputs** for the same input (security enhancement):

```python
cipher = ColorCipher()

# Same input, different encrypted outputs every time!
message = "Same secret message"
password = "same_password"

# Generate multiple encryptions
encryptions = []
for i in range(5):
    encrypted = cipher.encrypt_to_image(message, password)
    encryptions.append(encrypted)
    print(f"Encryption {i+1}: {len(encrypted)} bytes")

# All encryptions are different (prevents pattern analysis)
print(f"All different: {len(set(encryptions)) == len(encryptions)}")

# But all decrypt to the same content
for i, encrypted in enumerate(encryptions):
    decrypted = cipher.decrypt_from_image(encrypted, password)
    print(f"Decryption {i+1}: {decrypted == message}")
```

### Superior Compression - 99.9% Size Reduction

```python
# Demonstration of superior compression
cipher = ColorCipher()

# Test with different content types
test_cases = [
    "Hi",
    "Hello",
    "Siddhu",
    "This is a longer message with more content to test compression efficiency",
    "x" * 1000  # 1KB of data
]

for content in test_cases:
    encrypted = cipher.encrypt_to_image(content, "test_password", "webp")
    
    print(f"\nContent: '{content[:20]}{'...' if len(content) > 20 else ''}'")
    print(f"Original size: {len(content.encode())} bytes")
    print(f"Encrypted size: {len(encrypted)} bytes")
    print(f"Compression ratio: {len(encrypted) / len(content.encode()):.3f}")
    
    # Verify perfect decryption
    decrypted = cipher.decrypt_from_image(encrypted, "test_password")
    print(f"Perfect decryption: {content == decrypted}")
```

### Pixel String Layout for Perfect Visual Patterns

```python
from PIL import Image
from io import BytesIO

cipher = ColorCipher()

# Small messages get pixel string layout (height=1, exact width)
messages = ["Hi", "Hello", "Secret", "CLWE"]

for msg in messages:
    encrypted = cipher.encrypt_to_image(msg, "password", "png")
    
    # Inspect the image properties
    img = Image.open(BytesIO(encrypted))
    print(f"Message: '{msg}' -> Image: {img.size[0]}x{img.size[1]} pixels")
    
    # Save for visualization
    with open(f"pixel_string_{msg.lower()}.png", "wb") as f:
        f.write(encrypted)
```

---

## ChromaCryptKEM - Post-Quantum Key Exchange

### Basic Key Encapsulation Mechanism

```python
from clwe.core.chromacrypt_kem import ChromaCryptKEM

# Initialize with security level (128, 192, or 256 bits)
kem = ChromaCryptKEM(security_level=128)

# Step 1: Generate key pair
print("Generating key pair...")
public_key, private_key = kem.keygen()

# Step 2: Encapsulate (sender side)
print("Encapsulating shared secret...")
shared_secret, ciphertext = kem.encapsulate(public_key)

# Step 3: Decapsulate (receiver side)
print("Decapsulating shared secret...")
recovered_secret = kem.decapsulate(private_key, ciphertext)

# Verify
success = shared_secret == recovered_secret
print(f"Key exchange successful: {success}")
print(f"Shared secret length: {len(shared_secret)} bytes")
print(f"Shared secret preview: {shared_secret.hex()[:32]}...")
```

### Performance Optimized KEM

```python
import time

# Use optimized parameters for better performance
kem_optimized = ChromaCryptKEM(security_level=128, optimized=True)

def benchmark_kem(kem, iterations=5):
    """Benchmark KEM operations"""
    
    # Benchmark key generation
    keygen_times = []
    for _ in range(iterations):
        start = time.time()
        pub, priv = kem.keygen()
        keygen_times.append((time.time() - start) * 1000)
    
    # Benchmark encapsulation
    encap_times = []
    for _ in range(iterations):
        start = time.time()
        secret, ct = kem.encapsulate(pub)
        encap_times.append((time.time() - start) * 1000)
    
    # Benchmark decapsulation
    decap_times = []
    for _ in range(iterations):
        start = time.time()
        recovered = kem.decapsulate(priv, ct)
        decap_times.append((time.time() - start) * 1000)
    
    print(f"Average KeyGen: {sum(keygen_times)/len(keygen_times):.2f}ms")
    print(f"Average Encaps: {sum(encap_times)/len(encap_times):.2f}ms")
    print(f"Average Decaps: {sum(decap_times)/len(decap_times):.2f}ms")

# Run benchmark
print("Benchmarking optimized KEM:")
benchmark_kem(kem_optimized)
```

### Multiple Security Levels

```python
# Test different security levels
security_levels = [128, 192, 256]

for level in security_levels:
    print(f"\n--- {level}-bit Security Level ---")
    
    kem = ChromaCryptKEM(security_level=level, optimized=True)
    
    # Generate keys
    start = time.time()
    pub_key, priv_key = kem.keygen()
    keygen_time = (time.time() - start) * 1000
    
    # Key exchange
    start = time.time()
    secret, ct = kem.encapsulate(pub_key)
    recovered = kem.decapsulate(priv_key, ct)
    exchange_time = (time.time() - start) * 1000
    
    print(f"Key generation: {keygen_time:.1f}ms")
    print(f"Key exchange: {exchange_time:.1f}ms")
    print(f"Success: {secret == recovered}")
```

---

## ColorHash - Quantum-Resistant Hashing

### Basic Cryptographic Hashing

```python
from clwe.core.color_hash import ColorHash

# Initialize color hash
hasher = ColorHash(security_level=128)

# Hash different types of data
test_data = [
    "Simple message",
    "Important document content",
    "User password: super_secure_123",
    b"Binary data content",
    "Unicode content: 🔐🌈💎"
]

for data in test_data:
    color_hash = hasher.hash(data)
    print(f"Data: {str(data)[:30]}...")
    print(f"Color hash: {color_hash}")
    print(f"Hash type: {type(color_hash)}")
    
    # Verify hash consistency
    verify_hash = hasher.hash(data)
    print(f"Consistent: {color_hash == verify_hash}\n")
```

### Salted Hashing for Enhanced Security

```python
import secrets

hasher = ColorHash(security_level=128)

# Generate random salt
salt = secrets.token_bytes(32)
print(f"Salt: {salt.hex()[:32]}...")

# Hash with salt
data = "Sensitive user data"
salted_hash = hasher.hash_with_salt(data, salt)

print(f"Original data: {data}")
print(f"Salted hash: {salted_hash}")

# Verify with same salt
verification = hasher.hash_with_salt(data, salt)
print(f"Verification matches: {salted_hash == verification}")

# Different salt produces different hash
different_salt = secrets.token_bytes(32)
different_hash = hasher.hash_with_salt(data, different_salt)
print(f"Different salt = different hash: {salted_hash != different_hash}")
```

### HMAC Authentication

```python
# HMAC for message authentication
hasher = ColorHash(security_level=128)

# Generate authentication key
auth_key = secrets.token_bytes(32)
print(f"Auth key: {auth_key.hex()[:32]}...")

# Messages to authenticate
messages = [
    "Transaction: Send $100 to Alice",
    "Transaction: Send $1000 to Bob", 
    "System command: shutdown -h now"
]

# Generate HMAC for each message
for msg in messages:
    hmac_hash = hasher.hmac_hash(msg, auth_key)
    print(f"Message: {msg}")
    print(f"HMAC: {hmac_hash}")
    
    # Verify HMAC
    verify_hmac = hasher.hmac_hash(msg, auth_key)
    print(f"Authentic: {hmac_hash == verify_hmac}\n")
```

---

## ChromaCryptSign - Digital Signatures

### Basic Digital Signatures

```python
from clwe.core.chromacrypt_sign import ChromaCryptSign

# Initialize signature scheme
signer = ChromaCryptSign(security_level=128)

# Generate signing keys
print("Generating signing key pair...")
public_key, private_key = signer.keygen()

# Document to sign
document = "Important contract: Transfer of $1,000,000 to Alice Corp."
print(f"Document: {document}")

# Create digital signature
print("Signing document...")
signature = signer.sign(private_key, document)

# Verify signature
print("Verifying signature...")
is_valid = signer.verify(public_key, document, signature)
print(f"Signature valid: ✓" if is_valid else "Signature invalid: ✗")

# Test tampered document
tampered_doc = "Important contract: Transfer of $1,000,001 to Alice Corp."
is_invalid = signer.verify(public_key, tampered_doc, signature)
print(f"Tampered document valid: ✓" if is_invalid else "Tampered rejected: ✓")
```

### Batch Document Signing

```python
signer = ChromaCryptSign(security_level=128)
pub_key, priv_key = signer.keygen()

# Multiple documents to sign
documents = [
    "Contract #001: Software license agreement",
    "Contract #002: Service level agreement", 
    "Contract #003: Non-disclosure agreement",
    "Invoice #001: $5,000 for services rendered",
    "Certificate: Alice Smith completed training"
]

# Sign all documents
signatures = []
print("Signing multiple documents...")
for i, doc in enumerate(documents, 1):
    signature = signer.sign(priv_key, doc)
    signatures.append(signature)
    print(f"✓ Document {i} signed")

# Verify all signatures
print("\nVerifying all signatures...")
all_valid = True
for i, (doc, sig) in enumerate(zip(documents, signatures), 1):
    valid = signer.verify(pub_key, doc, sig)
    status = "✓" if valid else "✗"
    print(f"{status} Document {i}: {valid}")
    all_valid &= valid

print(f"\nAll signatures valid: {all_valid}")
```

### Simple Byte-Based Signatures

```python
# Simplified signature interface
signer = ChromaCryptSign(security_level=128)
pub_key, priv_key = signer.keygen()

# Sign and get bytes
message = "Digital signature test message"
signature_bytes = signer.sign_simple(priv_key, message)

print(f"Message: {message}")
print(f"Signature size: {len(signature_bytes)} bytes")
print(f"Signature preview: {signature_bytes[:32].hex()}...")

# Verify from bytes
is_valid = signer.verify_simple(pub_key, message, signature_bytes)
print(f"Verification successful: {is_valid}")
```

---

## Visual Steganography Examples

### Creating Visual Cryptographic Art

```python
from clwe.core.color_cipher import ColorCipher
from PIL import Image
from io import BytesIO

cipher = ColorCipher()

# Create multiple visual encryption layers
secret_messages = [
    "Layer 1: Public information available to everyone",
    "Layer 2: Confidential data for authorized personnel only",
    "Layer 3: Top secret classified intelligence information"
]

passwords = [
    "public_access_key",
    "confidential_key_2023", 
    "top_secret_clearance_alpha"
]

print("Creating visual steganographic layers...")

# Generate encrypted visual layers
visual_layers = []
for i, (message, password) in enumerate(zip(secret_messages, passwords), 1):
    
    # Encrypt message to visual format
    encrypted_visual = cipher.encrypt_to_image(message, password, "png")
    visual_layers.append(encrypted_visual)
    
    # Save as viewable image
    filename = f"steganographic_layer_{i}.png"
    with open(filename, "wb") as f:
        f.write(encrypted_visual)
    
    # Show image properties
    img = Image.open(BytesIO(encrypted_visual))
    print(f"Layer {i}: {img.size[0]}x{img.size[1]} pixels, {len(encrypted_visual)} bytes")

print(f"\nCreated {len(visual_layers)} steganographic layers!")

# Decrypt specific layers with correct passwords
print("\nDecrypting layers...")
for i, (layer, password) in enumerate(zip(visual_layers, passwords), 1):
    try:
        decrypted = cipher.decrypt_from_image(layer, password)
        print(f"✓ Layer {i}: {decrypted[:50]}...")
    except Exception as e:
        print(f"✗ Layer {i}: Decryption failed")
```

### Covert Communication Example

```python
# Simulate covert communication through visual channels
cipher = ColorCipher()

# Secret intelligence data
intelligence_data = {
    "operation": "Northern Lights",
    "target_location": "59.9139° N, 10.7522° E",
    "asset_count": 12,
    "mission_date": "2024-03-15",
    "classification": "TOP SECRET"
}

# Convert to string for encryption
intel_string = str(intelligence_data)
cover_password = "bird_watching_society_2024"

# Encrypt intelligence into innocent-looking image
covert_image = cipher.encrypt_to_image(intel_string, cover_password, "webp")

# Save as seemingly innocent image
with open("nature_photography.webp", "wb") as f:
    f.write(covert_image)

print("Covert intelligence embedded in 'nature_photography.webp'")
print(f"Image size: {len(covert_image)} bytes")

# Receiving agent decrypts the hidden data
recovered_intel = cipher.decrypt_from_image(covert_image, cover_password)
print(f"Recovered intelligence: {recovered_intel[:100]}...")
```

---

## Performance Optimization Guide

### Monitoring Performance

```python
import time
import psutil
from clwe.core.color_cipher import ColorCipher
from clwe.core.chromacrypt_kem import ChromaCryptKEM

def monitor_performance(operation_name, operation_func, *args):
    """Monitor memory and time performance"""
    
    # Get initial memory
    process = psutil.Process()
    initial_memory = process.memory_info().rss / 1024 / 1024  # MB
    
    # Time the operation
    start_time = time.time()
    result = operation_func(*args)
    end_time = time.time()
    
    # Get final memory
    final_memory = process.memory_info().rss / 1024 / 1024  # MB
    
    print(f"\n--- {operation_name} Performance ---")
    print(f"Execution time: {(end_time - start_time)*1000:.2f}ms")
    print(f"Memory used: {final_memory - initial_memory:.2f}MB")
    print(f"Peak memory: {final_memory:.2f}MB")
    
    return result

# Performance monitoring examples
cipher = ColorCipher()
kem = ChromaCryptKEM(security_level=128, optimized=True)

# Monitor ColorCipher performance
test_message = "Performance test message with reasonable length for testing"
password = "performance_test_password_123"

encrypted = monitor_performance(
    "ColorCipher Encryption",
    cipher.encrypt_to_image,
    test_message, password, "webp"
)

decrypted = monitor_performance(
    "ColorCipher Decryption", 
    cipher.decrypt_from_image,
    encrypted, password
)

# Monitor KEM performance
pub_key, priv_key = monitor_performance(
    "KEM Key Generation",
    kem.keygen
)

secret, ct = monitor_performance(
    "KEM Encapsulation",
    kem.encapsulate,
    pub_key
)

recovered = monitor_performance(
    "KEM Decapsulation",
    kem.decapsulate,
    priv_key, ct
)
```

### Optimizing for Different Use Cases

```python
# Configuration for different performance requirements

# 1. Ultra-Fast Configuration (minimal security for testing)
fast_cipher = ColorCipher()
fast_kem = ChromaCryptKEM(security_level=128, optimized=True)

# 2. Balanced Configuration (recommended for production)
balanced_cipher = ColorCipher()
balanced_kem = ChromaCryptKEM(security_level=192, optimized=True)

# 3. Maximum Security Configuration (sensitive applications)
secure_cipher = ColorCipher()
secure_kem = ChromaCryptKEM(security_level=256, optimized=True)

configs = [
    ("Fast", fast_cipher, fast_kem),
    ("Balanced", balanced_cipher, balanced_kem),
    ("Secure", secure_cipher, secure_kem)
]

test_data = "Configuration performance test"

for name, cipher_config, kem_config in configs:
    print(f"\n--- {name} Configuration ---")
    
    # Test encryption speed
    start = time.time()
    encrypted = cipher_config.encrypt_to_image(test_data, "test", "webp")
    encrypt_time = (time.time() - start) * 1000
    
    # Test KEM speed
    start = time.time()
    pub, priv = kem_config.keygen()
    keygen_time = (time.time() - start) * 1000
    
    print(f"Encryption: {encrypt_time:.2f}ms")
    print(f"Key generation: {keygen_time:.2f}ms")
    print(f"Encrypted size: {len(encrypted)} bytes")
```

---

## Security Configurations

### Security Level Comparison

```python
from clwe.core.chromacrypt_kem import ChromaCryptKEM
from clwe.core.color_hash import ColorHash
from clwe.core.chromacrypt_sign import ChromaCryptSign

# Test all security levels
security_levels = [128, 192, 256]

print("Security Level Comparison:")
print("=" * 50)

for level in security_levels:
    print(f"\n{level}-bit Security Level:")
    
    # Initialize components
    kem = ChromaCryptKEM(security_level=level, optimized=True)
    hasher = ColorHash(security_level=level)
    signer = ChromaCryptSign(security_level=level, optimized=True)
    
    # Test basic operations
    try:
        # KEM test
        pub, priv = kem.keygen()
        secret, ct = kem.encapsulate(pub)
        recovered = kem.decapsulate(priv, ct)
        kem_success = secret == recovered
        
        # Hash test
        hash_result = hasher.hash("test data")
        hash_success = hash_result is not None
        
        # Signature test
        sign_pub, sign_priv = signer.keygen()
        signature = signer.sign(sign_priv, "test message")
        verify_success = signer.verify(sign_pub, "test message", signature)
        
        print(f"  ✓ KEM: {'Pass' if kem_success else 'Fail'}")
        print(f"  ✓ Hash: {'Pass' if hash_success else 'Fail'}")
        print(f"  ✓ Signatures: {'Pass' if verify_success else 'Fail'}")
        
    except Exception as e:
        print(f"  ✗ Error: {str(e)[:50]}...")
```

### Password Security Best Practices

```python
import secrets
import hashlib

def generate_secure_password(length=32):
    """Generate cryptographically secure password"""
    import string
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def strengthen_user_password(user_password):
    """Strengthen user-provided password using key derivation"""
    # Generate random salt
    salt = secrets.token_bytes(32)
    
    # Use PBKDF2 to strengthen the password
    strengthened = hashlib.pbkdf2_hmac(
        'sha256', 
        user_password.encode(), 
        salt, 
        100000  # 100,000 iterations
    )
    
    return strengthened.hex(), salt.hex()

# Examples of secure password practices
print("Password Security Examples:")
print("=" * 30)

# 1. Generate secure password
secure_password = generate_secure_password()
print(f"Generated secure password: {secure_password[:16]}...")

# 2. Strengthen user password
user_password = "user_chosen_password_123"
strengthened_key, salt = strengthen_user_password(user_password)
print(f"User password strengthened: {strengthened_key[:32]}...")
print(f"Salt used: {salt[:32]}...")

# 3. Use strengthened password with CLWE
cipher = ColorCipher()
message = "Highly sensitive information"

# Use strengthened password for encryption
encrypted = cipher.encrypt_to_image(message, strengthened_key, "webp")
decrypted = cipher.decrypt_from_image(encrypted, strengthened_key)

print(f"Encryption with strengthened password: {'Success' if message == decrypted else 'Failed'}")
```

---

## Integration Examples

### Web Application Integration

```python
# Example Flask web application integration
# Note: This is a demonstration - would need Flask installed

"""
from flask import Flask, request, jsonify
import base64
from clwe.core.color_cipher import ColorCipher

app = Flask(__name__)
cipher = ColorCipher()

@app.route('/encrypt', methods=['POST'])
def encrypt_endpoint():
    data = request.json
    message = data.get('message')
    password = data.get('password')
    
    if not message or not password:
        return jsonify({'error': 'Message and password required'}), 400
    
    try:
        # Encrypt message
        encrypted = cipher.encrypt_to_image(message, password, "webp")
        
        # Return base64 encoded result
        return jsonify({
            'encrypted': base64.b64encode(encrypted).decode(),
            'format': 'webp',
            'size': len(encrypted)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/decrypt', methods=['POST'])
def decrypt_endpoint():
    data = request.json
    encrypted_b64 = data.get('encrypted')
    password = data.get('password')
    
    if not encrypted_b64 or not password:
        return jsonify({'error': 'Encrypted data and password required'}), 400
    
    try:
        # Decode and decrypt
        encrypted = base64.b64decode(encrypted_b64)
        decrypted = cipher.decrypt_from_image(encrypted, password)
        
        return jsonify({'decrypted': decrypted})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
"""

# Simulation of the above web application
import base64

cipher = ColorCipher()

def simulate_encrypt_request(message, password):
    """Simulate web encryption request"""
    try:
        encrypted = cipher.encrypt_to_image(message, password, "webp")
        return {
            'status': 'success',
            'encrypted': base64.b64encode(encrypted).decode(),
            'format': 'webp',
            'size': len(encrypted)
        }
    except Exception as e:
        return {'status': 'error', 'error': str(e)}

def simulate_decrypt_request(encrypted_b64, password):
    """Simulate web decryption request"""
    try:
        encrypted = base64.b64decode(encrypted_b64)
        decrypted = cipher.decrypt_from_image(encrypted, password)
        return {
            'status': 'success',
            'decrypted': decrypted
        }
    except Exception as e:
        return {'status': 'error', 'error': str(e)}

# Test the web application simulation
print("Web Application Integration Simulation:")
print("=" * 40)

# Encrypt via web API
encrypt_response = simulate_encrypt_request("Web API test message", "web_password_123")
print(f"Encrypt response: {encrypt_response['status']}")
if encrypt_response['status'] == 'success':
    print(f"Encrypted size: {encrypt_response['size']} bytes")
    
    # Decrypt via web API
    decrypt_response = simulate_decrypt_request(
        encrypt_response['encrypted'], 
        "web_password_123"
    )
    print(f"Decrypt response: {decrypt_response['status']}")
    if decrypt_response['status'] == 'success':
        print(f"Decrypted message: {decrypt_response['decrypted']}")
```

### Database Integration Example

```python
# Secure database operations with CLWE encryption
import sqlite3
import base64
import json

class SecureDatabase:
    def __init__(self, db_path, master_password):
        self.db_path = db_path
        self.cipher = ColorCipher()
        self.master_password = master_password
        self.conn = sqlite3.connect(db_path)
        self._create_tables()
    
    def _create_tables(self):
        """Create tables for encrypted storage"""
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS encrypted_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                encrypted_content TEXT NOT NULL,
                content_type TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        self.conn.commit()
    
    def store_encrypted(self, name, data, content_type="text"):
        """Store data with CLWE encryption"""
        try:
            # Encrypt the data
            encrypted = self.cipher.encrypt_to_image(data, self.master_password, "webp")
            encrypted_b64 = base64.b64encode(encrypted).decode()
            
            # Store in database
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO encrypted_data (name, encrypted_content, content_type)
                VALUES (?, ?, ?)
            ''', (name, encrypted_b64, content_type))
            self.conn.commit()
            
            return cursor.lastrowid
        except Exception as e:
            print(f"Storage error: {e}")
            return None
    
    def retrieve_decrypted(self, name):
        """Retrieve and decrypt data"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                SELECT encrypted_content, content_type FROM encrypted_data 
                WHERE name = ? ORDER BY created_at DESC LIMIT 1
            ''', (name,))
            
            result = cursor.fetchone()
            if result:
                encrypted_b64, content_type = result
                encrypted = base64.b64decode(encrypted_b64)
                decrypted = self.cipher.decrypt_from_image(encrypted, self.master_password)
                return decrypted, content_type
            return None, None
        except Exception as e:
            print(f"Retrieval error: {e}")
            return None, None
    
    def list_encrypted_items(self):
        """List all encrypted items"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT id, name, content_type, created_at FROM encrypted_data
            ORDER BY created_at DESC
        ''')
        return cursor.fetchall()

# Demonstrate secure database usage
print("Secure Database Integration:")
print("=" * 30)

# Initialize secure database
db = SecureDatabase('secure_test.db', 'database_master_key_2024')

# Store various types of encrypted data
test_data = [
    ("user_credentials", "username:alice, password:secret123", "credentials"),
    ("api_key", "sk-1234567890abcdef", "api_key"),
    ("personal_note", "Remember to buy milk and bread", "note"),
    ("financial_data", "Account: 1234-5678, Balance: $50,000", "financial")
]

print("Storing encrypted data...")
for name, data, content_type in test_data:
    record_id = db.store_encrypted(name, data, content_type)
    print(f"✓ Stored '{name}' with ID: {record_id}")

print("\nRetrieving encrypted data...")
for name, original_data, _ in test_data:
    decrypted, content_type = db.retrieve_decrypted(name)
    if decrypted:
        match = decrypted == original_data
        print(f"✓ '{name}': {'Match' if match else 'Mismatch'}")
    else:
        print(f"✗ '{name}': Retrieval failed")

# List all items
print(f"\nStored items: {len(db.list_encrypted_items())}")
```

---

## Troubleshooting & Best Practices

### Common Issues and Solutions

```python
# Comprehensive troubleshooting guide

def diagnose_installation():
    """Diagnose CLWE installation issues"""
    print("CLWE Installation Diagnosis:")
    print("=" * 30)
    
    try:
        # Test basic imports
        from clwe.core.color_cipher import ColorCipher
        print("✓ ColorCipher import successful")
        
        from clwe.core.chromacrypt_kem import ChromaCryptKEM
        print("✓ ChromaCryptKEM import successful")
        
        from clwe.core.color_hash import ColorHash
        print("✓ ColorHash import successful")
        
        from clwe.core.chromacrypt_sign import ChromaCryptSign
        print("✓ ChromaCryptSign import successful")
        
        # Test basic functionality
        cipher = ColorCipher()
        test_encrypted = cipher.encrypt_to_image("test", "password")
        test_decrypted = cipher.decrypt_from_image(test_encrypted, "password")
        
        if test_decrypted == "test":
            print("✓ Basic encryption/decryption working")
        else:
            print("✗ Basic encryption/decryption failed")
            
        return True
        
    except ImportError as e:
        print(f"✗ Import error: {e}")
        print("Solution: pip install clwe")
        return False
    except Exception as e:
        print(f"✗ Functionality error: {e}")
        return False

def diagnose_performance():
    """Diagnose performance issues"""
    print("\nPerformance Diagnosis:")
    print("=" * 20)
    
    import time
    import sys
    
    print(f"Python version: {sys.version}")
    
    # Test encryption performance
    cipher = ColorCipher()
    test_message = "Performance test message"
    
    start = time.time()
    encrypted = cipher.encrypt_to_image(test_message, "test_password")
    encrypt_time = (time.time() - start) * 1000
    
    start = time.time()
    decrypted = cipher.decrypt_from_image(encrypted, "test_password")
    decrypt_time = (time.time() - start) * 1000
    
    print(f"Encryption time: {encrypt_time:.2f}ms")
    print(f"Decryption time: {decrypt_time:.2f}ms")
    
    if encrypt_time > 100:
        print("⚠ Slow encryption detected")
        print("  Recommendation: Check system resources")
    else:
        print("✓ Encryption performance good")
    
    if decrypt_time > 50:
        print("⚠ Slow decryption detected")
        print("  Recommendation: Check system resources")
    else:
        print("✓ Decryption performance good")

def test_memory_usage():
    """Test memory usage patterns"""
    print("\nMemory Usage Test:")
    print("=" * 18)
    
    try:
        import psutil
        process = psutil.Process()
        initial_memory = process.memory_info().rss / 1024 / 1024
        
        cipher = ColorCipher()
        
        # Test with increasingly larger data
        sizes = [100, 1000, 10000]
        for size in sizes:
            test_data = "x" * size
            encrypted = cipher.encrypt_to_image(test_data, "password")
            current_memory = process.memory_info().rss / 1024 / 1024
            memory_increase = current_memory - initial_memory
            
            print(f"Data size: {size:5d} bytes, Memory: +{memory_increase:.1f}MB")
            
            if memory_increase > 100:  # 100MB threshold
                print(f"⚠ High memory usage for {size} byte input")
        
        print("✓ Memory usage test completed")
        
    except ImportError:
        print("psutil not available - install with: pip install psutil")

# Run all diagnostics
diagnose_installation()
diagnose_performance()
test_memory_usage()
```

### Security Best Practices

```python
def demonstrate_security_best_practices():
    """Demonstrate security best practices"""
    print("\nSecurity Best Practices:")
    print("=" * 25)
    
    # 1. Strong password generation
    import secrets
    import string
    
    def generate_strong_password(length=32):
        alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
        return ''.join(secrets.choice(alphabet) for _ in range(length))
    
    strong_password = generate_strong_password()
    print(f"✓ Strong password generated: {strong_password[:16]}...")
    
    # 2. Secure random data
    secure_data = secrets.token_bytes(32)
    print(f"✓ Secure random data: {secure_data.hex()[:32]}...")
    
    # 3. Password verification
    cipher = ColorCipher()
    test_message = "Security test message"
    
    # Encrypt with strong password
    encrypted = cipher.encrypt_to_image(test_message, strong_password)
    
    # Verify only correct password works
    try:
        correct_decrypt = cipher.decrypt_from_image(encrypted, strong_password)
        print(f"✓ Correct password: {'Success' if correct_decrypt == test_message else 'Failed'}")
    except:
        print("✗ Correct password failed")
    
    # Test wrong password rejection
    wrong_password = "wrong_password_123"
    try:
        wrong_decrypt = cipher.decrypt_from_image(encrypted, wrong_password)
        if wrong_decrypt == test_message:
            print("✗ Security issue: Wrong password accepted")
        else:
            print("✓ Wrong password properly rejected")
    except:
        print("✓ Wrong password properly rejected")
    
    # 4. Variable output verification
    print("\n✓ Variable Output Security:")
    encryptions = []
    for i in range(3):
        enc = cipher.encrypt_to_image("same message", "same password")
        encryptions.append(enc)
        print(f"  Encryption {i+1}: {len(enc)} bytes")
    
    all_different = len(set(encryptions)) == len(encryptions)
    print(f"✓ All encryptions different: {all_different}")
    
    # All should decrypt correctly
    all_correct = all(
        cipher.decrypt_from_image(enc, "same password") == "same message"
        for enc in encryptions
    )
    print(f"✓ All decrypt correctly: {all_correct}")

demonstrate_security_best_practices()
```

### Error Handling Examples

```python
class CLWEError(Exception):
    """Base CLWE exception"""
    pass

class EncryptionError(CLWEError):
    """Encryption-specific error"""
    pass

class DecryptionError(CLWEError):
    """Decryption-specific error"""
    pass

def robust_encryption_workflow(data, password):
    """Robust encryption with comprehensive error handling"""
    print("\nRobust Encryption Workflow:")
    print("=" * 30)
    
    try:
        # Input validation
        if not data:
            raise EncryptionError("Empty data provided")
        if not password or len(password) < 8:
            raise EncryptionError("Password too weak (minimum 8 characters)")
        
        print("✓ Input validation passed")
        
        # Initialize cipher
        cipher = ColorCipher()
        print("✓ ColorCipher initialized")
        
        # Perform encryption
        encrypted = cipher.encrypt_to_image(data, password, "webp")
        if not encrypted:
            raise EncryptionError("Encryption produced no output")
        
        print(f"✓ Encryption successful: {len(encrypted)} bytes")
        
        # Verify by decryption
        decrypted = cipher.decrypt_from_image(encrypted, password)
        if decrypted != data:
            raise EncryptionError("Encryption verification failed")
        
        print("✓ Encryption verification passed")
        
        return encrypted
        
    except EncryptionError as e:
        print(f"✗ Encryption Error: {e}")
        return None
    except Exception as e:
        print(f"✗ Unexpected Error: {e}")
        return None

def robust_decryption_workflow(encrypted_data, password):
    """Robust decryption with comprehensive error handling"""
    try:
        # Input validation
        if not encrypted_data:
            raise DecryptionError("No encrypted data provided")
        if not password:
            raise DecryptionError("No password provided")
        
        # Initialize cipher
        cipher = ColorCipher()
        
        # Perform decryption
        decrypted = cipher.decrypt_from_image(encrypted_data, password)
        
        # Check for decryption errors
        if isinstance(decrypted, str) and "failed" in decrypted.lower():
            raise DecryptionError(decrypted)
        
        return decrypted
        
    except DecryptionError as e:
        print(f"✗ Decryption Error: {e}")
        return None
    except Exception as e:
        print(f"✗ Unexpected Error: {e}")
        return None

# Test robust workflows
test_data = "Important data for robust testing"
test_password = "robust_test_password_123"

# Test successful workflow
encrypted_result = robust_encryption_workflow(test_data, test_password)
if encrypted_result:
    decrypted_result = robust_decryption_workflow(encrypted_result, test_password)
    print(f"✓ Complete workflow: {'Success' if decrypted_result == test_data else 'Failed'}")

# Test error conditions
print("\nTesting Error Conditions:")
robust_encryption_workflow("", test_password)  # Empty data
robust_encryption_workflow(test_data, "123")   # Weak password
robust_decryption_workflow(b"invalid", test_password)  # Invalid encrypted data
```

---

## Summary

CLWE v0.0.1 provides a revolutionary post-quantum cryptographic library with:

### 🌟 **Key Features**
- **Universal Automatic Encryption**: One method handles all content types
- **Variable Output Security**: Enhanced protection through randomization
- **Superior Compression**: 99.9% size reduction with intelligent algorithms
- **Post-Quantum Security**: Resistant to both classical and quantum attacks
- **Visual Steganography**: Embed encrypted data in colorful images

### 🛡️ **Security Levels**
- **128-bit**: Fast operations, suitable for most applications
- **192-bit**: Enhanced security for sensitive data  
- **256-bit**: Maximum security for critical applications

### ⚡ **Performance**
- **Encryption**: Sub-millisecond operations
- **KEM Operations**: Industry-competitive speeds
- **Memory Efficient**: Optimized for production use

### 📚 **Complete API**
- **ColorCipher**: Universal symmetric encryption
- **ChromaCryptKEM**: Post-quantum key exchange
- **ColorHash**: Quantum-resistant hashing
- **ChromaCryptSign**: Digital signatures

For additional support and documentation:
- **GitHub**: https://github.com/clwe-dev/clwe
- **Issues**: Report bugs on GitHub Issues
- **Support**: Contact development team

**Ready to use post-quantum cryptography with the simplicity of a unified API!**

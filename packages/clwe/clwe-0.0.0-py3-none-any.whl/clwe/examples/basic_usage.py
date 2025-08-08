import clwe

def basic_kem_example():
    print("CLWE Key Encapsulation Mechanism Example")
    print("-" * 40)
    
    kem = clwe.ChromaCryptKEM(security_level=128)
    
    print("Generating key pair...")
    public_key, private_key = kem.keygen()
    
    print("Encapsulating shared secret...")
    shared_secret, ciphertext = kem.encapsulate(public_key)
    
    print("Decapsulating shared secret...")
    recovered_secret = kem.decapsulate(private_key, ciphertext)
    
    success = shared_secret == recovered_secret
    print(f"Success: {success}")
    print(f"Shared secret: {shared_secret.hex()[:32]}...")
    
    return success

def basic_visual_example():
    print("CLWE Visual Encryption Example")
    print("-" * 32)
    
    cipher = clwe.ColorCipher()
    
    message = "Hello, CLWE!"
    password = "secure_password"
    
    print(f"Original message: {message}")
    
    print("Encrypting to visual pattern...")
    encrypted = cipher.encrypt(message, password)
    
    print("Decrypting from visual pattern...")
    decrypted = cipher.decrypt(encrypted, password)
    
    success = message == decrypted
    print(f"Success: {success}")
    print(f"Decrypted message: {decrypted}")
    
    return success

def basic_hash_example():
    print("CLWE Color Hash Example")
    print("-" * 24)
    
    hasher = clwe.ColorHash()
    
    data = "Important data to hash"
    print(f"Data: {data}")
    
    print("Computing color hash...")
    color_hash = hasher.hash(data)
    
    print(f"Color hash: {color_hash}")
    
    print("Verifying hash...")
    is_valid = hasher.verify(data, color_hash)
    
    print(f"Hash verification: {is_valid}")
    
    return is_valid

def basic_signature_example():
    print("CLWE Digital Signature Example")
    print("-" * 32)
    
    signer = clwe.ChromaCryptSign(security_level=128)
    
    print("Generating signing key pair...")
    public_key, private_key = signer.keygen()
    
    message = "Document to sign"
    print(f"Message: {message}")
    
    print("Signing message...")
    signature = signer.sign(private_key, message)
    
    print("Verifying signature...")
    is_valid = signer.verify(public_key, message, signature)
    
    print(f"Signature valid: {is_valid}")
    
    return is_valid

if __name__ == "__main__":
    print("CLWE Basic Usage Examples")
    print("=" * 40)
    
    basic_kem_example()
    print()
    basic_visual_example()
    print()
    basic_hash_example()
    print()
    basic_signature_example()
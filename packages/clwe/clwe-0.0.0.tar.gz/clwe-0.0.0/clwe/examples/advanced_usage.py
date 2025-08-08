import clwe
from clwe.core.batch_operations import batch_color_processor
from clwe.core.hardware_acceleration import hardware_manager
from clwe.core.side_channel_protection import side_channel_protection

def advanced_batch_example():
    print("Advanced Batch Processing Example")
    print("-" * 35)
    
    messages = [
        "First confidential message",
        "Second encrypted content", 
        "Third secure communication"
    ]
    
    passwords = [
        "password1",
        "password2",
        "password3"
    ]
    
    print(f"Processing {len(messages)} messages in batch...")
    
    encrypted_batch = batch_color_processor.batch_color_encryption(messages, passwords)
    print("Batch encryption completed")
    
    decrypted_batch = batch_color_processor.batch_color_decryption(encrypted_batch, passwords)
    print("Batch decryption completed")
    
    success = all(orig == decr for orig, decr in zip(messages, decrypted_batch))
    print(f"Batch processing success: {success}")
    
    return success

def advanced_security_example():
    print("Advanced Security Features Example")
    print("-" * 36)
    
    print("Hardware acceleration status:")
    perf_summary = hardware_manager.get_performance_summary()
    print(f"  CPU cores: {perf_summary['cpu_cores']}")
    print(f"  SIMD width: {perf_summary['simd_width']}")
    print(f"  Available methods: {', '.join(perf_summary['acceleration_methods'])}")
    
    print("\nSide-channel protection:")
    protection_metrics = side_channel_protection.get_protection_metrics()
    print(f"  Active protections: {len(protection_metrics['total_protection_features'])}")
    print(f"  Security level: {side_channel_protection.security_level}")
    
    print("\nParameter security validation:")
    validation = side_channel_protection.validate_security_hardness(256, 3329, 2)
    print(f"  128-bit security: {validation['meets_128bit_security']}")
    print(f"  Estimated security: {validation['estimated_security_bits']:.1f} bits")
    print(f"  Production ready: {validation['recommended_for_production']}")
    
    return True

def advanced_performance_example():
    print("Advanced Performance Optimization Example")
    print("-" * 42)
    
    from clwe.utils.performance import PerformanceProfiler
    
    profiler = PerformanceProfiler()
    
    kem = clwe.ChromaCryptKEM(128, optimized=True)
    
    print("Profiling key generation...")
    public_key, private_key = profiler.measure("keygen", kem.keygen)
    
    print("Profiling encapsulation...")
    shared_secret, ciphertext = profiler.measure("encapsulate", kem.encapsulate, public_key)
    
    print("Profiling decapsulation...")
    recovered_secret = profiler.measure("decapsulate", kem.decapsulate, private_key, ciphertext)
    
    summary = profiler.get_summary()
    print("\nPerformance Summary:")
    for operation, metrics in summary.items():
        print(f"  {operation}: {metrics['wall_time_ms']:.2f}ms")
    
    return shared_secret == recovered_secret

def advanced_multiformat_example():
    print("Advanced Multi-Format Encryption Example")
    print("-" * 40)
    
    cipher = clwe.ColorCipher()
    
    message = "Multi-format encryption test"
    password = "advanced_password"
    
    print("String encryption:")
    encrypted_dict = cipher.encrypt(message, password)
    decrypted_string = cipher.decrypt(encrypted_dict, password)
    print(f"  Success: {message == decrypted_string}")
    
    print("Image encryption:")
    encrypted_image = cipher.encrypt_to_image(message, password, "png")
    decrypted_from_image = cipher.decrypt_from_image(encrypted_image, password)
    print(f"  Success: {message == decrypted_from_image}")
    
    print("File encryption:")
    file_data = message.encode('utf-8')
    encrypted_file = cipher.encrypt_file(file_data, password)
    decrypted_file = cipher.decrypt_file(encrypted_file, password)
    print(f"  Success: {file_data == decrypted_file}")
    
    return True

if __name__ == "__main__":
    print("CLWE Advanced Usage Examples")
    print("=" * 42)
    
    advanced_batch_example()
    print()
    advanced_security_example()
    print()
    advanced_performance_example()
    print()
    advanced_multiformat_example()
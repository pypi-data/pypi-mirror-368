#!/usr/bin/env python3
"""
Document Signing Demo - CLWE v0.0.1
Demonstrates the new document signing capabilities for PDFs and other documents
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

import clwe
from clwe.core.document_signer import DocumentSigner, DocumentVerificationReport
from clwe.core.chromacrypt_sign import ChromaCryptSign
import json
import tempfile

def demo_basic_document_signing():
    """Demonstrate basic document signing and verification"""
    print("Basic Document Signing Demo")
    print("=" * 40)
    
    # Initialize the document signer
    doc_signer = DocumentSigner(security_level=128)
    
    # Generate keys
    print("1. Generating signing keys...")
    public_key, private_key = doc_signer.chromacrypt_signer.keygen()
    print("   Keys generated successfully!")
    print()
    
    # Document to sign
    document_content = """
    This is a sample document that we want to sign using CLWE technology.
    
    Document Contents:
    - Important financial data
    - Contract terms and conditions
    - Legal agreements
    
    Signed on: 2025-01-01
    """
    
    print("2. Signing document...")
    print(f"   Document preview: {document_content[:100]}...")
    
    # Sign the document
    signature_package = doc_signer.sign_document(
        document_content, 
        private_key,
        document_type="contract",
        metadata={
            "author": "John Doe",
            "department": "Legal",
            "contract_id": "CTR-2025-001"
        }
    )
    
    print("   Document signed successfully!")
    print(f"   Signature algorithm: {signature_package['verification_data']['algorithm']}")
    print(f"   Signer ID: {signature_package['verification_data']['signer_id']}")
    print()
    
    # Verify the document
    print("3. Verifying document signature...")
    verification_result = doc_signer.verify_document(
        document_content,
        signature_package,
        public_key
    )
    
    if verification_result["valid"]:
        print("   ✓ Signature verification PASSED")
        print("   Document integrity confirmed")
    else:
        print("   ✗ Signature verification FAILED")
        print(f"   Reason: {verification_result['reason']}")
    print()
    
    # Test with modified document
    print("4. Testing with modified document...")
    modified_document = document_content + "\n[MODIFIED] This line was added after signing!"
    
    modified_verification = doc_signer.verify_document(
        modified_document,
        signature_package,
        public_key
    )
    
    if modified_verification["valid"]:
        print("   ✗ Unexpected: Modified document verified (this should not happen)")
    else:
        print("   ✓ Modified document correctly rejected")
        print(f"   Reason: {modified_verification['reason']}")
    print()
    
    return signature_package, public_key, private_key

def demo_file_signing():
    """Demonstrate signing actual files"""
    print("File Signing Demo")
    print("=" * 25)
    
    doc_signer = DocumentSigner(security_level=128)
    public_key, private_key = doc_signer.chromacrypt_signer.keygen()
    
    # Create temporary files for testing
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        test_content = """
Sample Contract Document
=======================

Party A: ACME Corporation
Party B: XYZ Industries

Terms:
1. Delivery within 30 days
2. Payment within 60 days
3. Quality assurance required

This contract is legally binding.
        """
        f.write(test_content)
        temp_file_path = f.name
    
    try:
        print(f"1. Signing text file: {os.path.basename(temp_file_path)}")
        
        # Sign the text file
        signature_package = doc_signer.sign_text_document(
            temp_file_path,
            private_key,
            metadata={
                "contract_type": "Supply Agreement",
                "parties": ["ACME Corporation", "XYZ Industries"],
                "value": 50000
            }
        )
        
        print("   File signed successfully!")
        print()
        
        # Create signature certificate
        cert_path = temp_file_path + ".sig"
        doc_signer.create_signature_certificate(signature_package, cert_path)
        print(f"2. Signature certificate created: {os.path.basename(cert_path)}")
        print()
        
        # Verify by reading the file again
        print("3. Verifying signed file...")
        with open(temp_file_path, 'r') as f:
            file_content = f.read()
        
        verification_result = doc_signer.verify_document(
            file_content,
            signature_package,
            public_key
        )
        
        # Generate detailed report
        report = DocumentVerificationReport.generate_report(verification_result, signature_package)
        print("   Verification Report:")
        print("   " + report.replace('\n', '\n   '))
        
    finally:
        # Clean up temporary files
        if os.path.exists(temp_file_path):
            os.unlink(temp_file_path)
        if 'cert_path' in locals() and os.path.exists(cert_path):
            os.unlink(cert_path)

def demo_color_signature_features():
    """Demonstrate the color signature features"""
    print("Color Signature Features Demo")
    print("=" * 35)
    
    doc_signer = DocumentSigner(security_level=128)
    
    document = "Contract for software development services"
    
    # Show color signature generation
    print("1. Generating color signature...")
    color_sig = doc_signer.color_hash.hash_pattern(document, num_colors=6, pattern_type="dynamic")
    
    print(f"   Selected pattern: {color_sig['pattern_type']}")
    print("   Color signature:")
    for i, color in enumerate(color_sig['colors']):
        print(f"     Color {i+1}: RGB{color}")
    print()
    
    print("2. All available patterns for this document:")
    for pattern_name, colors in color_sig['all_patterns'].items():
        print(f"   {pattern_name.capitalize()}: {colors[:2]}...")  # First 2 colors
    print()
    
    print("3. Color signature metadata:")
    metadata = color_sig['hash_metadata']
    for key, value in metadata.items():
        print(f"   {key}: {value}")

def demo_advanced_features():
    """Demonstrate advanced signing features"""
    print("Advanced Features Demo")
    print("=" * 30)
    
    doc_signer = DocumentSigner(security_level=256)  # Higher security
    public_key, private_key = doc_signer.chromacrypt_signer.keygen()
    
    # Complex document with metadata
    document = {
        "type": "financial_report",
        "data": "Q4 2024 Financial Results: Revenue $10M, Profit $2M",
        "classification": "confidential"
    }
    
    document_json = json.dumps(document, sort_keys=True)
    
    print("1. Signing complex JSON document...")
    signature_package = doc_signer.sign_document(
        document_json,
        private_key,
        document_type="json",
        metadata={
            "classification": "confidential",
            "department": "Finance",
            "approval_level": "C-level",
            "retention_period": "7_years"
        }
    )
    
    print("   Complex document signed with enhanced metadata")
    print()
    
    print("2. Signature package structure:")
    structure = {
        "signature_version": signature_package["signature_version"],
        "verification_data_keys": list(signature_package["verification_data"].keys()),
        "document_signature_keys": list(signature_package["document_signature"].keys()),
        "security_layers": list(signature_package["document_signature"]["security_layers"].keys())
    }
    
    for key, value in structure.items():
        print(f"   {key}: {value}")
    print()
    
    print("3. Verification with detailed analysis...")
    verification = doc_signer.verify_document(document_json, signature_package, public_key)
    
    if verification["valid"]:
        details = verification["verification_details"]
        print("   ✓ Advanced verification successful")
        print(f"   Color verification: {details['color_verification']}")
        print(f"   Timestamp: {details['signature_timestamp']}")
    else:
        print(f"   ✗ Verification failed: {verification['reason']}")

def main():
    """Main demo function"""
    print("CLWE Document Signing Technology Demonstration")
    print("=" * 55)
    print("Real-world document signing using post-quantum cryptography")
    print()
    
    try:
        # Run all demos
        demo_basic_document_signing()
        print("\n" + "="*60 + "\n")
        
        demo_file_signing()
        print("\n" + "="*60 + "\n")
        
        demo_color_signature_features()
        print("\n" + "="*60 + "\n")
        
        demo_advanced_features()
        
        print("\n" + "="*60)
        print("DEMONSTRATION COMPLETED SUCCESSFULLY!")
        print("\nCLWE Document Signing Features:")
        print("✓ Post-quantum cryptographic signatures")
        print("✓ Multi-color visual verification")
        print("✓ Comprehensive metadata support")
        print("✓ PDF and document file support")
        print("✓ Security layer validation")
        print("✓ Detailed verification reports")
        print("✓ Real-world document integrity protection")
        
    except Exception as e:
        print(f"Error during demonstration: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
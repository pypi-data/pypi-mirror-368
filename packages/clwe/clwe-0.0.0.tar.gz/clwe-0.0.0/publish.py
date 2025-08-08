#!/usr/bin/env python3

import subprocess
import sys
import os
import getpass

def run_command(cmd, description):
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, check=True)
        print(f"✅ {description}: SUCCESS")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description}: FAILED")
        return False

def main():
    print("🚀 CLWE v0.0.1 Publishing Script")
    print("=" * 40)
    
    # Check if dist files exist
    if not os.path.exists("dist") or not os.listdir("dist"):
        print("❌ No distribution files found!")
        print("Please run build.py first")
        return False
    
    print("📦 Distribution files:")
    for file in os.listdir("dist"):
        print(f"  - {file}")
    
    print("\nPublishing options:")
    print("1. TestPyPI (recommended for testing)")
    print("2. Production PyPI")
    print("3. Exit")
    
    choice = input("\nSelect option (1-3): ").strip()
    
    if choice == "1":
        # TestPyPI
        print("\n🧪 Publishing to TestPyPI...")
        cmd = "twine upload --repository testpypi dist/*"
        if run_command(cmd, "Uploading to TestPyPI"):
            print("\n✅ Published to TestPyPI!")
            print("Test installation:")
            print("pip install --index-url https://test.pypi.org/simple/ clwe==0.0.1")
    
    elif choice == "2":
        # Production PyPI
        print("\n⚠️  Publishing to PRODUCTION PyPI!")
        confirm = input("Are you sure? (yes/no): ").strip().lower()
        
        if confirm == "yes":
            cmd = "twine upload dist/*"
            if run_command(cmd, "Uploading to PyPI"):
                print("\n🎉 Published to PyPI!")
                print("Installation:")
                print("pip install clwe==0.0.1")
        else:
            print("Publishing cancelled.")
    
    elif choice == "3":
        print("Exiting.")
        return
    
    else:
        print("Invalid choice.")
        return

if __name__ == "__main__":
    main()
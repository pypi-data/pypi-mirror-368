from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="clwe",
    version="0.0.0",
    author="Siddhu Chelluru",
    author_email="founder@cryptopix.in",
    description="Color Lattice Learning with Errors - Post-Quantum Cryptographic Library",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://cryptopix.in",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Topic :: Security :: Cryptography",
        "Topic :: Scientific/Engineering :: Mathematics",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "numpy>=1.19.0",
        "cryptography>=3.4.0",
        "pillow>=8.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.10",
            "black>=21.0",
            "mypy>=0.800",
        ],
        "performance": [
            "scipy>=1.7.0",
            "numba>=0.53.0",
        ],
        "visualization": [
            "matplotlib>=3.3.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "clwe=clwe.cli:main",
        ],
    },
    keywords="post-quantum cryptography lattice cryptography visual steganography",
    project_urls={
        "Bug Reports": "https://cryptopix.in",
        "Source": "https://cryptopix.in",
        "Documentation": "https://cryptopix.in",
    },
    include_package_data=True,
    zip_safe=False,
)
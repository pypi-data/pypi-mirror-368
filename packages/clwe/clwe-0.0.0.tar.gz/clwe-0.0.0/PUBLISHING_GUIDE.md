# CLWE Publishing Guide

This guide covers how to publish CLWE to PyPI, contribute to the project, and maintain the library.

## Table of Contents

1. [Publishing to PyPI](#publishing-to-pypi)
2. [Development Setup](#development-setup)
3. [Testing](#testing)
4. [Building](#building)
5. [Version Management](#version-management)
6. [Contribution Guidelines](#contribution-guidelines)
7. [Release Process](#release-process)

## Publishing to PyPI

### Prerequisites

1. **PyPI Account**: Create accounts on both [PyPI](https://pypi.org) and [TestPyPI](https://test.pypi.org)
2. **API Tokens**: Generate API tokens for secure publishing
3. **Build Tools**: Install required tools

```bash
pip install build twine
```

### Step-by-Step Publishing

#### 1. Prepare the Release

```bash
# Clone the repository
git clone https://github.com/clwe-dev/clwe.git
cd clwe

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -e .[dev]
```

#### 2. Update Version

Update version in these files:
- `setup.py`
- `pyproject.toml`
- `clwe/__init__.py`

```python
# clwe/__init__.py
__version__ = "0.0.1"
```

#### 3. Run Tests

```bash
# Run full test suite
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=clwe --cov-report=html

# Check code formatting
black --check clwe/

# Type checking
mypy clwe/
```

#### 4. Build the Package

```bash
# Clean previous builds
rm -rf dist/ build/ *.egg-info/

# Build source and wheel distributions
python -m build
```

This creates:
- `dist/clwe-0.0.1.tar.gz` (source distribution)
- `dist/clwe-0.0.1-py3-none-any.whl` (wheel distribution)

#### 5. Test on TestPyPI

```bash
# Upload to TestPyPI first
twine upload --repository testpypi dist/*

# Test installation from TestPyPI
pip install --index-url https://test.pypi.org/simple/ clwe==0.0.1
```

#### 6. Publish to PyPI

```bash
# Upload to production PyPI
twine upload dist/*
```

#### 7. Verify Installation

```bash
# Test installation from PyPI
pip install clwe==0.0.1

# Verify functionality
python -c "import clwe; print(clwe.__version__)"
```

### Automated Publishing with GitHub Actions

Create `.github/workflows/publish.yml`:

```yaml
name: Publish to PyPI

on:
  release:
    types: [published]

jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.8'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install build twine
    
    - name: Build package
      run: python -m build
    
    - name: Publish to PyPI
      env:
        TWINE_USERNAME: __token__
        TWINE_PASSWORD: ${{ secrets.PYPI_API_TOKEN }}
      run: twine upload dist/*
```

## Development Setup

### Local Development Environment

```bash
# Clone repository
git clone https://github.com/clwe-dev/clwe.git
cd clwe

# Create virtual environment
python -m venv clwe-dev
source clwe-dev/bin/activate

# Install in editable mode with all dependencies
pip install -e .[dev,performance,visualization]

# Install pre-commit hooks
pre-commit install
```

### Project Structure

```
clwe-v0.0.1/
├── clwe/                       # Main package
│   ├── __init__.py             # Package initialization
│   ├── core/                   # Core implementations
│   │   ├── chromacrypt_kem.py  # KEM implementation
│   │   ├── color_cipher.py     # Visual encryption
│   │   ├── color_hash.py       # Quantum-resistant hashing
│   │   ├── chromacrypt_sign.py # Digital signatures
│   │   ├── parameters.py       # Security parameters
│   │   ├── transforms.py       # Color transformations
│   │   ├── ntt_engine.py       # NTT optimization
│   │   ├── hardware_acceleration.py  # SIMD/GPU support
│   │   ├── batch_operations.py # Batch processing
│   │   ├── production_optimizations.py # Performance
│   │   └── side_channel_protection.py  # Security
│   ├── utils/                  # Utilities
│   │   ├── serialization.py    # Data serialization
│   │   ├── validation.py       # Input validation
│   │   └── performance.py      # Performance tools
│   ├── examples/               # Usage examples
│   └── cli.py                  # Command-line interface
├── tests/                      # Test suite
├── docs/                       # Documentation
├── setup.py                    # Setup configuration
├── pyproject.toml             # Modern Python packaging
├── README.md                   # Main documentation
├── USAGE_GUIDE.md             # Usage guide
├── PUBLISHING_GUIDE.md        # This file
├── LICENSE                     # MIT license
├── MANIFEST.in                # Include additional files
└── .github/                   # GitHub workflows
```

## Testing

### Test Suite Organization

```bash
tests/
├── test_chromacrypt_kem.py     # KEM tests
├── test_color_cipher.py        # Visual encryption tests
├── test_color_hash.py          # Hash function tests
├── test_chromacrypt_sign.py    # Signature tests
├── test_optimizations.py       # Performance tests
├── test_side_channel.py        # Security tests
├── test_batch_operations.py    # Batch processing tests
└── conftest.py                 # Test configuration
```

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_chromacrypt_kem.py

# Run with coverage
pytest --cov=clwe --cov-report=html

# Run performance tests
pytest tests/test_optimizations.py -v

# Run security tests
pytest tests/test_side_channel.py -v
```

### Writing Tests

Example test structure:

```python
# tests/test_example.py
import pytest
import clwe

class TestChromaCryptKEM:
    def test_keygen(self):
        kem = clwe.ChromaCryptKEM(128)
        pub_key, priv_key = kem.keygen()
        assert pub_key is not None
        assert priv_key is not None
    
    def test_encap_decap(self):
        kem = clwe.ChromaCryptKEM(128)
        pub_key, priv_key = kem.keygen()
        
        secret, ciphertext = kem.encapsulate(pub_key)
        recovered = kem.decapsulate(priv_key, ciphertext)
        
        assert secret == recovered
    
    @pytest.mark.parametrize("security_level", [128, 192, 256])
    def test_multiple_security_levels(self, security_level):
        kem = clwe.ChromaCryptKEM(security_level)
        pub_key, priv_key = kem.keygen()
        assert len(pub_key.to_bytes()) > 0
```

## Building

### Source Distribution

```bash
# Build source distribution
python setup.py sdist
```

### Wheel Distribution

```bash
# Build wheel
python setup.py bdist_wheel
```

### Universal Build

```bash
# Build both source and wheel
python -m build
```

### Build Verification

```bash
# Check built distributions
twine check dist/*

# List contents
tar -tzf dist/clwe-0.0.1.tar.gz
unzip -l dist/clwe-0.0.1-py3-none-any.whl
```

## Version Management

### Semantic Versioning

CLWE follows [Semantic Versioning](https://semver.org/):

- **MAJOR.MINOR.PATCH** (e.g., 0.0.1)
- **MAJOR**: Breaking changes
- **MINOR**: New features, backward compatible
- **PATCH**: Bug fixes, backward compatible

### Version Update Checklist

1. Update `setup.py`
2. Update `pyproject.toml`
3. Update `clwe/__init__.py`
4. Update `CHANGELOG.md`
5. Create git tag
6. Update documentation

```bash
# Update version and create tag
git add .
git commit -m "Bump version to 0.0.1"
git tag v0.0.1
git push origin main --tags
```

## Contribution Guidelines

### Code Style

- **Formatting**: Use `black` for code formatting
- **Imports**: Use `isort` for import sorting  
- **Type Hints**: Add type hints for all public APIs
- **Docstrings**: Use Google-style docstrings

```python
def example_function(param1: int, param2: str) -> bool:
    """Example function with proper typing and docstring.
    
    Args:
        param1: Integer parameter description
        param2: String parameter description
        
    Returns:
        Boolean result description
        
    Raises:
        ValueError: When param1 is negative
    """
    if param1 < 0:
        raise ValueError("param1 must be non-negative")
    return len(param2) > param1
```

### Pull Request Process

1. **Fork** the repository
2. **Create** a feature branch
3. **Implement** changes with tests
4. **Run** test suite
5. **Submit** pull request

```bash
# Fork and clone
git clone https://github.com/yourusername/clwe.git
cd clwe

# Create feature branch
git checkout -b feature/new-optimization

# Make changes and test
# ... development work ...

# Commit and push
git add .
git commit -m "Add new optimization feature"
git push origin feature/new-optimization

# Create pull request on GitHub
```

### Commit Messages

Use conventional commit format:

```
type(scope): description

[optional body]

[optional footer]
```

Examples:
- `feat(kem): add new key generation optimization`
- `fix(cipher): resolve visual encryption bug`
- `docs(readme): update installation instructions`
- `perf(ntt): improve polynomial multiplication speed`

## Release Process

### Pre-Release Checklist

1. **Code Review**: All changes reviewed and approved
2. **Tests**: Full test suite passes
3. **Documentation**: Updated and accurate
4. **Changelog**: Release notes prepared
5. **Version**: Bumped appropriately
6. **Dependencies**: Verified and updated

### Release Steps

1. **Prepare Release Branch**
   ```bash
   git checkout -b release/0.0.1
   # Update version numbers
   # Update CHANGELOG.md
   git commit -m "Prepare release 0.0.1"
   ```

2. **Create Release PR**
   - Submit pull request to main branch
   - Ensure all checks pass
   - Get approval from maintainers

3. **Merge and Tag**
   ```bash
   git checkout main
   git pull origin main
   git tag v0.0.1
   git push origin v0.0.1
   ```

4. **Build and Publish**
   ```bash
   python -m build
   twine upload dist/*
   ```

5. **Create GitHub Release**
   - Go to GitHub releases page
   - Create new release from tag
   - Add release notes from CHANGELOG.md
   - Upload distribution files

### Post-Release

1. **Verify Installation**
   ```bash
   pip install clwe==0.0.1
   python -c "import clwe; print('Success!')"
   ```

2. **Update Documentation**
   - Update documentation sites
   - Announce release
   - Update social media

3. **Monitor Issues**
   - Watch for bug reports
   - Respond to user questions
   - Plan next release

## Maintenance

### Security Updates

- Monitor dependencies for vulnerabilities
- Update dependencies regularly
- Follow security best practices
- Respond quickly to security issues

### Performance Monitoring

- Run regular benchmarks
- Profile performance regressions
- Optimize based on user feedback
- Maintain performance targets

### Community Support

- Respond to issues promptly
- Help users with questions
- Accept and review contributions
- Maintain project roadmap

## Contact

For publishing questions or contributions:

- **Email**: contact@clwe.dev
- **GitHub**: https://github.com/clwe-dev/clwe
- **Issues**: https://github.com/clwe-dev/clwe/issues
- **Discussions**: https://github.com/clwe-dev/clwe/discussions
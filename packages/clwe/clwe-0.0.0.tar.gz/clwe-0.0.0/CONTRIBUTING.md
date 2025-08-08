# Contributing to CLWE

We welcome contributions to CLWE! This document provides guidelines for contributing to the project.

## Ways to Contribute

- **Bug Reports**: Report bugs via GitHub Issues
- **Feature Requests**: Suggest new features via GitHub Issues
- **Code Contributions**: Submit pull requests with improvements
- **Documentation**: Improve documentation and examples
- **Performance**: Optimize algorithms and implementations
- **Security**: Enhance security features and protections

## Development Setup

1. **Fork and Clone**
   ```bash
   git clone https://github.com/yourusername/clwe.git
   cd clwe
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv clwe-dev
   source clwe-dev/bin/activate  # On Windows: clwe-dev\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -e .[dev,performance,visualization]
   ```

4. **Run Tests**
   ```bash
   pytest tests/ -v
   ```

## Code Style

- **Formatting**: Use `black` for code formatting
- **Type Hints**: Add type hints for all public APIs
- **Docstrings**: Use clear, concise documentation
- **Performance**: Optimize for both security and speed
- **Security**: Follow secure coding practices

## Pull Request Process

1. **Create Feature Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Implement Changes**
   - Write clean, well-documented code
   - Add tests for new functionality
   - Ensure all tests pass
   - Update documentation as needed

3. **Test Your Changes**
   ```bash
   pytest tests/ --cov=clwe
   black clwe/
   mypy clwe/
   ```

4. **Submit Pull Request**
   - Write clear commit messages
   - Describe changes in pull request
   - Reference any related issues

## Reporting Issues

When reporting bugs, please include:
- Python version
- CLWE version
- Operating system
- Steps to reproduce
- Expected vs actual behavior
- Error messages or stack traces

## Security Issues

For security-related issues, please email contact@clwe.dev instead of using public issues.

## Code of Conduct

We expect all contributors to follow professional standards:
- Be respectful and inclusive
- Focus on constructive feedback
- Help maintain a welcoming environment
- Follow the project's technical standards

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
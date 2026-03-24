# Contributing to SpamShield ML

Thank you for considering contributing to SpamShield ML! We welcome contributions from the community.

## 📋 Table of Contents

- [Code of Conduct](#-code-of-conduct)
- [How Can I Contribute?](#-how-can-i-contribute)
- [Development Setup](#-development-setup)
- [Pull Request Guidelines](#-pull-request-guidelines)
- [Coding Standards](#-coding-standards)
- [Testing](#-testing)

---

## 🤝 Code of Conduct

Please read and follow our [Code of Conduct](CODE_OF_CONDUCT.md) to maintain a welcoming and inclusive community.

---

## 🙌 How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check existing issues. When creating a bug report, include:

- **Clear title and description**
- **Steps to reproduce** the issue
- **Expected vs actual behavior**
- **Environment details** (OS, Python version, etc.)
- **Code snippets** if applicable

**Example:**
```markdown
**Bug Summary**: Model inference fails on empty strings

**Steps to Reproduce**:
1. Start the API server
2. Send POST request to /analyze with empty text
3. Observe 500 error

**Expected**: Graceful handling with 400 error
**Actual**: Internal server error

**Environment**: Python 3.9, Windows 10
```

### Suggesting Enhancements

Enhancement suggestions should be detailed and include:

- **Use case** - why this feature would be useful
- **Proposed solution** - how it could work
- **Alternatives considered** - other approaches

### Your First Code Contribution

1. Look for issues labeled `good first issue` or `help wanted`
2. Fork the repository
3. Create a branch (`git checkout -b feat/your-feature`)
4. Make your changes
5. Submit a pull request

---

## 🛠 Development Setup

### Prerequisites

- Python 3.9+
- Node.js 20+
- Git

### Local Development

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/spam-detection.git
cd spam-detection

# Install backend dependencies
cd backend
pip install -r requirements.txt
pip install -e ".[dev]"  # For development mode

# Install frontend dependencies
cd ../frontend
npm install

# Download NLTK data
python -c "import nltk; nltk.download(['punkt_tab', 'stopwords', 'wordnet'])"

# Run tests to verify setup
cd ..
pytest tests/ -v
```

---

## 📬 Pull Request Guidelines

### Before Submitting

- [ ] Code follows project style guidelines
- [ ] Tests added/updated and passing
- [ ] Documentation updated if needed
- [ ] No linting errors
- [ ] Commit messages are clear and descriptive

### PR Title Format

Use [Conventional Commits](https://www.conventionalcommits.org/):

```
feat: add transformer-based classifier
fix: resolve memory leak in batch processing
docs: update API reference examples
test: add integration tests for /analyze endpoint
chore: update dependencies
```

### PR Description Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
Describe testing performed and results

## Checklist
- [ ] Code reviewed
- [ ] Tests passing
- [ ] Documentation updated
```

---

## 📝 Coding Standards

### Python

- Follow [PEP 8](https://pep8.org/) style guide
- Use type hints for function signatures
- Write docstrings for public APIs (Google style)
- Maximum line length: 88 characters (Black default)

```python
def analyze_message(text: str, threshold: float = 0.5) -> dict:
    """
    Analyze a message for spam classification.
    
    Args:
        text: The message text to analyze
        threshold: Classification threshold (default: 0.5)
    
    Returns:
        Dictionary containing prediction and confidence
    """
    pass
```

### JavaScript/TypeScript

- Use ES6+ features
- Prefer `const` over `let`
- Use TypeScript for new components
- Follow existing component patterns

---

## 🧪 Testing

### Running Tests

```bash
# Backend
pytest tests/ -v --cov=backend --cov-report=term-missing

# Frontend
cd frontend && npm test

# All tests
make test
```

### Writing Tests

- Unit tests for individual components
- Integration tests for API endpoints
- Aim for >90% code coverage
- Test edge cases and error conditions

---

## 📚 Additional Resources

- [Project Documentation](docs/)
- [API Reference](README.md#-api-reference)
- [ML Pipeline Guide](README.md#-ml-pipeline)

---

## 🎉 Recognition

Contributors will be acknowledged in:

- README.md contributors section
- Release notes
- Project documentation

Thank you for contributing to SpamShield ML! 🚀

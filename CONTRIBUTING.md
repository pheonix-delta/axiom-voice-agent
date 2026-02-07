# Contributing to AXIOM Voice Agent

Thank you for your interest in contributing! This document provides guidelines for participating in the project.

## Code of Conduct

We are committed to providing a welcoming and inclusive environment. All contributors must:
- Be respectful and constructive in discussions
- Avoid harassment, discrimination, or offensive behavior
- Report violations to the maintainers

## Getting Started

### Prerequisites
- Python 3.10+
- Git LFS (for model files)
- CUDA 12.x (optional, for GPU acceleration)

### Setup Development Environment
```bash
# Clone repository
git clone https://github.com/yourusername/axiom-voice-agent.git
cd axiom-voice-agent

# Create virtual environment (recommended name: axiomvenv)
python3 -m venv axiomvenv
source axiomvenv/bin/activate

# Install dependencies (avoid --break-system-packages; use the venv)
pip install -r requirements.txt

# Download models (see INSTALLATION.md)
python scripts/download_models.py

# Run tests
pytest tests/

# Start development server
python backend/main_agent_web.py
```

## Contribution Types

### 🐛 Bug Reports
- Check existing issues first
- Include: Python version, OS, error message, steps to reproduce
- Label: `bug`

### ✨ Feature Requests
- Describe the feature and why it's needed
- Explain how it fits the project vision
- Label: `enhancement`

### 📚 Documentation
- Fix typos, clarify explanations, add examples
- Ensure consistency with existing docs
- Label: `documentation`

### 🔧 Code Contributions
- Fork the repository
- Create feature branch: `git checkout -b feature/your-feature`
- Make changes following the code style guide (see below)
- Add tests for new functionality
- Commit with clear messages: `git commit -m "Add feature X"`
- Push and open a Pull Request

## Code Style Guidelines

### Python Code
- Follow **PEP 8** for style
- Use type hints for function signatures
- Document functions/classes with docstrings
- Max line length: 100 characters (soft limit)

```python
def classify_intent(text: str, confidence_threshold: float = 0.5) -> tuple[str, float]:
    """
    Classify user intent from text.
    
    Args:
        text: User input text
        confidence_threshold: Minimum confidence to return result
        
    Returns:
        (intent_label, confidence_score) tuple
        
    Raises:
        ValueError: If text is empty
    """
    if not text:
        raise ValueError("Text cannot be empty")
    
    prediction = model.predict(text)
    label, score = prediction
    
    if score >= confidence_threshold:
        return label, score
    return "unknown", score
```

### Commits
- Use clear, descriptive messages
- Reference issues: `Fix #123`
- Prefix with type: `feat:`, `fix:`, `docs:`, `test:`, `refactor:`

```
fix: correct STT symlink resolution on Windows
- Change relative path traversal from ../ to ../../
- Add fallback to environment variable
- Fixes #45

refactor: simplify conversation manager FIFO queue
- Extract queue logic to separate class
- Add type hints
- Reduce complexity from O(n) to O(1)
```

## Testing

### Running Tests
```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_intent_classifier.py

# Run with coverage
pytest --cov=backend tests/
```

### Writing Tests
```python
# tests/test_stt_handler.py
import pytest
from backend.stt_handler import STTHandler

def test_stt_initialization():
    """Test STT handler initializes without errors."""
    handler = STTHandler()
    assert handler is not None
    assert handler.initialized == True

def test_stt_transcription():
    """Test basic transcription."""
    handler = STTHandler()
    # Load test audio file
    audio_data = load_test_audio("test_audio.wav")
    result = handler.transcribe(audio_data)
    assert isinstance(result, str)
    assert len(result) > 0
```

## Critical - What NOT to Commit

### ❌ Never commit:
- **.env files** with API keys or secrets
- **Hardcoded passwords** or credentials
- **Large model binaries** (use Git LFS for `.gguf`, `.bin` files)
- **Personal API tokens** or authentication credentials
- **System-specific paths** (use relative paths from config.py)

### ✅ If working with models:
- Use Git LFS: `git lfs track "*.gguf"`
- Include model metadata (model card, training data attribution)
- Reference external sources (GitHub releases, HuggingFace hub)

### ✅ If adding secrets/configuration:
```python
# BAD
API_KEY = "sk-1234567890abcdef"  # ❌ Never hardcode

# GOOD
import os
API_KEY = os.getenv("API_KEY")  # ✅ Read from environment
```

## Model Contributions

### If proposing a new model or fine-tune:
1. Include training data attribution
2. Add model card (README in model directory)
3. Document performance metrics
4. Specify license (must be compatible with Apache 2.0)

**Example Model Card** (`models/my_model/README.md`):
```markdown
# My Custom Model

## Model Details
- **Base**: Llama 3.2 3B (Meta)
- **Fine-tuned on**: 500 robotics instruction examples
- **Task**: Intent classification for robotics commands
- **License**: Apache 2.0

## Performance
- Accuracy: 94.2% (validation set)
- F1-score: 0.912
- Inference time: ~50ms (CPU)

## Training Data
Data sourced from:
- Public robotics datasets (Creative Commons)
- User-contributed examples (see CONTRIBUTORS.md)
- Synthetic augmentation (50% of training set)

## Usage
```python
from setfit import SetFitModel
model = SetFitModel.from_pretrained("models/my_model")
prediction = model.predict(["move robot forward"])
```

## Attribution
- Training pipeline by [Your Name]
- Data curation with help from community members listed in CONTRIBUTORS.md
```

## Documentation Contributions

### Before updating docs:
- Check if changes are accurate (test code examples)
- Maintain consistency with existing style
- Update table of contents if adding new sections
- Add links to related documentation

### Documentation checklist:
- [ ] Examples are correct and tested
- [ ] Links work and point to current versions
- [ ] Formatting is consistent with existing docs
- [ ] Spelling and grammar are correct
- [ ] Code samples follow project style guide

## Pull Request Process

1. **Fork** the repository
2. **Branch** from `main`: `git checkout -b feature/something`
3. **Make changes** with clear commits
4. **Add tests** for new code (minimum 80% coverage for new functionality)
5. **Update docs** if needed
6. **Push** to your fork
7. **Open PR** with:
   - Clear title: `Add X feature` or `Fix Y bug`
   - Description: What changed and why
   - Link issues: `Closes #123`
   - Screenshots (if UI change)

### PR Review Process
- At least 1 maintainer review required
- Tests must pass
- No merge conflicts
- Code follows style guidelines
- Documentation updated

### Feedback Loop
- Respond to comments constructively
- Request re-review after changes
- Ask for clarification if needed

## Recognition

Contributors are recognized in:
- `CONTRIBUTORS.md` (major contributions)
- GitHub contributor graph
- Release notes (for significant work)

### Levels of Contribution
- **Bug fix**: 1-point issue report + fix
- **Feature**: 10-point new capability
- **Documentation**: 5-point doc improvement
- **Model contribution**: 15-point custom model

## Licensing

By contributing to this project, you agree that:
- Your code is licensed under **Apache 2.0** (see LICENSE file)
- You have rights to the code you contribute
- You grant the project rights to use and redistribute your contributions

## Questions or Need Help?

- **Documentation**: See [README.md](README.md), [QUICK_START.md](QUICK_START.md), [OSS_DEPLOYMENT_GUIDE.md](OSS_DEPLOYMENT_GUIDE.md)
- **Technical**: Open an issue with `question` label
- **Security**: See [SECURITY.md](SECURITY.md) for responsible disclosure

## Resources

- [Python PEP 8 Style Guide](https://www.python.org/dev/peps/pep-0008/)
- [Apache 2.0 License](LICENSE)
- [Git LFS Documentation](https://git-lfs.github.com/)
- [Project Architecture](docs/ARCHITECTURE.md)
- [SetFit Documentation](https://github.com/huggingface/setfit)

---

**Thank you for contributing to AXIOM! 🚀**

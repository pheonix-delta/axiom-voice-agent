# Changelog

All notable changes to the AXIOM Voice Agent project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- CHANGELOG.md to track project updates and releases
- Virtual environment safety guard in start.sh to prevent system-wide package pollution

### Changed
- **BREAKING**: Standardized virtual environment naming from `venv` to `axiomvenv` across all documentation
- Updated setup instructions in README.md, QUICK_START.md, REQUIREMENTS_AND_SETUP_ISSUES.md, INSTALLATION.md, GITHUB_README.md, CONTRIBUTING.md to use `axiomvenv`
- Improved start.sh Python version check to validate `python3` existence before calling `--version`
- Enhanced installation guidance with explicit warnings against using `--break-system-packages` flag

### Fixed
- Python version check in start.sh now properly validates Python 3 existence before attempting version detection
- Virtual environment activation check in start.sh now prevents installation outside of venv

### Security
- Added safeguards to ensure all pip installations occur within virtual environment, preventing system Python pollution

---

## [0.1.0] - 2026-02-07

### Initial Release
- Complete voice agent system with STT, TTS, intent classification, and RAG
- SetFit-based intent classifier with 94% accuracy
- Semantic RAG handler for knowledge retrieval
- 3D equipment carousel UI
- Template response system with 2,116+ pre-verified responses
- WebSocket-based real-time communication
- Conversation history and context management

## Description
<!-- Provide a clear and concise description of what this PR accomplishes -->

## Related Issue(s)
<!-- Link related issues using "Closes #123" or "Fixes #456" -->
Closes #

## Type of Change
<!-- Mark the relevant option with an 'x' -->
- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update
- [ ] Performance improvement
- [ ] Code refactoring
- [ ] Model update or fine-tune

## Changes Made
<!-- List the key changes in this PR -->
- 
- 
- 

## Testing Performed
<!-- Describe the testing you've done to verify your changes -->
- [ ] Tested locally with `python backend/main_agent_web.py`
- [ ] Verified voice input/output functionality
- [ ] Ran existing tests: `pytest tests/`
- [ ] Added new tests for new functionality
- [ ] Tested on target hardware (specify GPU/CPU)

### Test Results
```
# Paste test output or describe manual testing results
```

## Screenshots / Demo (if applicable)
<!-- Add screenshots or GIFs for UI changes, or link to demo videos -->

## Performance Impact
<!-- Does this change affect performance? Provide before/after metrics if relevant -->
- Latency impact: <!-- e.g., "No change", "+50ms for new feature", "-30ms optimization" -->
- Memory impact: <!-- e.g., "No change", "+200MB for new model", "-15% reduction" -->
- VRAM impact: <!-- e.g., "No change", "+500MB", "-1GB optimization" -->

## Documentation Updated
<!-- Mark what documentation has been updated -->
- [ ] README.md (if user-facing change)
- [ ] CHANGELOG.md (for notable changes)
- [ ] Inline code comments/docstrings
- [ ] docs/ folder (if applicable)
- [ ] CONTRIBUTING.md (if process changed)

## Code Quality Checklist
- [ ] Code follows PEP 8 style guidelines
- [ ] Functions have type hints and docstrings
- [ ] No hardcoded credentials or API keys
- [ ] No `print()` statements (use `logging` instead)
- [ ] Relative paths handled via `config.py` (no absolute paths)
- [ ] Large models tracked with Git LFS (if applicable)

## Security Considerations
- [ ] No sensitive data exposed
- [ ] Input validation implemented for user-facing features
- [ ] Dependencies checked for known vulnerabilities

## Breaking Changes
<!-- If this PR introduces breaking changes, describe them and the migration path -->

## Additional Notes
<!-- Any other information reviewers should know -->

## Reviewer Checklist (for maintainers)
- [ ] Code review completed
- [ ] Tests pass
- [ ] Documentation is adequate
- [ ] No merge conflicts
- [ ] Approved for merge

# libadic Release Checklist

Use this checklist when preparing a new release for PyPI distribution.

## Pre-Release Preparation

### Version Management
- [ ] Update version number in `python/libadic/_version.py`
- [ ] Update version in `pyproject.toml` (should auto-sync)
- [ ] Update `CHANGELOG.md` with new version details
- [ ] Verify all version references are consistent

### Code Quality
- [ ] Run full test suite: `pytest python/tests/ -v`
- [ ] Run crypto tests: `python python/examples/crypto_api_demo.py`
- [ ] Run installation verification: `python scripts/verify_installation.py`
- [ ] Check code formatting: `black python/ --check`
- [ ] Run static analysis: `mypy python/libadic/ --ignore-missing-imports`

### Documentation
- [ ] Update README.md with any new features
- [ ] Update API_REFERENCE.md if needed
- [ ] Update PYTHON_CRYPTO_API.md for crypto changes
- [ ] Verify all links in documentation work
- [ ] Update PIP_QUICKSTART.md if installation process changed

### Build System
- [ ] Test local build: `python -m build --sdist`
- [ ] Test wheel build (if possible): `python -m build --wheel`
- [ ] Verify MANIFEST.in includes all necessary files
- [ ] Check that examples and documentation are included
- [ ] Test clean install in virtual environment

## Release Process

### GitHub Preparation
- [ ] Commit all changes
- [ ] Push to main branch
- [ ] Verify GitHub Actions CI passes
- [ ] Create and push version tag: `git tag v1.x.x && git push origin v1.x.x`

### Testing Distribution
- [ ] Build packages: `./scripts/build_and_upload.sh`
- [ ] Check package quality: `twine check dist/*`
- [ ] Upload to Test PyPI: `./scripts/build_and_upload.sh test`
- [ ] Test installation from Test PyPI:
  ```bash
  pip install -i https://test.pypi.org/simple/ libadic
  python -c "import libadic; libadic.show_versions()"
  ```
- [ ] Test crypto functionality from Test PyPI installation
- [ ] Uninstall test package: `pip uninstall libadic`

### Production Release
- [ ] Final verification of package contents
- [ ] Create GitHub Release with release notes
- [ ] Upload to Production PyPI: `./scripts/build_and_upload.sh prod`
- [ ] Verify package appears on PyPI: https://pypi.org/project/libadic/
- [ ] Test installation from PyPI: `pip install libadic`

### Post-Release
- [ ] Update documentation with new PyPI links
- [ ] Announce release on relevant channels
- [ ] Monitor for installation issues
- [ ] Update development version number for next cycle

## Emergency Rollback

If a critical issue is discovered after release:

1. **Yank the problematic version on PyPI**:
   - Go to https://pypi.org/manage/project/libadic/
   - Find the problematic version and "yank" it
   
2. **Hotfix and re-release**:
   - Fix the critical issue
   - Increment patch version (e.g., 1.0.0 → 1.0.1)
   - Follow full release process for hotfix

3. **Communication**:
   - Create GitHub issue explaining the problem
   - Update documentation with workarounds if needed
   - Consider posting on relevant forums/communities

## Environment Setup

### Required Tools
```bash
pip install build twine pytest black mypy
```

### PyPI Credentials
- Set up `~/.pypirc` using `.pypirc.template`
- Get API tokens from PyPI and Test PyPI
- Store tokens securely (never commit to git)

### GitHub Secrets (for automated releases)
- `PYPI_API_TOKEN`: Production PyPI token
- `TEST_PYPI_API_TOKEN`: Test PyPI token

## Version Numbering

libadic follows semantic versioning (semver):

- **Major** (x.0.0): Breaking changes to public API
- **Minor** (1.x.0): New features, backward compatible
- **Patch** (1.0.x): Bug fixes, backward compatible

### Examples:
- `1.0.0`: Initial stable release
- `1.0.1`: Bug fix release
- `1.1.0`: New cryptographic algorithm support
- `2.0.0`: Major API restructuring (breaking changes)

## Common Issues

### Build Failures
- **Missing GMP/MPFR**: Install development libraries
- **CMake errors**: Check CMake version (≥3.14 required)
- **Compiler errors**: Ensure C++17 compiler available

### Upload Issues
- **Duplicate version**: Must increment version for new uploads
- **Authentication**: Check PyPI API tokens in `~/.pypirc`
- **Package size**: Large packages may timeout (use GitHub Actions)

### Installation Issues
- **Import errors**: Check Python version compatibility (≥3.7)
- **Missing dependencies**: Ensure numpy is installed
- **Platform issues**: Some platforms may need wheels built by CI

---

**Remember**: Better to catch issues in Test PyPI than Production PyPI! 🚀
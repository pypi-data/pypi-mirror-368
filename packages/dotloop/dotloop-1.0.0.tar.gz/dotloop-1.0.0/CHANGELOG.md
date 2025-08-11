# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial project structure and deployment configuration

## [1.0.0] - 2024-01-XX

### Added
- Initial release of the Dotloop Python API wrapper
- Complete project structure with modern Python packaging
- Comprehensive deployment process with GitHub Actions
- Version bump script for automated releases
- Full test coverage requirements (100%)
- Code quality tools integration (Black, isort, flake8, mypy)
- Security scanning with bandit and safety
- Type hints support with py.typed marker
- Comprehensive documentation and README
- MIT License
- Support for Python 3.8+

### Infrastructure
- GitHub Actions workflow for CI/CD
- Automated PyPI publishing on tag creation
- Multi-platform testing (Ubuntu, Windows, macOS)
- Code coverage reporting with Codecov
- Security vulnerability scanning
- Automated changelog generation
- GitHub releases creation

### Development Tools
- Pre-commit hooks configuration
- Development dependencies management
- Build and packaging configuration
- Version management automation
- Documentation generation setup

---

## Release Process

This project uses automated releases triggered by git tags:

1. **Version Bump**: Use `python scripts/bump_version.py [major|minor|patch]`
2. **Automatic Publishing**: GitHub Actions automatically publishes to PyPI when a version tag is pushed
3. **Release Notes**: GitHub releases are created automatically with changelog information

## Version History

- **1.0.0**: Initial release with complete project structure and deployment automation

---

For more details about each release, see the [GitHub Releases](https://github.com/theperrygroup/dotloop/releases) page. 
# Changelog

All notable changes to django-i18n-noprefix will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- GitHub Actions release workflow for automated PyPI deployment
- TestPyPI integration for pre-release testing
- Release helper script for local validation
- Version management with __version__.py
- Automated release notes generation

## [0.1.0] - TBD

### Added
- Initial implementation of NoPrefixLocaleMiddleware
- Language detection from session, cookie, and Accept-Language header
- Template tags for language switching (switch_language_url, is_current_language, language_selector)
- Three language selector styles (dropdown, list, inline)
- CSS framework support (Bootstrap 5, Tailwind CSS, Vanilla CSS)
- Complete example Django project with translations
- Comprehensive test suite with 93% code coverage
- System checks for configuration validation
- Django 4.2 LTS, 5.0, and 5.1 support
- Python 3.8 through 3.12 support
- Development environment setup script
- Pre-commit hooks for code quality (Black, Ruff, MyPy)
- GitHub Actions CI/CD pipeline for testing and quality checks
- Integration tests for Django reverse() and template tags
- End-to-end scenario tests

### Fixed
- Session key attribute check for compatibility with mock sessions in tests

### Documentation
- Complete README with installation and usage instructions
- Example project with Korean and Japanese translations
- Task tracking document (TASKS.md) for development roadmap
- Contributing guidelines
- API reference documentation

[Unreleased]: https://github.com/jinto/django-i18n-noprefix/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/jinto/django-i18n-noprefix/releases/tag/v0.1.0

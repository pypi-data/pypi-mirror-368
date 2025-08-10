# Changelog - Rust Package

All notable changes to the Rust package will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial Rust library implementation
- Command-line interface for course map generation
- Support for SVG, PNG, and DOT output formats
- Comprehensive test suite with 14 unit tests
- Graphviz integration for visual output

### Changed
- Package name unified to `coursemap`
- Independent versioning system

### Fixed
- Test isolation using tempfile for temporary files
- Doctest compilation issues

## [0.1.0] - 2025-01-08

### Added
- Initial release of the Rust package
- Core functionality for parsing Quarto/Markdown documents
- Dependency graph generation
- Multi-format rendering support

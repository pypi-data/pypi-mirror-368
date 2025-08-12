## [0.4.2](https://github.com/soren-n/vibe/compare/v0.4.1...v0.4.2) (2025-08-11)

### Bug Fixes

* ensure publishing jobs fetch git tags for proper versioning ([aca42a2](https://github.com/soren-n/vibe/commit/aca42a2e407aeeb9a6f4a664500685da686a34a5))

## [0.4.1](https://github.com/soren-n/vibe/compare/v0.4.0...v0.4.1) (2025-08-11)

### Bug Fixes

* add TestPyPI publishing step to release workflow ([3e96c38](https://github.com/soren-n/vibe/commit/3e96c38db69c60fc9fdddcc2a4961fbffac873ba))

## [0.4.0](https://github.com/soren-n/vibe/compare/v0.3.0...v0.4.0) (2025-08-11)

### Features

* add TestPyPI publishing workflows ([a640f65](https://github.com/soren-n/vibe/commit/a640f65ae7d2e527c36c337cb39318db080ce54d))

## [0.3.0](https://github.com/soren-n/vibe/compare/v0.2.3...v0.3.0) (2025-08-11)

### Features

* rename package to vibe-soren-n for PyPI publishing ([d643dee](https://github.com/soren-n/vibe/commit/d643deec88a40c5a8ac9121284847496de4336f7))

## [0.2.3](https://github.com/soren-n/vibe/compare/v0.2.2...v0.2.3) (2025-08-11)

### Bug Fixes

* properly pass VSCE_PAT environment variable to semantic-release ([544ed14](https://github.com/soren-n/vibe/commit/544ed14ad210d2857b2eeed71bd0d525d85664e6))

## [0.2.2](https://github.com/soren-n/vibe/compare/v0.2.1...v0.2.2) (2025-08-11)

### Bug Fixes

* update vsce authentication to use environment variable instead of deprecated --pat flag ([affc328](https://github.com/soren-n/vibe/commit/affc328e647ddcdb89c55d6327961fcf384b3176))

# Changelog

All notable changes to the Vibe project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.2.1] - 2025-08-11

### Added
- Comprehensive research guidance fallback for unmatched queries
- Dynamic workflow discovery with timestamp-based cache invalidation
- VS Code extension with MCP integration
- Universal project release workflows
- Image conversion workflows with ImageMagick

### Changed
- Enhanced analyzer with smart fallback logic
- Improved workflow orchestration and guidance generation
- Updated workflow YAML schema validation

### Fixed
- Removed FFmpeg from image conversion workflow (focused on static images)
- Resolved workflow schema validation issues
- Fixed duplicate function definitions in loader
- Added proper type annotations to resolve mypy errors

## [0.1.0] - 2025-01-01

### Added
- Initial release of Vibe workflow orchestration system
- Core workflow engine with YAML-based definitions
- Natural language query processing
- MCP server integration
- Basic CI/CD pipeline

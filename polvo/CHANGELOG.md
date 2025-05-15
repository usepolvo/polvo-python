# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- New features that haven't been released yet

### Changed

- Changes to existing functionality

### Deprecated

- Features that will be removed in upcoming releases

### Removed

- Features that have been removed

### Fixed

- Bug fixes

### Security

- Security improvements

## [1.2.0] - 2024-04-07

### Added

- Google Drive tentacle with comprehensive file operations support:
  - Added multi-tenant OAuth2 authentication support
  - Added file operations (list, get, download, create, update, delete)
  - Integration with Google's official Python client library
  - Example scripts demonstrating usage patterns

### Changed

- Restructured Google Drive tentacle to follow resource-specific pattern:
  - Moved file operations to dedicated Files class
  - Leveraged core OAuth2Auth implementation
  - Improved code organization and maintainability

## [1.1.0] - 2024-04-05

### Added

- Added AI model tentacles for multiple providers:
  - OpenAI integration with chat completions and embeddings support
  - Anthropic Claude integration with messages API and streaming support
  - Google Gemini integration with text generation and embeddings
- New example script demonstrating AI model integrations
- Updated requirements to include AI provider SDK dependencies

## [1.0.2] - 2024-04-05

### Added

- Initial public release of the Polvo Python library

### Features

- Core functionality with auth handlers, API client templates, rate limiters
- Brain module for high-level LLM abstractions
- Tentacles for API integrations
- Webhook processing and server
- Async support throughout the library

# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.3] - 2024-12-XX

### Added
- Support for DeepSeek provider with reasoning models
- Support for Google Gemini provider
- Enhanced error handling for missing optional dependencies
- Improved token counting with provider-specific estimators
- Better memory management with system prompt preservation
- JSON template validation for structured data extraction
- Streaming chat support with real-time response handling

### Changed
- Updated default models to more modern options (gpt-4o-mini, claude-3.5-sonnet)
- Improved default parameters across all providers
- Enhanced memory system with better token and prompt limiting
- Refactored token counting system for better modularity
- Updated documentation with comprehensive examples

### Fixed
- Fixed Anthropic provider error handling for missing dependencies
- Corrected token counting for streaming responses
- Fixed memory trimming logic for system prompts
- Resolved import issues with optional dependencies
- Fixed JSON parsing edge cases

## [0.1.2] - 2024-XX-XX

### Added
- Initial support for multiple LLM providers
- Basic memory management system
- Token counting functionality
- JSON parsing utilities

### Changed
- Core architecture improvements
- Better error handling

## [0.1.1] - 2024-XX-XX

### Added
- Initial release
- Basic chat functionality
- OpenAI provider support

[0.1.3]: https://github.com/commonai/common-ai-core/compare/v0.1.2...v0.1.3
[0.1.2]: https://github.com/commonai/common-ai-core/compare/v0.1.1...v0.1.2
[0.1.1]: https://github.com/commonai/common-ai-core/releases/tag/v0.1.1 
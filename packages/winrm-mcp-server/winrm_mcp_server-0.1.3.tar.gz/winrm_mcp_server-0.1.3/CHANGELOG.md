# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2025-08-08

### Added

- Initial release of WinRM MCP Server
- Remote PowerShell command execution via WinRM
- Support for both HTTP and HTTPS connections
- Configurable timeout and retry settings
- Comprehensive error handling with semantic error types
- SSL certificate validation options
- Detailed logging compatible with VS Code MCP output
- Command-line entry point for easy installation
- Complete documentation and examples

### Security

- Secure credential handling (credentials not logged)
- SSL certificate validation by default
- Input validation to prevent command injection

[Unreleased]: https://github.com/antonvano-microsoft/winrm-mcp-server/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/antonvano-microsoft/winrm-mcp-server/releases/tag/v0.1.0

# Changelog

All notable changes to this project will be documented in this file.

## [0.1.2] - 2025-01-12

### Added
- Debug mode support via `MCP_DEBUG` environment variable
- Proper stderr logging for MCP stdio transport compliance
- Protocol-level debug messages for request/response tracing

### Changed
- All logging output now explicitly directed to stderr to keep stdout clean for JSON-RPC
- Enhanced logging with debug-level traces for troubleshooting

### Fixed
- Fixed potential stdout pollution issue in MCP stdio transport mode
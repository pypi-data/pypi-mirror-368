# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.2] - 2025-01-20

### Added
- **Address Isolation System**: Complete address privacy and isolation between users
- Enhanced session management with automatic address restoration
- Address validation without tenant account contamination
- Pattern-based tenant default address detection

### Changed
- **BREAKING**: New users must provide a valid address during first session acquisition
- Existing users have addresses automatically restored from snapshots
- Address validation now uses read-only operations to prevent contamination
- Enhanced error handling for address-related operations

### Fixed
- **Critical**: Address validation no longer pollutes tenant accounts with mystery addresses
- **Critical**: Fixed address cleanup order during session release
- Dynamic tenant default detection using address patterns instead of hardcoded IDs
- Proper address restoration from encrypted snapshots

## [0.1.1] - 2025-01-15

### Added
- `get_standalone_address_suggestions()` method for address validation without requiring an active session
- Enhanced address management examples in documentation

### Changed
- Updated documentation to distinguish between session-based and standalone address suggestions

## [0.1.0] - 2024-08-04

### Added
- Initial release of DoorDash Python Client
- Organization-based authentication system
- Restaurant search and browsing functionality
- Cart management (add, remove, view items)
- Order placement and tracking
- Address management
- Payment method handling
- Bundle opportunities for multi-store orders
- Comprehensive type hints and Pydantic models
- Both synchronous and asynchronous API support
- Automatic retry logic and error handling
- Full test suite and examples
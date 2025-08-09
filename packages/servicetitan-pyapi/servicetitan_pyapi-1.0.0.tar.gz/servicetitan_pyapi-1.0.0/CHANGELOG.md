# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2024-01-10

### Added
- Initial release of ServiceTitan Python API library
- OAuth2 authentication support with automatic token refresh
- BaseClient architecture for consistent API interactions
- Comprehensive client modules:
  - Appointments client
  - Bookings client  
  - Calls client
  - Customers client
  - Estimates client
  - Invoices client
  - Jobs client
  - Leads client
  - Locations client
  - Marketing client
  - Marketing Ads client
  - Settings client
- Custom endpoint support for flexible API access
- Built-in pagination handling
- Comprehensive error handling and custom exceptions
- Type hints throughout the codebase
- Utilities for common operations
- Response models for structured data handling

### Testing
- Complete test suite with 58 test cases
- pytest framework with fixtures and mocking
- Coverage reporting and automated testing
- Test cases covering authentication, base client, and all service clients

### Documentation
- Comprehensive README with installation and usage examples
- API documentation with code samples
- Contributor guidelines and development setup
- Security policy and vulnerability reporting procedures
- Testing documentation with setup instructions

### Development
- Black code formatting
- isort import sorting
- flake8 linting
- mypy type checking
- bandit security scanning
- Pre-commit hooks for code quality
- GitHub Actions CI/CD pipeline
- Automated testing across Python 3.8-3.12

### Legal & Compliance
- MIT License for open source distribution
- Security policy for vulnerability disclosure
- Contribution guidelines for community development
- Issue templates for structured bug reports and feature requests

## [Unreleased]

### Planned
- Additional ServiceTitan API endpoint coverage
- Enhanced error handling and retry mechanisms
- Performance optimizations for large data sets
- Extended documentation and examples
- API response caching capabilities

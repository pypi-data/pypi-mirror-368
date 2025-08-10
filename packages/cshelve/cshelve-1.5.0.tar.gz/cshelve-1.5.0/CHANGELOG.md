# Changelog

## [1.5.0] - 2025-08-09
### Added
- Configuration as `dict`.

## [1.4.0] - 2025-08-06
### Added
- SFTP provider.

## [1.3.0] - 2025-05-28
### Fixed
- AWS S3 provider now raises `cshelve.KeyNotFoundError` when trying to access a non-existing key.

### Added
- Raise `cshelve.AuthTypeError` if the authentication type is unknown on AWS S3.
- Raise `cshelve.AuthError` if the authentication fails on AWS S3.

## [1.2.0] - 2025-02-09
### Added
- Ability to save non-pickle objects.
- Option to disable versioning.

## [1.1.0] - 2025-02-07
### Added
- AWS S3 support.
- TOML support for `provider_params`.
- In TOML, replace variables starting with "$" with the corresponding environment variable.

## [1.0.0] - 2025-01-31
### Added
- Add metadata to object to improve compatibility between versions.
- Allow transparent migration from older version to 1.0.0.
- Tests for compatibility between versions, os and python versions.

## [0.9.0] - 2024-12-22
### Added
- Allow data encryption

## [0.8.0] - 2024-12-17
### Added
- Allow data compression

## [0.7.0] - 2024-12-04
### Added
- Provide parameters to provider.
- Provider parameters support on `in-memory` and `azure-blob`.

### Improvement
- Release on Pypi on the GitHub trigger.

## [0.6.0] - 2024-11-24
### Added
- Logging support for the `cshelve`.
- Logging support for the `azure-blob` provider.

## [0.5.0] - 2024-11-20
### Added
- Pathlib support.

## [0.4.1] - 2024-11-14
### Improvement
- Documentation for the `cshelve` package.

## [0.4.0] - 2024-11-12
### Breaking Change
- The `azure-blob` is not installed by default. To install it, use `pip install cshelve[azure-blob]`.

### Added
- Added a development container for streamlined development.
- Introduced `ConfigurationError` exception for handling provider configuration errors.
- Initialized project documentation.

## [0.3.0] - 2024-11-08
### Added
- In-memory provider

### Improvement
- Tests refactored.
- Use in-memory provider for unit tests.
- Run examples in the CI pipeline.

## [0.2.2] - 2024-11-03
### Added
- Authentication methods for the azure-blob provider:
    - Anonymous read-only access on public blob storage.
    - Using Access key.

## [0.2.1] - 2024-11-02
### Improvement
- Interfaced with cloud provider modules.
- Added unit tests for the azure-blob provider.

## [0.2.0] - 2024-10-30
### Added
- Performance tests were added to the project. See [main.py](./performances/) for details.

### Changed
- **Breaking Change**: The provider `azure` in the `.ini` configuration has been renamed to `azure-blob`.

### Improved
- Improved the `n` flag to remove database content quicker using parallelism.

## [0.1.0] - 2024-10-24
- Initial release.

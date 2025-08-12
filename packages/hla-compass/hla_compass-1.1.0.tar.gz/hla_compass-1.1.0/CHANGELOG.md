# Changelog

All notable changes to the HLA-Compass Python SDK will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-07-15

### Added
- Initial release of HLA-Compass Python SDK
- CLI tool for module management (`hla-compass` command)
- Module initialization with templates
- Local and remote module testing
- Module building and packaging
- Module deployment to HLA-Compass platform
- Data access APIs for peptides, proteins, and samples
- Storage APIs for S3 integration
- Authentication system with JWT support
- Rich terminal output for better developer experience
- Comprehensive error handling and validation
- Example modules demonstrating best practices

### Features
- `hla-compass init` - Create new modules from templates
- `hla-compass test` - Test modules locally or remotely
- `hla-compass build` - Package modules for deployment
- `hla-compass deploy` - Deploy modules to the platform
- `hla-compass logs` - View module execution logs
- `hla-compass auth` - Manage authentication

### Documentation
- Complete API documentation
- Module development guide
- Example modules with detailed comments
- Troubleshooting guide

## [0.9.0] - 2025-06-01 (Pre-release)

### Added
- Beta version for internal testing
- Core SDK functionality
- Basic CLI commands

## Notes

To upgrade to the latest version:
```bash
pip install --upgrade hla-compass
```

For detailed documentation, visit https://docs.hla-compass.com
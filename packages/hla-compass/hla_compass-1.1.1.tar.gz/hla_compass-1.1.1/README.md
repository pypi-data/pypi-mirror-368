# HLA-Compass Python SDK

[![PyPI version](https://badge.fury.io/py/hla-compass.svg)](https://badge.fury.io/py/hla-compass)
[![Python Versions](https://img.shields.io/pypi/pyversions/hla-compass.svg)](https://pypi.org/project/hla-compass/)
[![Downloads](https://pepy.tech/badge/hla-compass)](https://pepy.tech/project/hla-compass)

The official Python SDK for developing modules on the HLA-Compass platform.

## Requirements

- Python 3.8 or higher (3.8, 3.9, 3.10, 3.11 supported)
- pip package manager

## Installation

### Install from PyPI (Recommended)

```bash
pip install hla-compass
```

For development tools:
```bash
pip install hla-compass[dev]
```

For machine learning modules:
```bash
pip install hla-compass[ml]
```

### Install from Source (Latest Development Version)

```bash
# Clone the repository
git clone https://github.com/AlitheaBio/HLA-Compass-platform.git
cd HLA-Compass-platform/sdk/python

# Install in development mode
pip install -e .
```

## Quick Start

```bash
# Install SDK
pip install hla-compass

# Create module
hla-compass init my-module --type no-ui --compute lambda

# Test locally
cd my-module
hla-compass test --local

# Build package
hla-compass build
```

📚 **For complete development guide, see: [/docs/MODULE_DEVELOPMENT_GUIDE.md](https://github.com/AlitheaBio/HLA-Compass-platform/blob/main/docs/MODULE_DEVELOPMENT_GUIDE.md)**

## Module Development

For comprehensive module development information including:
- Base Module class and APIs
- Data access patterns
- Storage operations
- Error handling
- Testing strategies
- Deployment workflows

**See the complete guide: [/docs/MODULE_DEVELOPMENT_GUIDE.md](https://github.com/AlitheaBio/HLA-Compass-platform/blob/main/docs/MODULE_DEVELOPMENT_GUIDE.md)**

## CLI Commands

### Module Management

```bash
# Create new module
hla-compass init <name> [options]

# Validate module structure
hla-compass validate

# Test module
hla-compass test [--local] [--remote] [--input FILE]

# Build module package
hla-compass build [--output DIR]

# Deploy module
hla-compass deploy <file> [--env ENV] [--version VERSION]
```

### Authentication

```bash
# Login to platform
hla-compass auth login --env dev

# Logout
hla-compass auth logout

# Check authentication status
hla-compass auth status
```

### Logs and Monitoring

```bash
# View module logs
hla-compass logs [JOB_ID] [--tail] [--lines N]

# List recent executions
hla-compass logs
```

## Testing

### Unit Testing

```python
# tests/test_module.py
import pytest
from hla_compass.testing import ModuleTester, MockContext

def test_module_execution():
    tester = ModuleTester()
    
    input_data = {
        'sequence': 'MLLSVPLLL',
        'threshold': 0.5
    }
    
    result = tester.test_local(
        'backend/main.py',
        input_data
    )
    
    assert result['status'] == 'success'
    assert len(result['results']) > 0
```

### Integration Testing

```python
# Test with mock API data
def test_with_mock_data():
    context = MockContext.create(
        api_data={
            'peptides': [
                {'id': '1', 'sequence': 'MLLSVPLLL'},
                {'id': '2', 'sequence': 'SIINFEKL'}
            ]
        }
    )
    
    result = tester.test_local(
        'backend/main.py',
        {'min_length': 8},
        context
    )
    
    assert len(result['results']) == 2
```

### Performance Testing

```python
# Benchmark module performance
def test_performance():
    tester = ModuleTester()
    
    results = tester.benchmark(
        'backend/main.py',
        input_data,
        iterations=100
    )
    
    assert results['average_time'] < 0.1  # 100ms
```

## Advanced Features

### Module Types

#### Lambda Modules (Quick Analysis)
- Execution time: <15 minutes
- Memory: 128MB - 10GB
- Best for: Simple calculations, data filtering

#### Fargate Modules (Long Running)
- Execution time: <8 hours
- Memory: 512MB - 30GB
- Best for: Complex pipelines, batch processing

#### SageMaker Modules (ML Inference)
- GPU support available
- Pre-trained model hosting
- Best for: Machine learning predictions

### With-UI Modules

For modules with frontend components:

```typescript
// frontend/index.tsx
import React from 'react';
import { ModuleProps } from '@hla-compass/sdk';

export const ModuleUI: React.FC<ModuleProps> = ({
  input,
  onExecute,
  result
}) => {
  return (
    <div>
      {/* Your UI here */}
    </div>
  );
};
```

### Custom Validation

```python
class MyModule(Module):
    def validate_inputs(self, input_data):
        # Call parent validation
        validated = super().validate_inputs(input_data)
        
        # Custom validation
        sequence = validated.get('sequence', '')
        if not all(aa in 'ACDEFGHIKLMNPQRSTVWY' for aa in sequence):
            raise ValidationError("Invalid amino acids in sequence")
        
        return validated
```

## Best Practices

1. **Input Validation**: Always validate inputs thoroughly
2. **Error Handling**: Use try-except blocks and provide clear error messages
3. **Logging**: Use appropriate logging levels (debug, info, warning, error)
4. **Performance**: Process data in batches when possible
5. **Memory**: Stream large results instead of loading all into memory
6. **Security**: Never hardcode credentials or sensitive data
7. **Testing**: Write comprehensive tests for all functionality
8. **Documentation**: Document inputs, outputs, and algorithms clearly

## Environment Variables

- `HLA_COMPASS_ENV`: Default environment (dev, staging, prod)
- `HLA_COMPASS_CONFIG_DIR`: Configuration directory (default: ~/.hla-compass)
- `HLA_COMPASS_LOG_LEVEL`: Logging level (DEBUG, INFO, WARNING, ERROR)

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure all dependencies are in requirements.txt
2. **Timeout Errors**: Increase timeout in manifest.json or optimize code
3. **Memory Errors**: Process data in smaller chunks or increase memory
4. **Authentication Errors**: Run `hla-compass auth login` to refresh tokens

### Debug Mode

Enable debug logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Support

- **Complete Guide**: [/docs/MODULE_DEVELOPMENT_GUIDE.md](https://github.com/AlitheaBio/HLA-Compass-platform/blob/main/docs/MODULE_DEVELOPMENT_GUIDE.md)
- **Examples**: [/modules/examples/](https://github.com/AlitheaBio/HLA-Compass-platform/tree/main/modules/examples)
- **Issues**: [GitHub Issues](https://github.com/AlitheaBio/HLA-Compass-platform/issues)
- **Quick Start**: [/docs/MODULE_QUICKSTART.md](https://github.com/AlitheaBio/HLA-Compass-platform/blob/main/docs/MODULE_QUICKSTART.md)

## License

Copyright © 2024 Alithea Bio. All rights reserved.
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

### 1. Create a New Module

```bash
hla-compass init my-module --type no-ui --compute lambda
cd my-module
```

### 2. Implement Your Module

```python
# backend/main.py
from hla_compass import Module

class MyModule(Module):
    def execute(self, input_data, context):
        # Access peptide data
        peptides = self.peptides.search(
            sequence=input_data.get('sequence'),
            min_length=9,
            max_length=11
        )
        
        # Process data
        results = []
        for peptide in peptides:
            result = self.analyze_peptide(peptide)
            results.append(result)
        
        # Return results
        return self.success(results, summary={
            'total_peptides': len(peptides),
            'analyzed': len(results)
        })
    
    def analyze_peptide(self, peptide):
        # Your analysis logic here
        return {
            'peptide_id': peptide['id'],
            'sequence': peptide['sequence'],
            'score': 0.95
        }
```

### 3. Test Your Module

```bash
# Test locally
hla-compass test --local

# Test with custom input
hla-compass test --input examples/sample_input.json

# Run benchmarks
hla-compass test --benchmark
```

### 4. Build and Deploy

```bash
# Build module package
hla-compass build

# Deploy to development
hla-compass deploy dist/my-module-1.0.0.zip --env dev
```

## Module Development

### Base Module Class

All modules should inherit from the `Module` base class:

```python
from hla_compass import Module

class MyModule(Module):
    def execute(self, input_data, context):
        # Module logic here
        pass
```

### Data Access

The SDK provides convenient data access classes:

```python
# Search peptides
peptides = self.peptides.search(
    sequence="MLLSVPLLL",
    min_length=9,
    max_length=11,
    limit=100
)

# Get protein information
proteins = self.proteins.search(
    gene_name="HLA-A",
    organism="Homo sapiens"
)

# Access sample data
samples = self.samples.search(
    tissue="lung",
    disease="cancer"
)
```

### Storage

Save results to S3:

```python
# Save JSON
url = self.storage.save_json("results.json", {
    'peptides': results,
    'metadata': metadata
})

# Save CSV
import pandas as pd
df = pd.DataFrame(results)
url = self.storage.save_csv("results.csv", df)

# Save figure
import matplotlib.pyplot as plt
fig, ax = plt.subplots()
ax.plot(data)
url = self.storage.save_figure("plot.png", fig)
```

### Error Handling

Use the built-in error handling:

```python
from hla_compass import ValidationError, ModuleError

class MyModule(Module):
    def execute(self, input_data, context):
        # Validation
        if 'sequence' not in input_data:
            raise ValidationError("Missing required field: sequence")
        
        # Module errors
        try:
            result = complex_calculation(input_data)
        except CalculationError as e:
            self.error("Calculation failed", details={'error': str(e)})
        
        return self.success(result)
```

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

- Documentation: https://docs.hla-compass.com/sdk/python
- Examples: https://github.com/hla-compass/python-sdk-examples
- Issues: https://github.com/hla-compass/python-sdk/issues
- Email: sdk-support@hla-compass.com

## License

Copyright © 2024 Alithea Bio. All rights reserved.
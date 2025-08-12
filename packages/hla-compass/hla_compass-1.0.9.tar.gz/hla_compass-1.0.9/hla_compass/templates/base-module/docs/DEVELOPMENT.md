# Development Guide - Simple Peptide Analyzer Template

This guide helps you customize and extend the Simple Peptide Analyzer template for your specific needs.

## Quick Start for Developers

### 1. Template Setup

```bash
# Clone/copy the template
git clone https://github.com/YOUR_USERNAME/simple-analyzer-template.git my-analyzer
cd my-analyzer

# Set up development environment
make dev-setup

# Verify everything works
make test
make run
```

### 2. Customize for Your Module

1. **Update Module Identity:**
   - Edit `manifest.json`: Change name, description, author
   - Update `README.md` with your module details
   - Modify `backend/main.py`: Update MODULE_NAME and version

2. **Implement Your Analysis:**
   - Replace the peptide analysis logic in `analyze_peptide()`
   - Add your custom calculations
   - Update input/output schemas in `manifest.json`

3. **Update Examples:**
   - Modify `examples/sample_input.json` with realistic data
   - Generate `examples/sample_output.json` with your analysis results

4. **Test Your Changes:**
   ```bash
   make test        # Run comprehensive tests
   make run         # Test with sample data
   make docker-test # Test in containerized environment
   ```

## Architecture Overview

### Module Structure

```
simple-analyzer-template/
├── backend/                  # Core module code
│   ├── main.py              # Main entry point and analysis logic
│   ├── requirements.txt     # Python dependencies
│   └── tests/
│       └── test_main.py     # Comprehensive test suite
├── examples/                # Sample data and outputs
│   ├── sample_input.json    # Example input format
│   └── sample_output.json   # Example output format
├── docs/                    # Documentation
│   ├── API.md              # API documentation
│   └── DEVELOPMENT.md      # This file
├── .github/workflows/      # GitHub Actions CI/CD
│   └── ci.yml             # Automated testing pipeline
├── manifest.json          # Module metadata and schema
├── Dockerfile            # Multi-stage container builds
├── Makefile             # Development automation
├── README.md            # Main documentation
├── LICENSE              # MIT license
└── .gitignore          # Git ignore rules
```

### Code Organization

#### `backend/main.py`

The main module is organized into distinct sections:

1. **Module Metadata:** Constants and configuration
2. **Data Definitions:** Amino acid properties and scientific constants  
3. **Main Interface:** `execute()` function for platform integration
4. **Input Validation:** Comprehensive validation with clear error messages
5. **Analysis Functions:** Core scientific calculations
6. **Utility Functions:** Helper functions for common operations
7. **Error Handling:** Standardized error responses
8. **Testing Interface:** Local execution for development

#### Key Design Patterns

1. **Separation of Concerns:** Distinct functions for different calculations
2. **Comprehensive Validation:** Input validation before processing
3. **Error Recovery:** Graceful handling of individual peptide failures
4. **Performance Optimization:** Efficient algorithms and batch processing
5. **Extensive Logging:** Detailed logging for debugging and monitoring

## Customization Guide

### Adding New Analysis Features

#### 1. Add New Calculations

```python
def calculate_custom_property(sequence: str) -> float:
    """
    Add your custom peptide property calculation.
    
    Args:
        sequence: Amino acid sequence
        
    Returns:
        Calculated property value
    """
    # Your calculation logic here
    result = 0.0
    for aa in sequence:
        result += CUSTOM_AA_PROPERTIES.get(aa, 0)
    
    return result
```

#### 2. Integrate into Analysis Pipeline

```python
def analyze_peptide(sequence: str, **options) -> Dict[str, Any]:
    # ... existing code ...
    
    # Add your custom property
    if options.get('include_custom_analysis', False):
        result['custom_property'] = calculate_custom_property(sequence)
        result['custom_classification'] = classify_custom_property(
            result['custom_property']
        )
    
    return result
```

#### 3. Update Input Schema

Add to `manifest.json`:

```json
{
  "inputs": {
    "include_custom_analysis": {
      "type": "boolean",
      "required": false,
      "default": false,
      "description": "Include custom property analysis"
    }
  }
}
```

#### 4. Update Output Schema

Add to `manifest.json`:

```json
{
  "outputs": {
    "peptide_properties": {
      "items": {
        "properties": {
          "custom_property": {
            "type": "number",
            "description": "Your custom property value"
          }
        }
      }
    }
  }
}
```

### Adding External Dependencies

#### 1. Update Requirements

Add to `backend/requirements.txt`:

```txt
# Your new dependency
scikit-learn>=1.0.0,<2.0.0
biopython>=1.79,<2.0.0
```

#### 2. Update Docker Build

If binary dependencies are needed, update `Dockerfile`:

```dockerfile
# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libssl-dev \
    your-system-package \
    && rm -rf /var/lib/apt/lists/*
```

#### 3. Update CI Pipeline

Add to `.github/workflows/ci.yml`:

```yaml
- name: Install system dependencies
  run: |
    sudo apt-get update
    sudo apt-get install -y your-system-package
```

### Modifying Input/Output Formats

#### 1. Change Input Structure

```python
def validate_inputs(input_data: Dict[str, Any]) -> Dict[str, Any]:
    # Add validation for new input fields
    if 'new_parameter' in input_data:
        if not isinstance(input_data['new_parameter'], expected_type):
            return {
                'valid': False, 
                'error': 'new_parameter must be of type expected_type'
            }
    
    return {'valid': True}
```

#### 2. Modify Output Structure

```python
def analyze_peptide(sequence: str, **options) -> Dict[str, Any]:
    result = {
        'sequence': sequence,
        'new_output_field': calculate_new_output(sequence)
    }
    
    # Group related outputs
    result['advanced_analysis'] = {
        'property_1': calculate_property_1(sequence),
        'property_2': calculate_property_2(sequence)
    }
    
    return result
```

### Performance Optimization

#### 1. Batch Processing

```python
def analyze_peptides_batch(sequences: List[str], **options) -> List[Dict]:
    """Process multiple sequences efficiently."""
    import numpy as np
    
    # Vectorized calculations where possible
    lengths = np.array([len(seq) for seq in sequences])
    
    results = []
    for i, sequence in enumerate(sequences):
        result = {
            'sequence': sequence,
            'length': int(lengths[i])  # Pre-calculated
        }
        # Add other calculations...
        results.append(result)
    
    return results
```

#### 2. Caching Expensive Calculations

```python
from functools import lru_cache

@lru_cache(maxsize=1000)
def expensive_calculation(sequence: str) -> float:
    """Cache results for repeated sequences."""
    # Expensive calculation here
    return result
```

#### 3. Progress Reporting

```python
def execute(input_data: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
    sequences = input_data['peptide_sequences']
    
    for i, sequence in enumerate(sequences):
        # Process sequence...
        
        # Log progress for large batches
        if len(sequences) > 100 and (i + 1) % 50 == 0:
            logger.info(f"Processed {i + 1}/{len(sequences)} sequences")
```

## Testing Your Module

### Unit Testing Strategy

#### 1. Test Categories

1. **Input Validation Tests:** All possible input scenarios
2. **Calculation Tests:** Scientific accuracy of algorithms
3. **Integration Tests:** End-to-end module execution
4. **Error Handling Tests:** Graceful failure scenarios
5. **Performance Tests:** Speed and memory usage

#### 2. Adding New Tests

```python
def test_custom_calculation():
    """Test your custom calculation function."""
    # Test with known input/output
    result = calculate_custom_property('TEST')
    expected = 42.0
    assert abs(result - expected) < 0.001
    
    # Test edge cases
    assert calculate_custom_property('') == 0.0
    
    # Test with all amino acids
    all_aa_sequence = ''.join(AA_PROPERTIES.keys())
    result = calculate_custom_property(all_aa_sequence)
    assert result > 0
```

#### 3. Integration Testing

```python
def test_custom_integration():
    """Test end-to-end execution with custom features."""
    input_data = {
        'peptide_sequences': ['TESTPEPTIDE'],
        'include_custom_analysis': True
    }
    
    result = execute(input_data, {'job_id': 'test'})
    
    assert result['status'] == 'success'
    peptide = result['peptide_properties'][0]
    assert 'custom_property' in peptide
```

### Performance Testing

```python
def test_large_batch_performance():
    """Test performance with large batches."""
    import time
    
    # Generate test data
    sequences = ['TESTPEPTIDE'] * 1000
    input_data = {'peptide_sequences': sequences}
    
    start_time = time.time()
    result = execute(input_data, {'job_id': 'perf-test'})
    execution_time = time.time() - start_time
    
    assert result['status'] == 'success'
    assert execution_time < 30.0  # Should complete within 30 seconds
    
    # Check throughput
    throughput = len(sequences) / execution_time
    assert throughput > 30  # At least 30 sequences/second
```

### Testing with Docker

```bash
# Test in clean environment
make docker-test

# Interactive testing
make docker-shell
cd backend && python main.py

# Performance testing
make docker-build
docker run --rm your-module:latest pytest backend/tests/ --benchmark-only
```

## Deployment Strategies

### 1. HLA-Compass Platform

```bash
# Package for HLA-Compass
make package

# Deploy (when SDK is available)
hla-compass auth login --env dev
hla-compass deploy simple-analyzer-1.0.0.zip --env dev
```

### 2. AWS Lambda

```bash
# Build Lambda-optimized image
make docker-build-lambda

# Deploy with AWS CLI
aws lambda create-function \
  --function-name my-peptide-analyzer \
  --package-type Image \
  --code ImageUri=your-account.dkr.ecr.region.amazonaws.com/my-analyzer:lambda \
  --role arn:aws:iam::your-account:role/lambda-role \
  --timeout 300 \
  --memory-size 512
```

### 3. Standalone Service

```bash
# Build production image
make docker-build-prod

# Run as service
docker run -d \
  --name peptide-analyzer \
  -p 8080:8080 \
  -e PORT=8080 \
  your-module:prod
```

## Best Practices

### 1. Code Quality

- **Type hints:** Use type annotations throughout
- **Docstrings:** Document all functions with examples
- **Error handling:** Provide clear error messages
- **Logging:** Use appropriate log levels
- **Testing:** Maintain >90% test coverage

### 2. Performance

- **Vectorization:** Use NumPy for numerical operations
- **Memory efficiency:** Process data in chunks if needed
- **Caching:** Cache expensive calculations
- **Profiling:** Regularly profile your code

### 3. Security

- **Input validation:** Validate all inputs thoroughly
- **Dependencies:** Keep dependencies updated
- **Secrets:** Never hardcode sensitive data
- **Logging:** Don't log sensitive information

### 4. Documentation

- **README:** Keep main documentation current
- **API docs:** Document all inputs/outputs
- **Examples:** Provide realistic usage examples
- **Changelog:** Track changes between versions

## Troubleshooting

### Common Issues

#### 1. Import Errors

```bash
# Check Python path
export PYTHONPATH=$PWD/backend:$PYTHONPATH

# Or modify sys.path in tests
import sys
sys.path.insert(0, 'backend')
```

#### 2. Docker Build Failures

```bash
# Clean build
make docker-clean
make docker-build

# Debug build
docker build --no-cache -t debug-build .
```

#### 3. Test Failures

```bash
# Run specific test
pytest backend/tests/test_main.py::test_function_name -v

# Debug with print statements
pytest backend/tests/ -v -s

# Check coverage
pytest backend/tests/ --cov=backend --cov-report=html
open htmlcov/index.html
```

#### 4. Performance Issues

```bash
# Profile your code
python -m cProfile backend/main.py

# Memory profiling
pip install memory_profiler
python -m memory_profiler backend/main.py
```

### Getting Help

1. **Check logs:** Look at execution logs for errors
2. **Run tests:** Use test suite to identify issues
3. **Use Docker:** Test in clean container environment
4. **Profile performance:** Identify bottlenecks
5. **Review documentation:** Check API docs for requirements

## Contributing to the Template

If you improve the template, consider contributing back:

1. Fork the template repository
2. Make your improvements
3. Add tests for new features
4. Update documentation
5. Submit a pull request

### Areas for Improvement

- Additional scientific calculations
- Performance optimizations
- Better error handling
- More comprehensive examples
- Enhanced documentation
- Additional deployment targets

## Advanced Topics

### Custom Validation Rules

```python
def validate_peptide_sequence(sequence: str) -> bool:
    """Custom validation beyond basic AA checking."""
    # Check for minimum length
    if len(sequence) < 6:
        return False
    
    # Check for maximum hydrophobicity
    hydrophobicity = calculate_hydrophobicity(sequence)
    if hydrophobicity > 50:  # Custom threshold
        return False
    
    return True
```

### Parallel Processing

```python
from concurrent.futures import ThreadPoolExecutor
import multiprocessing

def analyze_peptides_parallel(sequences: List[str], **options) -> List[Dict]:
    """Process sequences in parallel."""
    max_workers = min(multiprocessing.cpu_count(), len(sequences))
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [
            executor.submit(analyze_peptide, seq, **options) 
            for seq in sequences
        ]
        results = [future.result() for future in futures]
    
    return results
```

### Machine Learning Integration

```python
import joblib

def load_ml_model():
    """Load pre-trained ML model."""
    return joblib.load('models/peptide_classifier.pkl')

def predict_immunogenicity(sequence: str, model=None) -> float:
    """Predict peptide immunogenicity using ML."""
    if model is None:
        model = load_ml_model()
    
    features = extract_features(sequence)
    prediction = model.predict_proba([features])[0][1]
    
    return float(prediction)
```

This template provides a solid foundation for developing production-ready HLA-Compass modules. Customize it to meet your specific analysis needs while maintaining the established patterns for reliability, performance, and maintainability.
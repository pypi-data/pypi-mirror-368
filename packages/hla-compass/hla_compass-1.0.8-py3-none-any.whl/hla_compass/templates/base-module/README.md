# Simple Peptide Analyzer - HLA-Compass Module Template

[![CI](https://github.com/YOUR_USERNAME/simple-analyzer-template/actions/workflows/ci.yml/badge.svg)](https://github.com/YOUR_USERNAME/simple-analyzer-template/actions/workflows/ci.yml)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/release/python-380/)
[![HLA-Compass](https://img.shields.io/badge/HLA--Compass-compatible-green.svg)](https://hla-compass.com)

A production-ready template for developing external modules for the HLA-Compass bioinformatics platform. This template provides a complete, standalone repository structure for developing peptide analysis modules.

## Quick Start

### 1. Create Your Repository

```bash
# Option A: Use GitHub template (recommended)
# Click "Use this template" on GitHub to create your own repository

# Option B: Clone and customize
git clone https://github.com/YOUR_USERNAME/simple-analyzer-template.git my-peptide-module
cd my-peptide-module
rm -rf .git
git init
git remote add origin https://github.com/YOUR_USERNAME/my-peptide-module.git
```

### 2. Set Up Development Environment

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r backend/requirements.txt

# Install development dependencies
pip install pytest pytest-cov black isort
```

### 3. Test the Template

```bash
# Run unit tests
make test

# Test locally with sample data
make test-local

# Run in Docker (optional)
make test-docker
```

### 4. Customize for Your Module

1. **Update `manifest.json`**: Change name, description, author details
2. **Modify `backend/main.py`**: Implement your analysis logic
3. **Update `examples/`**: Provide realistic sample input/output
4. **Edit this `README.md`**: Document your specific module
5. **Configure GitHub Actions**: Update repository name in `.github/workflows/ci.yml`

## What's Included

This template provides a complete, production-ready structure:

```
simple-analyzer-template/
├── README.md                    # This file
├── LICENSE                      # MIT License
├── .gitignore                   # Python/IDE gitignore
├── Makefile                     # Common development tasks
├── Dockerfile                   # Container for testing/deployment
├── manifest.json                # Module metadata and configuration
├── .github/
│   └── workflows/
│       └── ci.yml              # GitHub Actions CI/CD pipeline
├── backend/
│   ├── main.py                 # Main module implementation
│   ├── requirements.txt        # Python dependencies
│   └── tests/
│       └── test_main.py        # Unit tests
├── examples/
│   ├── sample_input.json       # Example input data
│   └── sample_output.json      # Expected output format
└── docs/
    ├── API.md                  # API documentation
    └── DEVELOPMENT.md          # Development guide
```

## Features

### Module Implementation
- **Complete peptide analyzer**: Calculates molecular weight, isoelectric point, hydrophobicity, instability index
- **Comprehensive validation**: Input validation with clear error messages  
- **Batch processing**: Efficiently handles up to 1000 peptides per analysis
- **Configurable analysis**: Optional hydropathy and charge distribution calculations
- **Summary statistics**: Automatic generation of aggregate statistics

### Development Tools
- **Unit testing**: Complete test suite with pytest
- **Code quality**: Black formatting and isort import sorting
- **Docker support**: Containerized testing environment
- **Makefile**: Common development tasks automated
- **GitHub Actions**: Automated CI/CD pipeline

### Production Ready
- **Error handling**: Robust error handling and logging
- **Performance optimized**: Efficient algorithms for large datasets
- **Documentation**: Complete API and development documentation
- **Extensible design**: Easy to modify and extend

## Module Structure

### Input Format

```json
{
  "peptide_sequences": ["SIINFEKL", "GILGFVFTL", "YLQPRTFLL"],
  "include_hydropathy": true,
  "include_charge_distribution": false
}
```

### Output Format

```json
{
  "status": "success",
  "peptide_properties": [
    {
      "sequence": "SIINFEKL",
      "length": 8,
      "molecular_weight": 961.12,
      "isoelectric_point": 9.52,
      "net_charge_ph7": 1.02,
      "hydrophobicity": 1.6,
      "gravy": 0.2,
      "aromaticity": 0.125,
      "instability_index": 28.45
    }
  ],
  "summary": {
    "total_peptides": 3,
    "valid_peptides": 3,
    "average_length": 8.3,
    "average_mw": 1045.67,
    "amino_acid_frequency": {"S": 0.12, "I": 0.16, ...}
  }
}
```

## Development Guide

### Running Tests

```bash
# Run all tests
make test

# Run tests with coverage
make test-coverage

# Run specific test
pytest backend/tests/test_main.py::test_peptide_analysis -v
```

### Local Development

```bash
# Test with sample data
python backend/main.py

# Format code
make format

# Lint code
make lint
```

### Docker Development

```bash
# Build container
make docker-build

# Run tests in container
make docker-test

# Interactive shell
make docker-shell
```

## Deployment

### HLA-Compass Platform

```bash
# Install HLA-Compass CLI (when available)
pip install hla-compass

# Authenticate
hla-compass auth login --env dev

# Build and deploy
hla-compass build
hla-compass deploy dist/simple-analyzer-1.0.0.zip --env dev
```

### Standalone Deployment

```bash
# Create deployment package
make build

# Deploy to AWS Lambda (example)
aws lambda create-function \
  --function-name simple-peptide-analyzer \
  --runtime python3.11 \
  --zip-file fileb://dist/simple-analyzer-1.0.0.zip \
  --handler main.execute
```

## Customization Guide

### 1. Basic Information

Update `manifest.json` with your module details:

```json
{
  "name": "my-amazing-analyzer",
  "displayName": "My Amazing Peptide Analyzer",
  "description": "Your custom description here",
  "author": {
    "name": "Your Name",
    "email": "you@company.com",
    "organization": "Your Organization"
  }
}
```

### 2. Modify Analysis Logic

Edit `backend/main.py` to implement your specific analysis:

```python
def analyze_peptide(sequence: str, **kwargs) -> Dict[str, Any]:
    """
    Customize this function with your analysis logic.
    """
    result = {
        'sequence': sequence,
        'length': len(sequence)
    }
    
    # Add your custom analysis here
    result['custom_score'] = calculate_custom_score(sequence)
    
    return result
```

### 3. Add Dependencies

Update `backend/requirements.txt` with any additional libraries:

```txt
numpy>=1.21.0
pandas>=1.3.0
biopython>=1.79
scikit-learn>=1.0.0  # Add new dependencies here
```

### 4. Configure CI/CD

Update `.github/workflows/ci.yml` with your repository details:

```yaml
name: CI
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]
```

## Testing Your Module

### Unit Tests

The template includes comprehensive unit tests:

```python
def test_peptide_analysis():
    """Test basic peptide analysis functionality."""
    input_data = {
        'peptide_sequences': ['SIINFEKL', 'GILGFVFTL'],
        'include_hydropathy': True
    }
    
    result = execute(input_data, {})
    
    assert result['status'] == 'success'
    assert len(result['peptide_properties']) == 2
    assert 'summary' in result
```

### Integration Tests

Test with realistic data:

```python
def test_with_large_dataset():
    """Test module with larger dataset."""
    sequences = generate_test_sequences(100)
    input_data = {'peptide_sequences': sequences}
    
    result = execute(input_data, {})
    
    assert result['status'] == 'success'
    assert len(result['peptide_properties']) == 100
```

## Performance Considerations

### Memory Usage
- Processes batches of up to 1000 peptides
- Memory usage scales linearly with input size
- Typical usage: ~50MB for 1000 peptides

### Execution Time
- ~10ms per peptide for basic analysis
- ~15ms per peptide with full analysis
- Batch processing reduces per-peptide overhead

### Optimization Tips
1. **Use vectorized operations**: NumPy arrays for bulk calculations
2. **Cache expensive computations**: Memoize repeated calculations
3. **Process in chunks**: For very large datasets
4. **Profile your code**: Use `cProfile` to identify bottlenecks

## API Reference

### Main Function

```python
def execute(input_data: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Main entry point for the module.
    
    Args:
        input_data: Input parameters and data
        context: Execution context (job_id, user_id, etc.)
        
    Returns:
        Analysis results and metadata
    """
```

### Validation Function

```python
def validate_inputs(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate input parameters.
    
    Returns:
        {'valid': bool, 'error': str}
    """
```

### Analysis Functions

```python
def analyze_peptide(sequence: str, **options) -> Dict[str, Any]:
    """Analyze a single peptide sequence."""

def calculate_molecular_weight(sequence: str) -> float:
    """Calculate peptide molecular weight."""

def calculate_isoelectric_point(sequence: str) -> float:
    """Calculate isoelectric point using bisection method."""
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for new functionality
5. Run the test suite (`make test`)
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- **Documentation**: See `docs/` directory
- **Issues**: GitHub Issues
- **Email**: modules@company.com (update with your contact)
- **HLA-Compass Platform**: https://hla-compass.com

## Acknowledgments

- Built for the HLA-Compass bioinformatics platform
- Peptide analysis algorithms based on established biophysical methods
- Thanks to the open-source bioinformatics community

---

**Ready to build your own module?** Start by customizing the analysis logic in `backend/main.py` and update the examples with your specific use case.
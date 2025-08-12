# Simple Peptide Analyzer - API Documentation

This document provides detailed API documentation for the Simple Peptide Analyzer module.

## Overview

The Simple Peptide Analyzer is a comprehensive biophysical analysis module that calculates essential properties of peptide sequences. It's designed as a template for developing HLA-Compass modules with best practices for validation, error handling, and performance.

## Main Entry Point

### `execute(input_data, context)`

The primary interface function called by the HLA-Compass platform.

**Parameters:**
- `input_data` (Dict[str, Any]): Input parameters and data
- `context` (Dict[str, Any]): Execution context

**Returns:**
- `Dict[str, Any]`: Analysis results or error response

**Example:**
```python
from main import execute

input_data = {
    'peptide_sequences': ['SIINFEKL', 'GILGFVFTL'],
    'include_hydropathy': True,
    'include_charge_distribution': False
}
context = {'job_id': 'test-123'}

result = execute(input_data, context)
```

## Input Schema

### Required Parameters

#### `peptide_sequences`
- **Type:** `Array[string]`
- **Required:** Yes
- **Description:** Array of peptide sequences in single-letter amino acid code
- **Constraints:**
  - Minimum 1 sequence, maximum 1000 sequences per batch
  - Each sequence: 1-10,000 amino acids
  - Valid characters: `ACDEFGHIKLMNPQRSTVWY`
- **Example:** `["SIINFEKL", "GILGFVFTL", "YLQPRTFLL"]`

### Optional Parameters

#### `include_hydropathy`
- **Type:** `boolean`
- **Required:** No
- **Default:** `true`
- **Description:** Include hydropathy analysis (hydrophobicity, GRAVY, classification)
- **Example:** `true`

#### `include_charge_distribution`
- **Type:** `boolean`
- **Required:** No
- **Default:** `false`
- **Description:** Calculate charge distribution at pH 3.0, 5.0, 7.0, 9.0, 11.0
- **Example:** `true`

## Output Schema

### Success Response

```json
{
  "status": "success",
  "peptide_properties": [...],
  "summary": {...},
  "metadata": {...}
}
```

### Error Response

```json
{
  "status": "error", 
  "error": "Error description",
  "timestamp": "2024-01-15T10:30:45.123456",
  "metadata": {...}
}
```

## Peptide Properties

Each analyzed peptide returns the following properties:

### Core Properties (Always Included)

| Property | Type | Description |
|----------|------|-------------|
| `sequence` | string | Original peptide sequence |
| `length` | integer | Number of amino acids |
| `molecular_weight` | number | Molecular weight in Daltons |
| `isoelectric_point` | number | pH at which net charge is zero |
| `net_charge_ph7` | number | Net charge at physiological pH |
| `aromaticity` | number | Fraction of aromatic residues (0.0-1.0) |
| `instability_index` | number | Instability prediction (>40 = unstable) |
| `stability_classification` | string | "stable" or "unstable" |
| `composition` | object | Amino acid percentages |

### Hydropathy Properties (if `include_hydropathy=true`)

| Property | Type | Description |
|----------|------|-------------|
| `hydrophobicity` | number | Total hydrophobicity (Kyte-Doolittle) |
| `gravy` | number | Grand Average of Hydropathy |
| `hydropathy_class` | string | "hydrophobic", "hydrophilic", or "neutral" |

### Charge Properties (if `include_charge_distribution=true`)

| Property | Type | Description |
|----------|------|-------------|
| `charge_distribution` | object | Net charge at pH 3.0, 5.0, 7.0, 9.0, 11.0 |
| `charge_analysis` | object | Charge analysis summary |

## Summary Statistics

The `summary` object provides aggregate statistics:

### Basic Statistics
- `total_peptides`: Total sequences submitted
- `valid_peptides`: Successfully analyzed sequences  
- `error_count`: Failed analyses
- `success_rate`: Fraction successfully analyzed

### Length Statistics
- `min`, `max`, `mean`, `median`: Length distribution
- `distribution`: Histogram of lengths

### Property Averages
- `isoelectric_point`: Average pI
- `net_charge_ph7`: Average charge at pH 7
- `aromaticity`: Average aromaticity
- `instability_index`: Average instability

### Stability Analysis
- `stable_count`: Number of stable peptides
- `unstable_count`: Number of unstable peptides
- `percent_unstable`: Percentage unstable

### Composition Analysis
- `amino_acid_frequency`: Overall AA frequencies

## Core Functions

### Input Validation

#### `validate_inputs(input_data)`

Comprehensive input validation with detailed error reporting.

**Parameters:**
- `input_data` (Dict): Input data to validate

**Returns:**
- `Dict[str, Any]`: `{'valid': bool, 'error': str}`

**Validation Rules:**
1. `input_data` must be a dictionary
2. `peptide_sequences` is required and must be a list
3. Sequences must be non-empty strings with valid amino acids
4. Maximum 1000 sequences per batch
5. Boolean parameters must be actual booleans

### Peptide Analysis

#### `analyze_peptide(sequence, include_hydropathy=True, include_charge_distribution=False)`

Analyze a single peptide sequence.

**Parameters:**
- `sequence` (str): Amino acid sequence
- `include_hydropathy` (bool): Include hydropathy calculations
- `include_charge_distribution` (bool): Include charge distribution

**Returns:**
- `Dict[str, Any]`: Complete analysis results

**Raises:**
- `ValueError`: If sequence is empty
- `RuntimeError`: If analysis calculations fail

### Molecular Weight Calculation

#### `calculate_molecular_weight(sequence)`

Calculate peptide molecular weight accounting for peptide bonds.

**Formula:** Sum of amino acid weights minus (n-1) × 18.015 Da

**Parameters:**
- `sequence` (str): Amino acid sequence

**Returns:**
- `float`: Molecular weight in Daltons

### Charge Calculations

#### `calculate_net_charge(sequence, ph)`

Calculate net charge using Henderson-Hasselbalch equation.

**Parameters:**
- `sequence` (str): Amino acid sequence
- `ph` (float): pH value

**Returns:**
- `float`: Net charge at specified pH

#### `calculate_isoelectric_point(sequence)`

Calculate isoelectric point using bisection method.

**Parameters:**
- `sequence` (str): Amino acid sequence

**Returns:**
- `float`: Isoelectric point (pH where net charge = 0)

### Hydrophobicity Calculations

#### `calculate_hydrophobicity(sequence)`

Calculate total hydrophobicity using Kyte-Doolittle scale.

**Parameters:**
- `sequence` (str): Amino acid sequence

**Returns:**
- `float`: Total hydrophobicity value

### Other Calculations

#### `calculate_aromaticity(sequence)`

Calculate fraction of aromatic amino acids (F, W, Y).

#### `calculate_instability_index(sequence)`

Calculate instability index using Guruprasad method.

#### `calculate_aa_composition(sequence)`

Calculate amino acid composition as percentages.

## Error Handling

### Error Types

1. **ValidationError**: Invalid input parameters
2. **AnalysisError**: Calculation failures
3. **TimeoutError**: Execution time limits
4. **MemoryError**: Insufficient memory

### Error Response Format

```json
{
  "status": "error",
  "error": "Human-readable error message",
  "timestamp": "ISO timestamp",
  "metadata": {
    "module_name": "simple-analyzer",
    "module_version": "1.0.0",
    "job_id": "job-id",
    "error_type": "ErrorClassName"
  }
}
```

## Performance Characteristics

### Throughput
- **Typical:** 100-200 peptides/second
- **Small peptides (<20 AA):** Up to 500/second  
- **Large peptides (>100 AA):** 50-100/second

### Memory Usage
- **Base:** ~10MB
- **Per peptide:** ~0.5KB
- **1000 peptides:** ~10.5MB total

### Execution Time
- **Single peptide:** 1-5ms
- **100 peptides:** 0.5-2 seconds
- **1000 peptides:** 5-20 seconds

## Limitations

1. **Maximum batch size:** 1000 sequences
2. **Maximum sequence length:** 10,000 amino acids
3. **Execution timeout:** 300 seconds
4. **Memory limit:** 512MB
5. **Valid amino acids:** Standard 20 amino acids only

## Examples

### Basic Analysis

```python
input_data = {
    'peptide_sequences': ['SIINFEKL']
}
result = execute(input_data, {'job_id': 'basic'})
```

### Full Analysis

```python
input_data = {
    'peptide_sequences': ['SIINFEKL', 'GILGFVFTL'],
    'include_hydropathy': True,
    'include_charge_distribution': True
}
result = execute(input_data, {'job_id': 'full'})
```

### Batch Processing

```python
sequences = ['PEPTIDE' + str(i) for i in range(100)]
input_data = {
    'peptide_sequences': sequences,
    'include_hydropathy': False,
    'include_charge_distribution': False
}
result = execute(input_data, {'job_id': 'batch'})
```

## Integration Notes

### HLA-Compass Platform

This module is designed to integrate seamlessly with the HLA-Compass platform:

1. **Authentication:** Handled by platform
2. **Input validation:** Comprehensive built-in validation
3. **Error reporting:** Standardized error responses
4. **Logging:** CloudWatch integration ready
5. **Monitoring:** Performance metrics included

### AWS Lambda Deployment

- **Runtime:** Python 3.11
- **Memory:** 512MB recommended
- **Timeout:** 300 seconds
- **Handler:** `backend.main.execute`

### Custom Deployments

The module can run in any Python environment with minimal dependencies:
- Python 3.8+
- numpy (optional)
- pandas (optional)
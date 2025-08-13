# Peptide Analyzer Module

A ready-to-run HLA-Compass module that analyzes peptide sequences, searches for similar peptides in the database, and predicts HLA binding affinity.

## Features

- **Sequence Analysis**: Calculate molecular weight, hydrophobicity, and amino acid composition
- **Database Search**: Find similar peptides in the HLA-Compass database
- **HLA Binding Prediction**: Predict binding affinity for common HLA alleles
- **Interactive UI**: Beautiful interface built with Ant Design components
- **Export Results**: Download analysis results as JSON
- **Local Development**: Complete with database and web server

## Quick Start - ONE COMMAND!

```bash
# Make executable if needed
chmod +x run.sh

# Just run this:
./run.sh

# That's it! Browser opens at http://localhost:3333
```

This single command:
- ✅ Starts PostgreSQL with peptide data
- ✅ Installs dependencies
- ✅ Starts web server on port 3333
- ✅ Opens your browser automatically

## Alternative Testing Methods

```bash
# Test backend only
hla-compass test --local --input examples/sample_input.json

# Build package for deployment
hla-compass build

# Deploy to platform
hla-compass deploy dist/peptide-analyzer-1.0.0.zip --env dev
```

## Input Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| sequence | string | Yes | Peptide sequence (7-15 amino acids) |
| hla_allele | string | No | HLA allele for binding prediction (default: HLA-A*02:01) |
| limit | integer | No | Max similar peptides to return (default: 10) |

## Output Structure

```json
{
  "analysis": {
    "sequence": "SIINFEKL",
    "length": 8,
    "molecular_weight": 963.12,
    "hydrophobicity": 50.0,
    "charge_ratio": 12.5,
    "composition": {"S": 1, "I": 2, "N": 1, "F": 1, "E": 1, "K": 1, "L": 1}
  },
  "similar_peptides": [
    {
      "sequence": "SIINFEKL",
      "length": 8,
      "molecular_weight": 963.12,
      "source": "OVA",
      "similarity": 100.0
    }
  ],
  "predictions": {
    "hla_allele": "HLA-A*02:01",
    "score": 85.0,
    "binding_class": "Strong Binder",
    "percentile_rank": 15.0
  }
}
```

## Module Architecture

### Backend (`backend/main.py`)
- `PeptideAnalyzer` class with complete implementation
- Sequence validation and analysis
- Database integration for similar peptide search
- Simplified HLA binding prediction
- Error handling and logging

### Frontend (`frontend/index.tsx`)
- React component using Ant Design
- Form validation with real-time feedback
- Interactive results display
- Data export functionality
- Responsive layout

## Supported HLA Alleles

- HLA-A*02:01 (default)
- HLA-A*01:01
- HLA-A*03:01
- HLA-A*24:02
- HLA-B*07:02
- HLA-B*08:01
- HLA-B*27:05
- HLA-B*35:01
- HLA-C*07:01
- HLA-C*07:02

## Testing Examples

```bash
# Test with OVA epitope
echo '{"sequence": "SIINFEKL", "hla_allele": "HLA-A*02:01"}' > test.json
hla-compass test --local --input test.json

# Test with influenza epitope
echo '{"sequence": "GILGFVFTL", "hla_allele": "HLA-A*02:01"}' > test2.json
hla-compass test --local --input test2.json

# Test with custom parameters
echo '{"sequence": "YLQPRTFLL", "hla_allele": "HLA-B*27:05", "limit": 20}' > test3.json
hla-compass test --local --input test3.json
```

## API Usage

Once deployed, you can call the module via API:

```python
import requests

response = requests.post(
    "https://api.hla-compass.com/v1/modules/peptide-analyzer/execute",
    json={
        "sequence": "SIINFEKL",
        "hla_allele": "HLA-A*02:01",
        "limit": 10
    },
    headers={"Authorization": "Bearer YOUR_TOKEN"}
)

results = response.json()
```

## Customization

To customize this module:

1. **Modify HLA Binding Logic**: Edit the `predict_hla_binding()` method in `backend/main.py`
2. **Add More Analyses**: Extend the `analyze_sequence()` method
3. **Customize UI**: Edit `frontend/index.tsx` to add more visualizations
4. **Add ML Models**: Integrate real binding prediction models

## Performance

- Sequence analysis: < 100ms
- Database search: < 500ms (depends on database size)
- Total execution time: < 1 second for typical queries

## Notes

- The HLA binding prediction is simplified for demonstration
- Real implementations would use machine learning models
- Database search uses the SDK's built-in peptide search
- All UI components align with HLA-Compass platform styling

## Support

For questions or issues:
- Documentation: https://docs.hla-compass.com
- Support: support@alithea.bio
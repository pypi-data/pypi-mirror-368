# HLA-Compass Module - Minimal Template

This is a minimal template for creating HLA-Compass modules. It provides empty scaffolding with TODO comments to guide your implementation.

## Quick Start

1. **Update Module Information**
   - Edit `manifest.json` with your module details
   - Update author information, description, and tags

2. **Implement Your Logic**
   - Edit `backend/main.py`
   - Replace TODO comments with your implementation
   - Add your processing logic in the `execute()` method

3. **Add Dependencies**
   - Edit `backend/requirements.txt`
   - Add any Python packages your module needs

4. **Test Your Module**
   ```bash
   # Test locally
   hla-compass test --local
   
   # Test with sample input
   hla-compass test --local --input examples/sample_input.json
   ```

5. **Build and Deploy**
   ```bash
   # Build package
   hla-compass build
   
   # Deploy to platform
   hla-compass deploy dist/*.zip --env dev
   ```

## Module Structure

```
your-module/
├── manifest.json           # Module metadata and configuration
├── backend/
│   ├── main.py            # Main module implementation (TODO: implement)
│   └── requirements.txt   # Python dependencies (TODO: add your deps)
├── examples/
│   └── sample_input.json  # Example input (TODO: add example)
├── docs/
│   └── README.md          # Module documentation (TODO: document)
└── README.md              # This file
```

## Key Functions to Implement

### `execute(input_data, context)`
This is the main function that processes input and returns results.

**TODO List:**
- [ ] Validate input parameters
- [ ] Implement your processing logic
- [ ] Handle errors gracefully
- [ ] Return structured results

### Available SDK Features

Your module has access to:
- `self.peptides` - Query peptide database
- `self.proteins` - Query protein database
- `self.samples` - Query samples database
- `self.storage` - Save/load files from S3
- `self.logger` - Log messages to CloudWatch
- `self.success()` - Return success response
- `self.error()` - Return error response

## Example Implementation

```python
def execute(self, input_data, context):
    # Get input parameter
    sequence = input_data.get('sequence', '')
    
    # Query database
    peptides = self.peptides.search(sequence=sequence, limit=10)
    
    # Process results
    results = [
        {
            'sequence': p.sequence,
            'length': p.length,
            'mw': p.molecular_weight
        }
        for p in peptides
    ]
    
    # Return success
    return self.success({
        'peptides': results,
        'count': len(results)
    })
```

## Next Steps

1. Replace all TODO comments with your implementation
2. Add proper input validation
3. Implement your core logic
4. Add error handling
5. Write tests
6. Document your module

## Running Locally

```bash
# Make executable if needed
chmod +x run.sh

# Run the server
./run.sh

# Opens at http://localhost:3333
```

## Need Help?

- SDK Documentation: https://docs.hla-compass.com/sdk
- API Reference: https://docs.hla-compass.com/api
- Support: support@alithea.bio
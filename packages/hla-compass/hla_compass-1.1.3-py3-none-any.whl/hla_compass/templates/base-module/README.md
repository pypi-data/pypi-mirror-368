# Base Module Template

A basic HLA-Compass module template with Ant Design UI components.

## Features

- ✅ Ant Design UI components (matches platform style)
- ✅ Simple backend structure with TODOs
- ✅ Local development server on port 3333
- ✅ Ready to customize

## Quick Start

```bash
# Run the module locally
./run.sh

# Or manually:
python3 server.py

# Browser opens at http://localhost:3333
```

**Note:** If `run.sh` is not executable, run: `chmod +x run.sh`

## File Structure

```
base-module/
├── backend/
│   ├── main.py           # Module logic (implement your code here)
│   └── requirements.txt  # Python dependencies
├── frontend/
│   ├── index.tsx         # React UI with Ant Design
│   └── package.json      # Node dependencies
├── server.py             # Development server
├── run.sh               # Quick start script
├── docker-compose.yml   # Optional database setup
└── manifest.json        # Module configuration
```

## Development

1. **Backend**: Edit `backend/main.py` to implement your module logic
2. **Frontend**: Edit `frontend/index.tsx` to customize the UI
3. **Test**: Run `./run.sh` and open http://localhost:3333

## Testing

```bash
# Test backend
hla-compass test --local

# Test with UI
./run.sh
```

## Build & Deploy

```bash
# Build module package
hla-compass build

# Deploy to platform
hla-compass deploy dist/*.zip --env dev
```

## Adding a Database

Uncomment the PostgreSQL section in `docker-compose.yml` if you need a database:

```bash
# Start database
docker-compose up -d

# Then run server
./run.sh
```

## UI Components

This template uses Ant Design components that match the HLA-Compass platform:
- Forms with validation
- Tables for results
- Cards for layout
- Buttons and inputs
- Loading states
- Error handling

## Next Steps

1. Implement your module logic in `backend/main.py`
2. Customize the UI in `frontend/index.tsx`
3. Add any required dependencies
4. Test locally with `./run.sh`
5. Deploy when ready
# doc-studio

AI-amplified interactive workspace for documentation generation, powered by doc-evergreen.

## Quick Start

### 1. Install Dependencies

From the doc-studio directory:

```bash
cd /path/to/amplifier/scenarios/doc_studio
make install
```

### 2. Run doc-studio for Your Repository

**Option A: Run from your repository** (recommended)

```bash
# Navigate to the repository you want to document
cd /path/to/your/project

# Start the backend (specify your repo as workspace)
DOC_STUDIO_WORKSPACE=$(pwd) /path/to/amplifier/scenarios/doc_studio/make dev-backend

# In another terminal, start the frontend
cd /path/to/amplifier/scenarios/doc_studio
make dev-frontend
```

**Option B: Use make variable**

```bash
cd /path/to/amplifier/scenarios/doc_studio
make dev-backend WORKSPACE=/path/to/your/project

# In another terminal, start frontend
make dev-frontend
```

### 3. Open the Application

Open http://localhost:5173 in your browser.

## How It Works

1. **Workspace**: The app scans the directory you specify as the workspace
2. **File Tree**: Shows all files in your workspace repository
3. **Template**: Drag files from the tree into template sections
4. **Generate**: Click "Generate Document" to create documentation using doc-evergreen
5. **Preview**: View the generated markdown document with source attribution

## Workspace Configuration

The workspace is determined in this order:

1. `DOC_STUDIO_WORKSPACE` environment variable
2. `WORKSPACE` make variable (passed to env var)
3. Current working directory (default)

The workspace directory:
- Is where doc-studio scans for files to include
- Is where `.doc-studio/` configuration is saved
- Is where generated documents are saved by default

## Development

```bash
# Run linting and type checks
make check

# Run tests
make test

# Clean build artifacts
make clean
```

## Project Structure

```
doc_studio/
├── doc_studio/          # Backend (FastAPI)
│   ├── api/            # API routes and SSE
│   ├── models/         # Data models
│   ├── services/       # Business logic
│   └── utils/          # Utilities
├── frontend/           # Frontend (React + TypeScript)
│   ├── src/
│   │   ├── components/ # React components
│   │   ├── services/   # API client
│   │   └── types/      # TypeScript types
│   └── package.json
└── Makefile           # Build commands
```

## Tips

- Always run doc-studio targeting the root of the repository you want to document
- The file tree respects `.gitignore` and common ignore patterns
- Templates are saved in `.doc-studio/templates/` in your workspace
- Generated documents include source attribution showing which files contributed to each section

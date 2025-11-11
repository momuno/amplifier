# End-to-End Test Plan: doc-evergreen

**Tool**: doc-evergreen - AI-powered documentation generation

**Version**: 1.0 (with Source Mapping Phase 1)

**Date**: 2025-01-11

---

## Overview

This test plan covers all major workflows and features of doc-evergreen:

1. **Document Creation** (first-time generation)
2. **Document Regeneration** (updating existing docs)
3. **Template Management** (built-in, customization, selection)
4. **Source Discovery** (patterns vs auto-discovery)
5. **Source Mapping** (intelligent section mapping)
6. **History & Versioning** (tracking, backups, rollback)
7. **Edge Cases & Error Handling**

---

## Test Environment Setup

### Prerequisites
- Fresh git repository or test project
- doc-evergreen installed (`make install`)
- Claude API key configured
- Python 3.11+

### Test Project Structure
```
test-project/
├── src/
│   ├── auth.py          # Authentication logic
│   ├── api.py           # API endpoints
│   ├── models.py        # Data models
│   └── utils.py         # Utilities
├── docs/
│   └── setup.md         # Installation instructions
├── tests/
│   └── test_api.py      # Test files
├── config/
│   └── settings.py      # Configuration
└── README.md            # Existing readme (if any)
```

### Sample Source Files (See Appendix A)

---

## Part 1: Document Creation Workflows

### Scenario 1.1: Simple Create with Pattern-Based Discovery

**Goal**: Create documentation using explicit glob patterns

**Setup**: Fresh project, no `.doc-evergreen/` exists

**Steps**:
```bash
cd test-project
doc-evergreen create \
  --about "API documentation for REST endpoints" \
  --output docs/API.md \
  --sources "src/**/*.py" \
  --template api
```

**Expected Outcomes**:

**Console Output**:
```
============================================================
doc-evergreen create command
============================================================
About: API documentation for REST endpoints
Output: docs/API.md
Sources: ['src/**/*.py']
Template: api
Dry run: False
============================================================

📁 Step 1: Discovering source files...
Using provided patterns: ['src/**/*.py']

Found 4 source files:
  • src/auth.py
  • src/api.py
  • src/models.py
  • src/utils.py
Total size: 2.5 KB

📝 Step 2: Preparing template...
Using specified template: api
Loaded built-in template: api

🗺️  Step 3: Mapping sources to template sections...
✓ Mapped 5 sections
  • Authentication: 1 source(s)
  • Endpoints: 2 source(s)
  • Models: 1 source(s)
  • Error Handling: 1 source(s)
✓ Source map saved: api-map.v1.yaml

🤖 Step 4: Generating documentation (using LLM with source mapping)...
This may take 30-60 seconds...
✓ Document generated successfully

💾 Step 5: No existing document to backup

💾 Step 6: Saving document to docs/API.md...
✓ Document saved successfully

📋 Step 7: Updating history...
✓ Added new document entry
✓ History updated

============================================================
✅ Documentation created successfully!
============================================================
Output: docs/API.md
Template: api (built-in)
Source mapping: api-map.v1.yaml
Sources: 4 files
============================================================
```

**File System**:
```bash
.doc-evergreen/
├── history.yaml
└── source-maps/
    └── api-map.v1.yaml

docs/
└── API.md
```

**history.yaml**:
```yaml
docs:
  docs/API.md:
    created: "2025-01-11T10:30:00+00:00"
    last_generated: "2025-01-11T10:30:00+00:00"
    path: docs/API.md
    template_used:
      name: api
      path: ""
    previous_versions: []
    sources:
      - src/**/*.py
    about: "API documentation for REST endpoints"
    source_map_path: ".doc-evergreen/source-maps/api-map.v1.yaml"
```

**Verification**:
- [ ] All source files discovered correctly
- [ ] Source map created with sensible mappings
- [ ] Generated doc follows API template structure
- [ ] History tracks all metadata
- [ ] Output file contains relevant content

---

### Scenario 1.2: Create with Auto-Discovery (No --sources)

**Goal**: Let LLM intelligently discover relevant files

**Setup**: Same test project

**Steps**:
```bash
doc-evergreen create \
  --about "Developer guide for contributing to the authentication system" \
  --output docs/AUTH_GUIDE.md \
  --template guide
```

**Expected Outcomes**:

**Console Output**:
```
📁 Step 1: Discovering source files...
Using LLM to intelligently discover relevant files...

✓ LLM discovered 5 relevant files
  • src/auth.py
  • src/models.py
  • tests/test_api.py
  • docs/setup.md
  • README.md

Found 5 source files:
  • src/auth.py
  • src/models.py
  • tests/test_api.py
  • docs/setup.md
  • README.md
Total size: 3.2 KB

📝 Step 2: Preparing template...
Using LLM to select appropriate template...
Selected template: guide

...
```

**history.yaml**:
```yaml
docs:
  docs/AUTH_GUIDE.md:
    sources:
      - src/auth.py          # ← Specific files, not patterns
      - src/models.py
      - tests/test_api.py
      - docs/setup.md
      - README.md
```

**Verification**:
- [ ] LLM discovers files relevant to "authentication"
- [ ] Discovery is focused (doesn't include unrelated files)
- [ ] Specific file paths stored in history (not patterns)
- [ ] Template selection is appropriate

---

### Scenario 1.3: Create with Template Customization

**Goal**: Customize built-in template for project-specific needs

**Setup**: Same test project

**Steps**:
```bash
doc-evergreen create \
  --about "Project README with installation and quick start" \
  --output README.md \
  --template readme \
  --customize-template
```

**Expected Outcomes**:

**Console Output**:
```
📝 Step 2: Preparing template...
Using specified template: readme
Evaluating if template customization would be beneficial...
✓ Customization recommended: Project has unique setup requirements
Loaded built-in template: readme
Customizing template 'readme' (explicitly requested)
✓ Customized template created
Saved customized template: .doc-evergreen/templates/readme.v1.md
```

**File System**:
```bash
.doc-evergreen/
├── templates/
│   └── readme.v1.md       # ← Customized template
└── source-maps/
    └── readme-map.v1.yaml
```

**history.yaml**:
```yaml
docs:
  README.md:
    template_used:
      name: readme
      path: ".doc-evergreen/templates/readme.v1.md"  # ← Custom path
```

**Verification**:
- [ ] Customized template saved to templates/
- [ ] History tracks custom template path
- [ ] Generated doc reflects customizations
- [ ] Original built-in template unchanged

---

### Scenario 1.4: Create with Auto-Decide Template Customization

**Goal**: Let LLM decide if customization is beneficial

**Setup**: Same test project

**Steps**:
```bash
doc-evergreen create \
  --about "Contributing guidelines" \
  --output CONTRIBUTING.md \
  --template guide
# Note: No --customize-template or --no-customize-template flag
```

**Expected Outcomes**:

**Console Output** (if customization recommended):
```
📝 Step 2: Preparing template...
Evaluating if template customization would be beneficial...
✓ Customization recommended: Template sections don't align perfectly with project structure
Customizing template...
```

**OR** (if customization not needed):
```
📝 Step 2: Preparing template...
Evaluating if template customization would be beneficial...
✓ Template sufficient as-is: Standard guide structure fits project needs
Using template 'guide' directly
```

**Verification**:
- [ ] LLM evaluation runs automatically
- [ ] Decision logged to console with reasoning
- [ ] Appropriate action taken based on evaluation

---

### Scenario 1.5: Create with --no-customize-template Override

**Goal**: Force use of built-in template without customization

**Steps**:
```bash
doc-evergreen create \
  --about "API reference" \
  --output docs/API_REF.md \
  --template api \
  --no-customize-template
```

**Expected Outcomes**:
```
📝 Step 2: Preparing template...
Using template 'api' directly (explicitly requested)
Loaded built-in template: api
```

**Verification**:
- [ ] No customization attempted
- [ ] No evaluation performed
- [ ] Built-in template used directly

---

### Scenario 1.6: Dry Run Creation

**Goal**: Preview what would be created without making changes

**Steps**:
```bash
doc-evergreen create \
  --about "Test documentation" \
  --output docs/TEST.md \
  --sources "src/**/*.py" \
  --template api \
  --dry-run
```

**Expected Outcomes**:
```
Found 4 source files:
  • src/auth.py
  • src/api.py
  • src/models.py
  • src/utils.py
Total size: 2.5 KB

[DRY RUN] Would proceed with:
  2. Template selection/customization
  3. Source-to-section mapping
  4. Document generation
  5. Backup existing document (if exists)
  6. Save to output path
  7. Update history.yaml
```

**File System**:
- No changes made
- No .doc-evergreen/ created
- No output file written

**Verification**:
- [ ] Preview shows all steps
- [ ] No side effects
- [ ] File discovery still runs (to show what would be used)

---

### Scenario 1.7: Create with Existing Output File

**Goal**: Verify backup behavior when overwriting existing file

**Setup**:
```bash
echo "# Old README" > README.md
```

**Steps**:
```bash
doc-evergreen create \
  --about "New project README" \
  --output README.md \
  --template readme
```

**Expected Outcomes**:
```
💾 Step 5: Backing up existing document...
✓ Backed up to: .doc-evergreen/versions/README.md.20250111_103045.bak

💾 Step 6: Saving document to README.md...
✓ Document saved successfully

📋 Step 7: Updating history...
✓ Added version entry for regeneration  # ← Note: First-time but file existed
✓ History updated
```

**File System**:
```bash
.doc-evergreen/
├── versions/
│   └── README.md.20250111_103045.bak  # ← Backup of old content
└── history.yaml
```

**history.yaml**:
```yaml
docs:
  README.md:
    created: "..."
    previous_versions:
      - timestamp: "2025-01-11T10:30:45+00:00"
        backup_path: ".doc-evergreen/versions/README.md.20250111_103045.bak"
```

**Verification**:
- [ ] Old file backed up before overwrite
- [ ] Backup tracked in history
- [ ] New content written to output

---

## Part 2: Document Regeneration Workflows

### Scenario 2.1: Simple Regenerate (No Changes to Sources)

**Goal**: Regenerate document when template or LLM behavior changes

**Setup**: Scenario 1.1 completed (docs/API.md exists)

**Steps**:
```bash
doc-evergreen regenerate docs/API.md
```

**Expected Outcomes**:
```
============================================================
doc-evergreen regenerate command
============================================================
Mode: Regenerate single document: docs/API.md
Dry run: False
============================================================

📋 Loading configuration from history...

📄 Regenerating: docs/API.md
------------------------------------------------------------
About: API documentation for REST endpoints
Output: docs/API.md
Sources: ['src/**/*.py']
Template: api

📁 Step 1: Gathering source files...
Found 4 source files

📝 Step 2: Loading template...
Loaded built-in template: api

🗺️  Step 3: Loading/creating source mapping...
✓ Loaded source map from .doc-evergreen/source-maps/api-map.v1.yaml

🤖 Step 4: Generating documentation (using LLM with source mapping)...
This may take 30-60 seconds...
✓ Document generated successfully

💾 Step 5: Backing up existing document...
✓ Backed up to: .doc-evergreen/versions/API.md.20250111_104523.bak

💾 Step 6: Saving document to docs/API.md...
✓ Document saved successfully

📋 Step 7: Updating history...
✓ History updated

✅ Successfully regenerated: docs/API.md
```

**history.yaml** (updated):
```yaml
docs:
  docs/API.md:
    last_generated: "2025-01-11T10:45:23+00:00"  # ← Updated
    previous_versions:
      - timestamp: "2025-01-11T10:45:23+00:00"
        backup_path: ".doc-evergreen/versions/API.md.20250111_104523.bak"
        template_used:
          name: api
          path: ""
        sources:
          - src/**/*.py
        source_map_path: ".doc-evergreen/source-maps/api-map.v1.yaml"
```

**Verification**:
- [ ] Existing source map loaded (not recreated)
- [ ] Old document backed up
- [ ] New document generated
- [ ] History updated with version entry

---

### Scenario 2.2: Regenerate After Source Code Changes

**Goal**: Update documentation when source files change

**Setup**: Scenario 2.1 completed

**Steps**:
```bash
# Modify source file
echo "\ndef new_endpoint():\n    '''New endpoint'''\n    pass" >> src/api.py

# Regenerate
doc-evergreen regenerate docs/API.md
```

**Expected Outcomes**:
- Same console output as 2.1
- Generated doc includes `new_endpoint()` information
- Same source map used (v1, not recreated)

**Verification**:
- [ ] New endpoint appears in generated doc
- [ ] Existing source map still used
- [ ] Mapping still appropriate despite code changes

---

### Scenario 2.3: Regenerate with Missing Source Map

**Goal**: Gracefully handle deleted or missing source maps

**Setup**: Scenario 2.1 completed

**Steps**:
```bash
# Delete source map
rm .doc-evergreen/source-maps/api-map.v1.yaml

# Regenerate
doc-evergreen regenerate docs/API.md
```

**Expected Outcomes**:
```
🗺️  Step 3: Loading/creating source mapping...
⚠ Source map not found: .doc-evergreen/source-maps/api-map.v1.yaml
Creating new source mapping...
✓ Mapped 5 sections
✓ Source map saved: api-map.v2.yaml  # ← NEW VERSION
```

**history.yaml** (updated):
```yaml
docs:
  docs/API.md:
    source_map_path: ".doc-evergreen/source-maps/api-map.v2.yaml"  # ← Updated
    previous_versions:
      - timestamp: "..."
        source_map_path: ".doc-evergreen/source-maps/api-map.v2.yaml"
```

**Verification**:
- [ ] Warning displayed about missing map
- [ ] New map created with next version number
- [ ] History updated to reference new map
- [ ] Regeneration completes successfully

---

### Scenario 2.4: Regenerate with Custom Template

**Goal**: Regenerate document that uses customized template

**Setup**: Scenario 1.3 completed (README.md with custom template)

**Steps**:
```bash
doc-evergreen regenerate README.md
```

**Expected Outcomes**:
```
📝 Step 2: Loading template...
Loaded customized template from .doc-evergreen/templates/readme.v1.md
```

**Verification**:
- [ ] Loads custom template (not built-in)
- [ ] Regenerates using customizations
- [ ] Generated doc maintains custom structure

---

### Scenario 2.5: Regenerate All Documents

**Goal**: Batch regenerate all configured documents

**Setup**: Multiple documents created (1.1, 1.2, 1.3)

**Steps**:
```bash
doc-evergreen regenerate --all
```

**Expected Outcomes**:
```
============================================================
Mode: Regenerate all configured documents
Dry run: False
============================================================

📋 Loading configuration from history...
Found 3 configured documents

📄 Regenerating: docs/API.md
------------------------------------------------------------
[... full regeneration output ...]
✅ Successfully regenerated: docs/API.md

📄 Regenerating: docs/AUTH_GUIDE.md
------------------------------------------------------------
[... full regeneration output ...]
✅ Successfully regenerated: docs/AUTH_GUIDE.md

📄 Regenerating: README.md
------------------------------------------------------------
[... full regeneration output ...]
✅ Successfully regenerated: README.md

============================================================
📊 Regeneration Summary
============================================================
✅ Successful: 3
============================================================
```

**Verification**:
- [ ] All 3 documents regenerated
- [ ] Each uses its own template and source map
- [ ] Summary shows success count
- [ ] All backups created

---

### Scenario 2.6: Regenerate All with Partial Failure

**Goal**: Verify --all continues after individual failures

**Setup**: Multiple documents, corrupt one source map

**Steps**:
```bash
# Corrupt a source map
echo "invalid: yaml: content:" > .doc-evergreen/source-maps/api-map.v1.yaml

# Regenerate all
doc-evergreen regenerate --all
```

**Expected Outcomes**:
```
📄 Regenerating: docs/API.md
------------------------------------------------------------
[... attempts regeneration ...]
⚠ Error regenerating docs/API.md: [error details]

📄 Regenerating: docs/AUTH_GUIDE.md
------------------------------------------------------------
[... successful regeneration ...]
✅ Successfully regenerated: docs/AUTH_GUIDE.md

📄 Regenerating: README.md
------------------------------------------------------------
[... successful regeneration ...]
✅ Successfully regenerated: README.md

============================================================
📊 Regeneration Summary
============================================================
✅ Successful: 2
⚠ Failed: 1
============================================================
```

**Verification**:
- [ ] First document fails but process continues
- [ ] Other documents regenerate successfully
- [ ] Summary shows both successes and failures
- [ ] Failed document not updated

---

### Scenario 2.7: Regenerate Dry Run

**Goal**: Preview regeneration without making changes

**Steps**:
```bash
doc-evergreen regenerate docs/API.md --dry-run
```

**Expected Outcomes**:
```
📄 Regenerating: docs/API.md
------------------------------------------------------------
About: API documentation for REST endpoints
Output: docs/API.md
Sources: ['src/**/*.py']
Template: api

[DRY RUN] Would regenerate this document
```

**Verification**:
- [ ] Shows configuration
- [ ] No actual regeneration
- [ ] No backups created
- [ ] No history changes

---

### Scenario 2.8: Regenerate Document Not in History

**Goal**: Handle request to regenerate unknown document

**Steps**:
```bash
doc-evergreen regenerate docs/UNKNOWN.md
```

**Expected Outcomes**:
```
⚠ Document not found in history: docs/UNKNOWN.md

Configured documents:
  • docs/API.md
  • docs/AUTH_GUIDE.md
  • README.md
```

**Verification**:
- [ ] Error message displayed
- [ ] Lists known documents
- [ ] Process exits gracefully

---

## Part 3: Template Management

### Scenario 3.1: List Available Built-in Templates

**Goal**: Discover what templates are available

**Steps**:
```bash
# This assumes a list-templates command exists
# Or user examines: doc_evergreen/templates/builtin/
ls doc_evergreen/templates/builtin/
```

**Expected Outcomes**:
```
readme.md
api.md
guide.md
```

**Verification**:
- [ ] Built-in templates accessible
- [ ] Templates contain clear sections and instructions

---

### Scenario 3.2: Template Customization Decision Process

**Goal**: Understand when LLM recommends customization

**Setup**: Various project types

**Test Cases**:

**Case A: Standard Project (should NOT customize)**
```bash
# Simple REST API with standard structure
doc-evergreen create --about "REST API docs" --output API.md --template api
# Expected: "Template sufficient as-is"
```

**Case B: Complex Project (should customize)**
```bash
# Project with unique architecture (e.g., microservices, event-driven)
doc-evergreen create --about "Microservices architecture docs" --output ARCH.md --template guide
# Expected: "Customization recommended: Complex architecture needs specialized sections"
```

**Verification**:
- [ ] LLM provides clear reasoning
- [ ] Decision is appropriate for project complexity
- [ ] User can override with explicit flags

---

### Scenario 3.3: Multiple Customized Template Versions

**Goal**: Track evolution of customized templates

**Steps**:
```bash
# Create with customization
doc-evergreen create --about "Version 1" --output V1.md --template guide --customize-template

# Later, create another with customization (triggers new version)
doc-evergreen create --about "Version 2" --output V2.md --template guide --customize-template
```

**Expected File System**:
```bash
.doc-evergreen/templates/
├── guide.v1.md
└── guide.v2.md
```

**Verification**:
- [ ] Each customization creates new version
- [ ] Version numbers increment
- [ ] Each document references its own version
- [ ] Old versions preserved

---

## Part 4: Source Discovery

### Scenario 4.1: Pattern-Based Discovery - Multiple Patterns

**Goal**: Use multiple glob patterns to gather sources

**Steps**:
```bash
doc-evergreen create \
  --about "Full system documentation" \
  --output docs/SYSTEM.md \
  --sources "src/**/*.py" "tests/**/*.py" "config/**/*.py" \
  --template guide
```

**Expected Outcomes**:
```
📁 Step 1: Discovering source files...
Using provided patterns: ['src/**/*.py', 'tests/**/*.py', 'config/**/*.py']

Found 12 source files:
  • src/auth.py
  • src/api.py
  • src/models.py
  • src/utils.py
  • tests/test_api.py
  • tests/test_auth.py
  • tests/test_models.py
  • tests/conftest.py
  • config/settings.py
  • config/logging.py
  • config/database.py
  • config/__init__.py
Total size: 8.3 KB
```

**Verification**:
- [ ] All patterns applied
- [ ] Files from all directories included
- [ ] No duplicates if patterns overlap

---

### Scenario 4.2: Pattern-Based Discovery - No Matches

**Goal**: Handle patterns that match no files

**Steps**:
```bash
doc-evergreen create \
  --about "Rust documentation" \
  --output docs/RUST.md \
  --sources "src/**/*.rs" \
  --template guide
```

**Expected Outcomes**:
```
📁 Step 1: Discovering source files...
Using provided patterns: ['src/**/*.rs']

Found 0 source files
Total size: 0 B

Error: No source files found for the specified topic/patterns
```

**Verification**:
- [ ] Clear error message
- [ ] Process exits gracefully
- [ ] No partial artifacts created

---

### Scenario 4.3: Auto-Discovery - Focused Topic

**Goal**: LLM discovers only relevant files for specific topic

**Steps**:
```bash
doc-evergreen create \
  --about "Database models and schemas" \
  --output docs/MODELS.md \
  --template guide
```

**Expected Outcomes**:
```
📁 Step 1: Discovering source files...
Using LLM to intelligently discover relevant files...

✓ LLM discovered 3 relevant files
  • src/models.py
  • src/database.py
  • tests/test_models.py

Found 3 source files: [...]
```

**Verification**:
- [ ] Only model-related files discovered
- [ ] Focused on topic (not entire codebase)
- [ ] Excludes unrelated files (e.g., auth.py, api.py)

---

### Scenario 4.4: Auto-Discovery - Broad Topic

**Goal**: LLM discovers comprehensive file set for broad topic

**Steps**:
```bash
doc-evergreen create \
  --about "Complete system overview and architecture" \
  --output docs/OVERVIEW.md \
  --template guide
```

**Expected Outcomes**:
```
✓ LLM discovered 10 relevant files
  • src/auth.py
  • src/api.py
  • src/models.py
  • src/utils.py
  • config/settings.py
  • docs/setup.md
  • README.md
  • tests/conftest.py
  [... more files ...]
```

**Verification**:
- [ ] Broad set of files discovered
- [ ] Includes source, config, docs, tests
- [ ] Still focused (doesn't include everything blindly)

---

### Scenario 4.5: Auto-Discovery with Large Codebase

**Goal**: Handle discovery in project with hundreds of files

**Setup**: Project with 200+ files

**Steps**:
```bash
doc-evergreen create \
  --about "Authentication system" \
  --output docs/AUTH.md \
  --template guide
```

**Expected Outcomes**:
- Discovery completes in reasonable time (<30 seconds)
- Discovers 5-15 relevant files (not all 200+)
- Focuses on auth-related files

**Verification**:
- [ ] Performance acceptable
- [ ] Discovery is selective
- [ ] No timeouts or errors

---

## Part 5: Source Mapping

### Scenario 5.1: Source Mapping Quality - Good Mapping

**Goal**: Verify that source-to-section mapping is sensible

**Setup**: Scenario 1.1 completed

**Steps**:
```bash
cat .doc-evergreen/source-maps/api-map.v1.yaml
```

**Expected Content**:
```yaml
metadata:
  template_name: api
  version: 1
  created_at: "2025-01-11T10:30:00"
  about: "API documentation for REST endpoints"
sections:
  Authentication:
    sources:
      - src/auth.py
  Endpoints:
    sources:
      - src/api.py
      - src/models.py
  Models:
    sources:
      - src/models.py
  Error Handling:
    sources:
      - src/utils.py
  Testing:
    sources:
      - tests/test_api.py
```

**Verification**:
- [ ] Mappings make logical sense
- [ ] Authentication section → auth.py (correct)
- [ ] Endpoints section → api.py + models.py (correct)
- [ ] No random/irrelevant mappings

---

### Scenario 5.2: Source Mapping - Empty Sections

**Goal**: Handle sections with no relevant sources

**Setup**: Template has "Deployment" section but no deployment files exist

**Expected Outcomes**:
```yaml
sections:
  Deployment:
    sources: []  # ← No sources mapped
```

**Verification**:
- [ ] Empty source list for irrelevant sections
- [ ] Generation still proceeds
- [ ] Section generated with general guidance (not file-specific)

---

### Scenario 5.3: Source Mapping - Multiple Sources per Section

**Goal**: Verify sections can map to multiple sources

**Expected Outcomes**:
```yaml
sections:
  API Implementation:
    sources:
      - src/api.py
      - src/routes.py
      - src/handlers.py
      - src/middleware.py
```

**Verification**:
- [ ] Multiple sources allowed
- [ ] All relevant sources included
- [ ] Generation uses all mapped sources for that section

---

### Scenario 5.4: Source Mapping Evolution

**Goal**: Create new mapping version when source structure changes

**Steps**:
```bash
# Initial state
doc-evergreen create --about "API docs" --output API.md --template api
# Creates api-map.v1.yaml

# Add new source file
echo "class NewModel: pass" > src/new_model.py

# Delete old map to force remapping
rm .doc-evergreen/source-maps/api-map.v1.yaml

# Regenerate
doc-evergreen regenerate API.md
# Creates api-map.v2.yaml with new source included
```

**Verification**:
- [ ] v2 includes new_model.py in appropriate section
- [ ] Both v1 and v2 can coexist
- [ ] History tracks which version was used when

---

## Part 6: History & Versioning

### Scenario 6.1: History Structure After Multiple Operations

**Goal**: Verify history accurately tracks all operations

**Steps**:
```bash
# Create document
doc-evergreen create --about "API" --output API.md --template api

# Regenerate twice
doc-evergreen regenerate API.md
doc-evergreen regenerate API.md

# Check history
cat .doc-evergreen/history.yaml
```

**Expected history.yaml**:
```yaml
docs:
  API.md:
    created: "2025-01-11T10:00:00"
    last_generated: "2025-01-11T10:15:00"  # ← Latest
    path: API.md
    template_used:
      name: api
      path: ""
    sources:
      - src/**/*.py
    about: "API"
    source_map_path: ".doc-evergreen/source-maps/api-map.v1.yaml"
    previous_versions:
      - timestamp: "2025-01-11T10:05:00"
        backup_path: ".doc-evergreen/versions/API.md.20250111_100500.bak"
        template_used:
          name: api
          path: ""
        sources:
          - src/**/*.py
        source_map_path: ".doc-evergreen/source-maps/api-map.v1.yaml"
      - timestamp: "2025-01-11T10:15:00"
        backup_path: ".doc-evergreen/versions/API.md.20250111_101500.bak"
        template_used:
          name: api
          path: ""
        sources:
          - src/**/*.py
        source_map_path: ".doc-evergreen/source-maps/api-map.v1.yaml"
```

**Verification**:
- [ ] Created timestamp preserved
- [ ] Last_generated updates each time
- [ ] Two version entries (one per regeneration)
- [ ] Each version tracks its backup path
- [ ] Source map path tracked for each version

---

### Scenario 6.2: Backup File Management

**Goal**: Verify backups are created and organized properly

**Steps**:
```bash
# Create and regenerate multiple times
doc-evergreen create --about "Test" --output TEST.md --template readme
doc-evergreen regenerate TEST.md
doc-evergreen regenerate TEST.md
doc-evergreen regenerate TEST.md

# Check versions directory
ls -la .doc-evergreen/versions/
```

**Expected Outcomes**:
```
.doc-evergreen/versions/
├── TEST.md.20250111_100000.bak
├── TEST.md.20250111_101000.bak
└── TEST.md.20250111_102000.bak
```

**Verification**:
- [ ] Each regeneration creates backup
- [ ] Timestamp-based naming
- [ ] Old backups preserved
- [ ] Backups are actual copies (can be restored)

---

### Scenario 6.3: Restoring from Backup (Manual)

**Goal**: Verify backups can be restored manually

**Steps**:
```bash
# Check current content
cat API.md

# Restore from backup
cp .doc-evergreen/versions/API.md.20250111_100500.bak API.md

# Verify restoration
cat API.md
```

**Verification**:
- [ ] Backup file is valid markdown
- [ ] Content matches earlier version
- [ ] Can be manually restored

---

### Scenario 6.4: Multiple Documents in History

**Goal**: Verify history handles multiple documents correctly

**Setup**: Create 5 different documents

**Expected history.yaml**:
```yaml
docs:
  README.md:
    [... doc config ...]
  docs/API.md:
    [... doc config ...]
  docs/GUIDE.md:
    [... doc config ...]
  CONTRIBUTING.md:
    [... doc config ...]
  CHANGELOG.md:
    [... doc config ...]
```

**Verification**:
- [ ] All documents tracked separately
- [ ] Each has own configuration
- [ ] Each has own version history
- [ ] No conflicts or overwrites

---

## Part 7: Edge Cases & Error Handling

### Scenario 7.1: Invalid Template Name

**Steps**:
```bash
doc-evergreen create \
  --about "Test" \
  --output TEST.md \
  --template nonexistent
```

**Expected Outcomes**:
```
Error: Template 'nonexistent' not found

Available built-in templates:
  • readme
  • api
  • guide
```

**Verification**:
- [ ] Clear error message
- [ ] Lists available templates
- [ ] Process exits gracefully

---

### Scenario 7.2: Invalid Output Path

**Steps**:
```bash
doc-evergreen create \
  --about "Test" \
  --output /root/forbidden/TEST.md \
  --template readme
```

**Expected Outcomes**:
```
Error: Cannot write to /root/forbidden/TEST.md: Permission denied
```

**Verification**:
- [ ] Permission error caught
- [ ] Clear error message
- [ ] No partial files created

---

### Scenario 7.3: Missing --about Flag

**Steps**:
```bash
doc-evergreen create \
  --output TEST.md \
  --template readme
# Missing --about
```

**Expected Outcomes**:
```
Error: --about is required
Usage: doc-evergreen create --about "..." --output "..." [--sources "..."] [--template "..."]
```

**Verification**:
- [ ] Required flag validated
- [ ] Usage help shown
- [ ] Clear error message

---

### Scenario 7.4: Very Large Source Files

**Goal**: Handle projects with large source files (>100KB)

**Setup**: Create source file with 200KB of code

**Steps**:
```bash
# Generate large file
python -c "for i in range(10000): print(f'def func_{i}(): pass')" > src/large.py

doc-evergreen create \
  --about "Test large files" \
  --output LARGE.md \
  --sources "src/**/*.py" \
  --template api
```

**Expected Outcomes**:
- Source discovery includes large file
- Source mapping prompt truncates to 15KB limit
- Generation completes successfully
- Generated doc may have less detail for large file

**Verification**:
- [ ] No errors or timeouts
- [ ] Large files handled gracefully
- [ ] Token limits respected

---

### Scenario 7.5: Empty Source Files

**Goal**: Handle source files with no content

**Setup**:
```bash
touch src/empty.py
```

**Expected Outcomes**:
- Empty file included in discovery
- Not mapped to any sections (no content to analyze)
- Generation completes

**Verification**:
- [ ] No errors
- [ ] Empty files don't break mapping
- [ ] Generated doc ignores empty files

---

### Scenario 7.6: Binary Files in Source Patterns

**Goal**: Handle non-text files in glob patterns

**Setup**:
```bash
cp some-image.png src/logo.png
```

**Steps**:
```bash
doc-evergreen create \
  --about "Test" \
  --output TEST.md \
  --sources "src/**/*"  # ← Will match logo.png
  --template readme
```

**Expected Outcomes**:
- Binary files skipped or handled gracefully
- Warning logged about non-text files
- Generation completes with text files only

**Verification**:
- [ ] No crashes on binary data
- [ ] Binary files filtered out
- [ ] User informed about skipped files

---

### Scenario 7.7: Corrupted history.yaml

**Goal**: Handle corrupted or invalid YAML

**Setup**:
```bash
echo "invalid: yaml: {{{ syntax" > .doc-evergreen/history.yaml
```

**Steps**:
```bash
doc-evergreen regenerate --all
```

**Expected Outcomes**:
```
Error: Failed to parse history.yaml: [YAML parse error details]
```

**Verification**:
- [ ] YAML parse error caught
- [ ] Clear error message
- [ ] Process exits gracefully (doesn't crash)

---

### Scenario 7.8: Git Repository Detection

**Goal**: Verify git root detection and warnings

**Test Case A: Running from git root**
```bash
cd /path/to/git-repo  # Where .git exists
doc-evergreen create --about "Test" --output README.md --template readme
```

**Expected**: No warnings, uses git root as repo_path

**Test Case B: Running from subdirectory**
```bash
cd /path/to/git-repo/src
doc-evergreen create --about "Test" --output ../API.md --template api
```

**Expected Outcomes**:
```
⚠️  Warning: Running from subdirectory of git repo.
   Current: /path/to/git-repo/src
   Git root: /path/to/git-repo
   Using git root as repo path.

💡 Tip: For best results, run from repository root:
   cd /path/to/git-repo
   make doc-create ABOUT="..." OUTPUT=...

Continue with git root as repo path? [y/N]:
```

**Test Case C: Not in git repo**
```bash
cd /tmp
mkdir test-project
cd test-project
doc-evergreen create --about "Test" --output README.md --template readme
```

**Expected Outcomes**:
```
⚠️  Warning: Not in a git repository.
   Using current directory as repo root.
   Directory: /tmp/test-project
```

**Verification**:
- [ ] Git root correctly detected
- [ ] Warnings shown when not at root
- [ ] User prompted for confirmation
- [ ] Works outside git repos with warning

---

### Scenario 7.9: Concurrent Regenerations

**Goal**: Handle simultaneous regenerations

**Setup**: Run in two terminals simultaneously

**Terminal 1**:
```bash
doc-evergreen regenerate API.md
```

**Terminal 2** (start immediately):
```bash
doc-evergreen regenerate API.md
```

**Expected Outcomes**:
- Both complete (or one waits/fails gracefully)
- No corrupted files
- No lost data
- History remains consistent

**Verification**:
- [ ] File integrity maintained
- [ ] History consistency preserved
- [ ] Appropriate locking or error handling

---

### Scenario 7.10: API Key Missing

**Goal**: Handle missing Claude API key

**Setup**:
```bash
unset ANTHROPIC_API_KEY
```

**Steps**:
```bash
doc-evergreen create --about "Test" --output TEST.md --template readme
```

**Expected Outcomes**:
```
Error: ANTHROPIC_API_KEY environment variable not set

Please set your Claude API key:
  export ANTHROPIC_API_KEY='your-key-here'

Or add to your shell profile (~/.bashrc, ~/.zshrc, etc.)
```

**Verification**:
- [ ] Clear error message
- [ ] Helpful instructions provided
- [ ] Process exits cleanly

---

### Scenario 7.11: API Rate Limiting

**Goal**: Handle Claude API rate limits gracefully

**Setup**: Trigger rate limit (multiple rapid requests)

**Expected Outcomes**:
- Retry with exponential backoff
- User informed of retry
- Eventually completes or fails with clear message

**Verification**:
- [ ] Retries automatically
- [ ] User kept informed
- [ ] Eventual success or clear failure

---

### Scenario 7.12: LLM Returns Malformed JSON

**Goal**: Handle invalid JSON in source mapping

**Setup**: Mock LLM to return non-JSON response

**Expected Outcomes**:
```
Error: Failed to parse source mapping from LLM response
The LLM returned: [actual response preview]

This is likely a temporary issue. Please try again.
```

**Verification**:
- [ ] Parse error caught
- [ ] Response preview shown (for debugging)
- [ ] Clear recovery instructions

---

## Part 8: Integration Scenarios

### Scenario 8.1: Full Lifecycle - Create to Multiple Regenerations

**Goal**: Test complete workflow from creation through multiple updates

**Steps**:
```bash
# Day 1: Initial creation
doc-evergreen create \
  --about "API documentation" \
  --output docs/API.md \
  --sources "src/**/*.py" \
  --template api

# Day 2: Code changes, regenerate
echo "def new_func(): pass" >> src/api.py
doc-evergreen regenerate docs/API.md

# Day 3: More changes, regenerate
echo "def another_func(): pass" >> src/auth.py
doc-evergreen regenerate docs/API.md

# Day 4: Review history
cat .doc-evergreen/history.yaml

# Check all backups
ls -la .doc-evergreen/versions/
```

**Expected Outcomes**:
- 3 backups created (initial + 2 regenerations)
- History shows 3 timestamps
- Latest doc has all new functions
- Can review progression through backups

**Verification**:
- [ ] Complete version history
- [ ] All backups accessible
- [ ] Documentation stays current
- [ ] History is coherent narrative

---

### Scenario 8.2: Multi-Document Project

**Goal**: Manage documentation for entire project

**Steps**:
```bash
# Create comprehensive documentation set
doc-evergreen create --about "Project overview" --output README.md --template readme
doc-evergreen create --about "API reference" --output docs/API.md --template api
doc-evergreen create --about "Contributing guidelines" --output CONTRIBUTING.md --template guide
doc-evergreen create --about "Architecture decisions" --output docs/ARCHITECTURE.md --template guide
doc-evergreen create --about "Setup instructions" --output docs/SETUP.md --template guide

# Update all at once after major refactor
doc-evergreen regenerate --all

# Check comprehensive history
cat .doc-evergreen/history.yaml
```

**Expected Outcomes**:
- 5 documents tracked independently
- Each with own template, sources, source map
- --all regenerates all 5
- Clear organization in .doc-evergreen/

**Verification**:
- [ ] Each document maintains independence
- [ ] Cross-references work (if manually added)
- [ ] Batch operations work correctly
- [ ] History is organized and clear

---

### Scenario 8.3: Template Evolution Over Time

**Goal**: Track how templates and mappings evolve

**Steps**:
```bash
# Week 1: Create with default template
doc-evergreen create --about "API docs" --output API.md --template api

# Week 2: Project complexity increases, customize
doc-evergreen create --about "API v2 docs" --output API_V2.md --template api --customize-template
# Creates api.v1.md

# Week 3: Further refinement
# Manually edit .doc-evergreen/templates/api.v1.md
# Save as api.v2.md
# Update history for API_V2.md to reference api.v2.md

# Week 4: New mapping needed
rm .doc-evergreen/source-maps/api-map.v1.yaml
doc-evergreen regenerate API_V2.md
# Creates api-map.v2.yaml

# Review evolution
ls -la .doc-evergreen/templates/
ls -la .doc-evergreen/source-maps/
```

**Expected Outcomes**:
- Multiple template versions
- Multiple source map versions
- Clear progression over time
- Old versions preserved

**Verification**:
- [ ] Can trace evolution
- [ ] Old versions still accessible
- [ ] Version numbers make sense
- [ ] Documentation reflects growth

---

### Scenario 8.4: Migrating Existing Documentation

**Goal**: Integrate doc-evergreen with existing docs

**Setup**: Project with hand-written README.md and docs/

**Steps**:
```bash
# Backup existing docs
cp README.md README.md.original
cp docs/API.md docs/API.md.original

# Generate with doc-evergreen (will backup automatically)
doc-evergreen create --about "Project README" --output README.md --template readme
doc-evergreen create --about "API reference" --output docs/API.md --template api

# Compare old vs new
diff README.md.original .doc-evergreen/versions/README.md.*.bak
diff README.md.original README.md
```

**Expected Outcomes**:
- Old docs backed up to versions/
- New docs generated
- Can compare and merge manually if needed

**Verification**:
- [ ] No data loss
- [ ] Old docs preserved
- [ ] New docs maintain structure
- [ ] Migration path is clear

---

## Success Criteria

### Phase 1 (Current) is successful if:

**Core Functionality**:
- [ ] All creation workflows work
- [ ] All regeneration workflows work
- [ ] Template management works
- [ ] Source discovery works (patterns + auto)
- [ ] Source mapping creates sensible mappings
- [ ] History tracking is accurate
- [ ] Versioning and backups work

**User Experience**:
- [ ] Console output is clear and helpful
- [ ] Error messages are actionable
- [ ] Dry run provides useful previews
- [ ] Git detection works correctly
- [ ] Warnings are appropriate

**Quality**:
- [ ] Generated docs follow template structure
- [ ] Source mapping improves doc quality
- [ ] Multiple documents coexist properly
- [ ] History is maintainable
- [ ] Edge cases handled gracefully

**Robustness**:
- [ ] No data loss scenarios
- [ ] Corrupted files handled
- [ ] API errors handled
- [ ] Large files handled
- [ ] Concurrent access handled

---

## Testing Approach

### Manual Testing Priority (Now)

**High Priority** (Test first):
1. Scenario 1.1 - Basic create
2. Scenario 2.1 - Basic regenerate
3. Scenario 1.2 - Auto-discovery
4. Scenario 2.5 - Regenerate all
5. Scenario 5.1 - Mapping quality
6. Scenario 7.1-7.3 - Basic error handling

**Medium Priority** (Test second):
- Template customization scenarios
- History and versioning scenarios
- Source discovery variations
- More error handling

**Low Priority** (Test if time):
- Edge cases
- Performance testing
- Concurrent operations
- Integration scenarios

### Future Automation

When converting to automated tests:

**Unit Tests** (60%):
- Template functions
- Source discovery logic
- Mapping logic
- History management
- YAML parsing

**Integration Tests** (30%):
- CLI command execution
- File system operations
- LLM interactions (mocked)
- Multi-step workflows

**E2E Tests** (10%):
- Full create workflow
- Full regenerate workflow
- Multi-document scenarios
- Real LLM calls (in CI)

---

## Test Execution Checklist

When running this test plan:

**Preparation**:
- [ ] Set up fresh test project
- [ ] Install doc-evergreen
- [ ] Configure API key
- [ ] Create sample source files

**Execution**:
- [ ] Part 1: Creation workflows (7 scenarios)
- [ ] Part 2: Regeneration workflows (8 scenarios)
- [ ] Part 3: Template management (3 scenarios)
- [ ] Part 4: Source discovery (5 scenarios)
- [ ] Part 5: Source mapping (4 scenarios)
- [ ] Part 6: History & versioning (4 scenarios)
- [ ] Part 7: Edge cases (12 scenarios)
- [ ] Part 8: Integration (4 scenarios)

**Documentation**:
- [ ] Record results for each scenario
- [ ] Note any deviations from expected
- [ ] Document bugs found
- [ ] Capture screenshots/logs where helpful
- [ ] Summarize findings

---

## Appendix A: Sample Source Files

### src/auth.py
```python
"""
Authentication module for the API.

Handles user authentication, token generation, and session management.
"""
from datetime import datetime, timedelta
import jwt

SECRET_KEY = "your-secret-key"

def authenticate_user(username: str, password: str) -> bool:
    """
    Authenticate a user with username and password.

    Args:
        username: The username
        password: The password

    Returns:
        True if authentication successful, False otherwise
    """
    # TODO: Check against database
    return username == "admin" and password == "password"

def generate_token(user_id: int) -> str:
    """
    Generate a JWT token for a user.

    Args:
        user_id: The user's ID

    Returns:
        JWT token string
    """
    payload = {
        "user_id": user_id,
        "exp": datetime.utcnow() + timedelta(hours=24)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

def verify_token(token: str) -> dict | None:
    """
    Verify and decode a JWT token.

    Args:
        token: The JWT token

    Returns:
        Decoded payload if valid, None otherwise
    """
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    except jwt.InvalidTokenError:
        return None
```

### src/api.py
```python
"""
REST API endpoints.

Provides HTTP endpoints for user management and data access.
"""
from fastapi import FastAPI, HTTPException, Depends
from .auth import verify_token
from .models import User, CreateUserRequest

app = FastAPI()

@app.get("/users")
async def get_users(token: str = Depends(verify_token)):
    """
    Get all users.

    Requires authentication.

    Returns:
        List of users
    """
    # TODO: Fetch from database
    return [
        {"id": 1, "username": "admin", "email": "admin@example.com"},
        {"id": 2, "username": "user", "email": "user@example.com"}
    ]

@app.post("/users")
async def create_user(request: CreateUserRequest):
    """
    Create a new user.

    Args:
        request: User creation request

    Returns:
        Created user
    """
    # TODO: Insert into database
    return {
        "id": 3,
        "username": request.username,
        "email": request.email
    }

@app.get("/users/{user_id}")
async def get_user(user_id: int, token: str = Depends(verify_token)):
    """
    Get a specific user by ID.

    Args:
        user_id: The user's ID

    Returns:
        User object

    Raises:
        HTTPException: If user not found
    """
    # TODO: Fetch from database
    if user_id == 1:
        return {"id": 1, "username": "admin", "email": "admin@example.com"}
    raise HTTPException(status_code=404, detail="User not found")
```

### src/models.py
```python
"""
Data models for the application.

Defines Pydantic models for request/response validation.
"""
from pydantic import BaseModel, EmailStr

class User(BaseModel):
    """User model."""
    id: int
    username: str
    email: EmailStr

class CreateUserRequest(BaseModel):
    """Request model for creating a user."""
    username: str
    email: EmailStr
    password: str

class LoginRequest(BaseModel):
    """Request model for user login."""
    username: str
    password: str

class TokenResponse(BaseModel):
    """Response model for authentication."""
    access_token: str
    token_type: str = "bearer"
```

### src/utils.py
```python
"""
Utility functions.

Common helpers used throughout the application.
"""
import hashlib

def hash_password(password: str) -> str:
    """
    Hash a password using SHA256.

    Args:
        password: Plain text password

    Returns:
        Hashed password
    """
    return hashlib.sha256(password.encode()).hexdigest()

def validate_email(email: str) -> bool:
    """
    Validate email format.

    Args:
        email: Email address

    Returns:
        True if valid, False otherwise
    """
    return "@" in email and "." in email.split("@")[1]
```

### tests/test_api.py
```python
"""
Tests for API endpoints.
"""
import pytest
from fastapi.testclient import TestClient
from src.api import app

client = TestClient(app)

def test_get_users():
    """Test getting all users."""
    # Need token for auth
    response = client.get("/users")
    # Would fail without token
    assert response.status_code in [200, 401]

def test_create_user():
    """Test creating a user."""
    response = client.post("/users", json={
        "username": "newuser",
        "email": "new@example.com",
        "password": "password123"
    })
    assert response.status_code == 200
    assert response.json()["username"] == "newuser"
```

---

**End of E2E Test Plan**

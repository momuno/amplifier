# Template Guide

This guide explains how to create and use JSON templates for generating documentation with doc_evergreen.

## What is a Template?

A template is a JSON file that defines:
- **What** documentation to generate (sections and structure)
- **How** to generate it (prompts for each section)
- **Where** to get information (source files for context)
- **Where** to save it (output file path)

Templates enable you to regenerate documentation consistently as your codebase evolves.

## Template Structure

### Basic Format

```json
{
  "document": {
    "title": "Document Title",
    "output": "path/to/output.md",
    "sections": [
      {
        "heading": "Section Name",
        "prompt": "Instructions for generating this section",
        "sources": ["file1.md", "file2.py"]
      }
    ]
  }
}
```

### Complete Example

```json
{
  "document": {
    "title": "My Project README",
    "output": "docs/README.md",
    "sections": [
      {
        "heading": "Overview",
        "prompt": "Explain what this project does and who it's for",
        "sources": ["README.md", "docs/architecture.md"]
      },
      {
        "heading": "Installation",
        "prompt": "Provide step-by-step installation instructions",
        "sources": ["README.md", "pyproject.toml", "package.json"]
      }
    ]
  }
}
```

## Field Reference

### Document Fields

| Field | Required | Description |
|-------|----------|-------------|
| `title` | Yes | Human-readable title for the document |
| `output` | Yes | Path where generated documentation will be saved |
| `sections` | Yes | Array of section definitions (see below) |

### Section Fields

| Field | Required | Description |
|-------|----------|-------------|
| `heading` | Yes | Section heading/title that appears in generated doc |
| `prompt` | Yes | Instructions telling the AI what to generate for this section |
| `sources` | Yes | Array of file paths providing context for generation |
| `sections` | No | Nested subsections (for hierarchical documentation) |

## Writing Effective Prompts

Good prompts are:
- **Specific**: "Explain the authentication flow with code examples" vs "Describe authentication"
- **Actionable**: "List the top 5 features with use cases" vs "Write about features"
- **Context-aware**: "Explain for beginners" vs "Explain for experts"
- **Scoped**: Focus on one aspect per section

### Prompt Examples

**❌ Too vague**:
```json
"prompt": "Write about the API"
```

**✅ Clear and specific**:
```json
"prompt": "Document the REST API endpoints. For each endpoint, provide: (1) HTTP method and path, (2) Request parameters, (3) Response format, (4) Example curl command"
```

**❌ Too broad**:
```json
"prompt": "Explain everything about configuration"
```

**✅ Well-scoped**:
```json
"prompt": "List all configuration options with their default values, acceptable values, and what each option controls. Organize by category (Database, API, Security, etc.)"
```

## Source Specification

### Understanding Sources

Sources are **specified per-section** in your template. Each section gets its own list of source files that provide context for generating that specific section.

**Key concept**: Sources are not global—they're defined individually for each section based on what information that section needs.

```json
{
  "sections": [
    {
      "heading": "API Documentation",
      "prompt": "Document all REST endpoints",
      "sources": ["src/api/*.py", "src/models.py"]  // ← Section-specific sources
    },
    {
      "heading": "Installation",
      "prompt": "Provide installation instructions",
      "sources": ["README.md", "pyproject.toml"]     // ← Different sources
    }
  ]
}
```

### How Sources Work

When generating a section, the system:
1. **Resolves** source patterns to actual file paths
2. **Reads** each resolved file's content
3. **Provides** file contents to the AI as context
4. **AI uses** this context to generate accurate, relevant content

The AI reads these files to:
- Extract accurate information about your code
- Maintain consistency with existing documentation
- Include relevant code examples
- Understand project structure and conventions
- Reference actual implementation details

### Glob Pattern Support

Doc-evergreen uses Python's `glob` module, supporting standard glob syntax:

#### Basic Patterns

| Pattern | Matches | Example |
|---------|---------|---------|
| `*.md` | All .md files in current directory | `README.md`, `CHANGELOG.md` |
| `src/*.py` | All .py files in src/ | `src/main.py`, `src/utils.py` |
| `**/*.md` | All .md files recursively | `docs/guide.md`, `docs/api/endpoints.md` |
| `src/**/*.py` | All .py files in src/ and subdirectories | `src/api/routes.py`, `src/models/user.py` |

#### Specific File Patterns

```json
// Single file
"sources": ["README.md"]

// Multiple specific files
"sources": ["README.md", "INSTALL.md", "pyproject.toml"]

// Mix specific files and patterns
"sources": ["README.md", "src/**/*.py", "docs/architecture.md"]
```

#### Directory Patterns

```json
// All Python files in a directory
"sources": ["amplifier/memory/*.py"]

// All files recursively in a directory
"sources": ["amplifier/memory/**/*"]

// Specific file types across multiple directories
"sources": ["amplifier/*/README.md"]
```

#### Advanced Patterns

```json
// Multiple file types
"sources": ["src/**/*.{py,js,ts}"]

// Exclude patterns (use negative patterns carefully)
"sources": ["src/**/*.py"]  // Note: Exclusions handled at glob level

// All config files
"sources": ["*.toml", "*.json", "*.yaml", "*.yml"]
```

### Source Resolution

**Important**: Source paths are resolved **relative to where you run the command** (current working directory).

#### Resolution Examples

If you run from `doc_evergreen/` directory:

```json
{
  "sources": ["README.md"]           // → doc_evergreen/README.md
}
```

```json
{
  "sources": ["src/**/*.py"]         // → All .py files in doc_evergreen/src/
}
```

```json
{
  "sources": ["../amplifier/README.md"]  // → Parent dir amplifier/README.md
}
```

**Best Practice**: Paths relative to doc_evergreen/ root (where you run `make regen-doc`):

```
doc_evergreen/           ← You run make from here (cwd)
├── templates/
│   └── readme.json
├── README.md            ← Use "README.md"
├── src/
│   ├── main.py          ← Use "src/**/*.py"
│   └── utils/
│       └── helper.py    ← Matched by "src/**/*.py"
├── amplifier/           ← Parent dir
│   └── README.md        ← Use "../amplifier/README.md"
```

### Common Source Patterns

#### Pattern: README Section

```json
{
  "heading": "Overview",
  "prompt": "Summarize project purpose and key features",
  "sources": [
    "../README.md",                    // Existing README for consistency
    "../pyproject.toml",               // Project metadata
    "../docs/architecture.md"          // High-level architecture
  ]
}
```

#### Pattern: API Documentation

```json
{
  "heading": "API Reference",
  "prompt": "Document all public API endpoints with examples",
  "sources": [
    "../src/api/**/*.py",              // All API route files
    "../src/models.py",                // Data models
    "../tests/test_api.py"             // API usage examples
  ]
}
```

#### Pattern: Module Documentation

```json
{
  "heading": "Memory Module",
  "prompt": "Document the memory system architecture and usage",
  "sources": [
    "../amplifier/memory/README.md",   // Module docs
    "../amplifier/memory/*.py",        // Module implementation
    "../tests/test_memory.py"          // Usage examples
  ]
}
```

#### Pattern: Installation Guide

```json
{
  "heading": "Installation",
  "prompt": "Provide step-by-step installation instructions",
  "sources": [
    "../README.md",                    // Existing install docs
    "../pyproject.toml",               // Python dependencies
    "../package.json",                 // Node dependencies (if applicable)
    "../Dockerfile"                    // Container setup (if applicable)
  ]
}
```

### Choosing Good Sources

#### ✅ DO Include

- **Existing documentation**: Maintain consistency with current docs
- **Source code**: Extract accurate implementation details
- **Configuration files**: Show actual setup (pyproject.toml, package.json, etc.)
- **Test files**: Demonstrate real usage patterns
- **Architecture docs**: Provide high-level context
- **README files**: Use module-specific READMEs for context

#### ❌ DON'T Include

- **Generated files**: Build artifacts, compiled code
- **Binary files**: Images, PDFs (unless absolutely necessary)
- **Very large files**: Files >100KB that aren't directly relevant
- **Irrelevant files**: Files unrelated to the section topic
- **Sensitive files**: Credentials, secrets, private keys
- **Dependency code**: node_modules/, .venv/ contents

### Source File Limits

- **Per section**: 10-20 source files recommended
- **File size**: Files >100KB may hit context limits
- **Total context**: All sources combined should stay under 50KB for best results

**If you need more context**:
1. Split into multiple sections with focused sources
2. Use more specific glob patterns
3. Curate which files are most relevant
4. Consider creating summary documents as sources

### Troubleshooting Sources

#### No files matched by glob pattern

**Symptoms**: Warning or error about zero source files

**Causes**:
- Pattern is relative to template location, not current directory
- Pattern syntax is incorrect
- Files don't exist at specified paths

**Solutions**:
```json
// Check pattern is relative to template
"sources": ["../src/*.py"]  // Not "src/*.py" if template is in templates/

// Verify files exist
"sources": ["../README.md"]  // ls ../README.md from template directory

// Use more specific patterns
"sources": ["../amplifier/memory/*.py"]  // Not "../*.py"
```

#### Wrong files are being used

**Symptoms**: Generated content references unexpected files

**Causes**:
- Glob pattern too broad
- Sources include unrelated files

**Solutions**:
```json
// Bad: Too broad
"sources": ["../**/*.py"]  // Matches EVERYTHING

// Good: Specific
"sources": ["../amplifier/memory/**/*.py"]

// Better: Curated list
"sources": [
  "../amplifier/memory/core.py",
  "../amplifier/memory/store.py"
]
```

#### Sources not found relative to template

**Symptoms**: "Source file not found" errors

**Cause**: Paths are resolved from template location, not working directory

**Solution**: Always use relative paths from template:
```json
// If template is at: project/templates/readme.json
// And source is at:  project/README.md

"sources": ["../README.md"]  // Correct: Go up one level
```

## Nested Sections

Templates support hierarchical documentation through nested sections:

```json
{
  "document": {
    "title": "User Guide",
    "output": "docs/guide.md",
    "sections": [
      {
        "heading": "Getting Started",
        "prompt": "Introduction for new users",
        "sources": ["README.md"],
        "sections": [
          {
            "heading": "Installation",
            "prompt": "Step-by-step installation guide",
            "sources": ["README.md", "INSTALL.md"]
          },
          {
            "heading": "Quick Start",
            "prompt": "5-minute tutorial for first-time users",
            "sources": ["README.md", "examples/hello_world.py"]
          }
        ]
      }
    ]
  }
}
```

**When to use nested sections**:
- Creating hierarchical documentation (book-like structure)
- Organizing complex topics with subsections
- Grouping related information under parent sections

**When to use flat sections**:
- Simple documentation (README, CHANGELOG)
- Each section is independent
- No logical hierarchy needed

## Creating Your First Template

### Step 1: Define the Output

Decide where the generated documentation should go:

```json
{
  "document": {
    "title": "My Project README",
    "output": "README.md",
    "sections": []
  }
}
```

### Step 2: Identify Sections

List the major sections your documentation needs:

```json
{
  "document": {
    "title": "My Project README",
    "output": "README.md",
    "sections": [
      {"heading": "Overview", "prompt": "", "sources": []},
      {"heading": "Installation", "prompt": "", "sources": []},
      {"heading": "Usage", "prompt": "", "sources": []},
      {"heading": "API Reference", "prompt": "", "sources": []}
    ]
  }
}
```

### Step 3: Write Prompts

For each section, write clear instructions:

```json
{
  "heading": "Overview",
  "prompt": "Explain what this project does, its main purpose, and key features. Keep it concise (2-3 paragraphs) and focus on value to users.",
  "sources": []
}
```

### Step 4: Add Sources

Identify which files contain relevant information:

```json
{
  "heading": "Overview",
  "prompt": "Explain what this project does, its main purpose, and key features. Keep it concise (2-3 paragraphs) and focus on value to users.",
  "sources": ["README.md", "docs/architecture.md", "pyproject.toml"]
}
```

### Step 5: Test and Refine

Generate documentation and review:

```bash
regen-doc my-template.json
```

Refine prompts and sources based on the output quality.

## Examples

### Simple Template (2 sections)

See `examples/simple.json` for a minimal template with:
- Overview section
- Installation section

**Use case**: Quick README generation for small projects

### Advanced Template (nested sections)

See `examples/nested.json` for a hierarchical template with:
- Getting Started (parent)
  - Installation (child)
  - Configuration (child)
- Usage (parent)
  - Basic Usage (child)
  - Advanced Usage (child)

**Use case**: Comprehensive documentation for larger projects

### Production Template

See `templates/amplifier_readme.json` for a real-world example with:
- 9 top-level sections
- Multiple source files per section
- Detailed prompts for consistent output

**Use case**: Maintaining complex project documentation

## Using Templates

### Generate Documentation

```bash
# Generate from template with approval prompt
regen-doc templates/my-template.json

# Auto-approve changes (no prompt)
regen-doc --auto-approve templates/my-template.json

# Override output path
regen-doc --output docs/custom.md templates/my-template.json
```

### Workflow

1. **Create template**: Define structure, prompts, sources
2. **Generate docs**: Run `regen-doc template.json`
3. **Review changes**: Check the diff output
4. **Approve or reject**: Type 'y' to apply, 'n' to abort
5. **Refine**: Update prompts/sources if needed
6. **Regenerate**: Run again as code changes

## Best Practices

### Template Organization

```
project/
├── templates/           # Production templates
│   └── readme.json
├── examples/            # Example templates
│   ├── simple.json
│   └── nested.json
└── docs/
    └── generated/       # Output location
```

### Version Control

**✅ Commit templates**: Track template changes in git
**✅ Review generated docs**: Check output before committing
**❌ Don't commit temp files**: .gitignore any test outputs

### Maintenance

- **Update prompts** when output quality degrades
- **Add sources** when new relevant files are created
- **Remove sources** for deleted or moved files
- **Refine sections** based on actual documentation needs

## Troubleshooting

### "No changes detected"

**Cause**: Generated content matches existing file exactly

**Solution**: This is expected if sources haven't changed. Try:
- Updating source files with new information
- Refining prompts to generate different content
- Checking if sources are being read correctly

### "Template parsing failed"

**Cause**: Invalid JSON syntax

**Solution**: Validate your JSON:
```bash
python -m json.tool < my-template.json
```

Common issues:
- Missing commas between array items
- Trailing commas (not allowed in JSON)
- Unquoted keys or values
- Mismatched brackets

### "Source file not found"

**Cause**: Source path is incorrect or file doesn't exist

**Solution**:
- Use paths relative to where you run the command
- Check for typos in file paths
- Verify files exist: `ls -la path/to/source.md`

### Generated content is off-topic

**Cause**: Prompts are too vague or sources are irrelevant

**Solution**:
- Make prompts more specific and detailed
- Add more relevant source files
- Remove sources that don't relate to the section
- Break large sections into smaller focused sections

## Next Steps

1. **Start simple**: Use `examples/simple.json` as a starting point
2. **Test locally**: Generate docs and review output
3. **Iterate**: Refine prompts and sources based on results
4. **Scale up**: Add more sections as you understand the system
5. **Maintain**: Regenerate docs as your codebase evolves

## Additional Resources

- **Sprint 8 Documentation**: See `ai_working/doc_evergreen/sprints/v0.3.0-test-case-basic-regen/SPRINT_08_TEMPLATE_PARSER.md` for implementation details
- **Schema Reference**: See `doc_evergreen/core/template_schema.py` for data structures
- **CLI Help**: Run `regen-doc --help` for command options

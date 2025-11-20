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

## Source Files

### How Sources Work

Sources provide context to the AI when generating content. The AI reads these files and uses them to:
- Extract accurate information
- Maintain consistency with existing docs
- Include relevant code examples
- Understand project structure

### Source File Patterns

You can specify sources in multiple ways:

**Exact paths**:
```json
"sources": ["README.md", "src/auth.py"]
```

**Glob patterns** (wildcards):
```json
"sources": ["docs/**/*.md", "src/**/*.py"]
```

**Multiple related files**:
```json
"sources": [
  "amplifier/memory/README.md",
  "amplifier/extraction/README.md",
  "amplifier/search/README.md"
]
```

### Choosing Good Sources

**✅ Include**:
- Existing documentation you want to maintain consistency with
- Source code files containing implementation details
- Configuration files (pyproject.toml, package.json, etc.)
- Architecture documents and design docs

**❌ Avoid**:
- Generated files (build artifacts)
- Binary files
- Very large files that don't contain relevant info
- Files unrelated to the section being generated

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

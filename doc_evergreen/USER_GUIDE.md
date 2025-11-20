# doc_evergreen User Guide

**AI-powered documentation that stays in sync with your code**

---

## Table of Contents

- [What is doc_evergreen?](#what-is-doc_evergreen)
- [Quick Start](#quick-start)
- [Core Concepts](#core-concepts)
- [Creating Templates](#creating-templates)
- [Using the CLI](#using-the-cli)
- [Workflows](#workflows)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)
- [Advanced Usage](#advanced-usage)
- [Examples](#examples)

---

## What is doc_evergreen?

doc_evergreen is a template-based documentation generator that uses AI to keep your documentation in sync with your evolving codebase.

### The Problem It Solves

Documentation gets out of sync with code. Developers update implementation but forget to update docs. Users read outdated documentation and get confused. Teams spend hours manually maintaining docs.

### The Solution

Define documentation structure once in a template. As your code evolves, regenerate docs with a single command. Preview exactly what changed. Approve or reject. Iterate until perfect.

### Key Benefits

- **Stay in sync**: Regenerate docs as code changes
- **Preview changes**: See diff before applying updates
- **Iterate freely**: Refine multiple times without restarting
- **Real-time feedback**: Watch progress during generation
- **Clear errors**: Actionable messages when something's wrong

---

## Quick Start

Get productive in 5 minutes.

### Installation

```bash
# Install doc_evergreen
pip install doc-evergreen

# Verify installation
doc-evergreen --help
```

### Create Your First Template

Create `templates/readme.json`:

```json
{
  "document": {
    "title": "My Project README",
    "output": "README.md",
    "sections": [
      {
        "heading": "Overview",
        "prompt": "Explain what this project does and who it's for",
        "sources": ["README.md", "pyproject.toml"]
      },
      {
        "heading": "Installation",
        "prompt": "Provide step-by-step installation instructions",
        "sources": ["README.md", "setup.py", "pyproject.toml"]
      }
    ]
  }
}
```

### Generate Documentation

```bash
# Generate with preview and approval
regen-doc templates/readme.json

# Auto-approve for CI/CD
regen-doc --auto-approve templates/readme.json
```

### Review and Approve

The tool shows you:
1. Progress as each section generates
2. Diff showing exactly what changed
3. Approval prompt - type 'y' to apply, 'n' to abort
4. Option to regenerate and refine

**That's it!** You now have AI-maintained documentation.

---

## Core Concepts

### Templates

A **template** is a JSON file defining:
- **What** to generate (sections and structure)
- **How** to generate it (prompts for AI)
- **Where** to get info (source files)
- **Where** to save it (output path)

Templates are version-controlled alongside your code.

### Sections

A **section** is one part of your documentation:
- **Heading**: The section title
- **Prompt**: Instructions telling AI what to write
- **Sources**: Files providing context for generation

Sections can nest hierarchically for complex docs.

### Sources

**Sources** are files the AI reads for context:
- Existing documentation
- Source code files
- Configuration files
- Test files showing usage

Sources are specified **per-section** - each section gets only the files it needs.

### Regeneration

**Regeneration** is the process of:
1. Reading your template
2. Generating new content from current code
3. Comparing with existing docs
4. Showing you what changed
5. Applying approved updates

Run regeneration whenever code changes significantly.

---

## Creating Templates

### Step-by-Step Guide

#### 1. Plan Your Structure

List the sections your documentation needs:

```
README.md should have:
- Overview
- Features
- Installation
- Quick Start
- Usage Examples
- API Reference
- Contributing
```

#### 2. Create Template Skeleton

```json
{
  "document": {
    "title": "My Project",
    "output": "README.md",
    "sections": [
      {"heading": "Overview", "prompt": "", "sources": []},
      {"heading": "Features", "prompt": "", "sources": []},
      {"heading": "Installation", "prompt": "", "sources": []}
    ]
  }
}
```

#### 3. Write Effective Prompts

**Good prompts are**:
- Specific: "List all REST API endpoints with request/response examples"
- Actionable: "Provide installation steps for macOS, Linux, and Windows"
- Scoped: Focus on one aspect per section

**Bad prompts**:
- Vague: "Write about the API"
- Too broad: "Explain everything"
- Ambiguous: "Make it good"

**Examples**:

```json
{
  "heading": "API Reference",
  "prompt": "Document all public API endpoints. For each endpoint: (1) HTTP method and path, (2) Request parameters with types, (3) Response format, (4) Example curl command, (5) Common errors. Organize alphabetically.",
  "sources": ["src/api/**/*.py", "tests/test_api.py"]
}
```

#### 4. Specify Sources

**Sources provide context**. Choose files that contain:
- Implementation details for accuracy
- Existing docs for consistency
- Tests for usage examples
- Config for setup information

**Source patterns**:

```json
// Specific files
"sources": ["README.md", "src/main.py"]

// Glob patterns (recursive)
"sources": ["src/**/*.py", "docs/**/*.md"]

// Module-specific
"sources": ["amplifier/memory/*.py", "amplifier/memory/README.md"]
```

**Important**: Paths are **relative to template location**. Use `../` to go up:

```
project/
├── templates/
│   └── readme.json      ← Template here
├── README.md            ← Use "../README.md"
└── src/
    └── main.py          ← Use "../src/main.py"
```

#### 5. Test and Refine

```bash
# Generate and review
regen-doc templates/readme.json

# Review the diff carefully
# Approve if good, reject if needs work

# If rejected, update prompts/sources and regenerate
# The tool offers to regenerate automatically
```

---

## Using the CLI

### Commands

#### `regen-doc`

Regenerate documentation from a template.

**Syntax**:
```bash
regen-doc [OPTIONS] TEMPLATE_PATH
```

**Options**:
- `--auto-approve`: Apply changes without approval prompt (CI/CD mode)
- `--output PATH`: Override output path from template

**Examples**:

```bash
# Standard workflow with review
regen-doc templates/readme.json

# Auto-approve for automation
regen-doc --auto-approve templates/readme.json

# Override output location
regen-doc --output custom/path.md templates/readme.json
```

### Progress Feedback

During generation, you see:

```
[1/3] Generating: Overview
      Sources: README.md, pyproject.toml (2 files)
      ✓ Complete (5.2s)

[2/3] Generating: Installation
      Sources: README.md, setup.py (2 files)
      ✓ Complete (3.8s)

[3/3] Generating: Usage
      Sources: src/main.py, examples/demo.py (2 files)
      ✓ Complete (6.1s)
```

### Change Preview

After generation, you see a diff:

```
Changes detected:
--- README.md
+++ README.md
@@ -10,7 +10,7 @@
-Old installation instructions
+## Installation
+
+pip install my-project

Apply these changes? [y/N]:
```

### Iterative Refinement

After applying changes, you can regenerate:

```
✓ File written: README.md

Regenerate with updated sources? [y/N]: y

[Generates again with updated file as context]
[Shows new diff]
[Prompts for approval]

Completed 2 iterations
```

---

## Workflows

### Initial Documentation Generation

**Scenario**: Create new documentation from scratch

**Steps**:
1. Create template defining structure
2. Write prompts for each section
3. Specify source files
4. Run `regen-doc template.json`
5. Review generated output
6. Approve and commit template + generated docs

**Best for**: New projects, major rewrites

### Updating Existing Documentation

**Scenario**: Code changed, docs need updates

**Steps**:
1. Use existing template
2. Run `regen-doc template.json`
3. Review diff showing what changed
4. Approve changes
5. Commit updated docs

**Best for**: Regular maintenance, after feature additions

### Iterative Refinement

**Scenario**: Generated docs need improvement

**Steps**:
1. Run `regen-doc template.json`
2. Review output, reject if not right
3. Update prompts or sources in template
4. When prompted "Regenerate?", choose 'y'
5. Review new output
6. Repeat until satisfied

**Best for**: Fine-tuning output quality

### CI/CD Integration

**Scenario**: Automated documentation updates

**Steps**:
1. Add to CI/CD pipeline:
   ```yaml
   - name: Update docs
     run: regen-doc --auto-approve templates/readme.json
   ```
2. Commit regenerated docs automatically
3. Or create PR with changes for review

**Best for**: Keeping docs synced automatically

### Multi-Template Projects

**Scenario**: Multiple documentation files

**Steps**:
1. Create template for each doc:
   - `templates/readme.json` → `README.md`
   - `templates/api.json` → `docs/API.md`
   - `templates/guide.json` → `docs/GUIDE.md`

2. Regenerate as needed:
   ```bash
   regen-doc templates/readme.json
   regen-doc templates/api.json
   regen-doc templates/guide.json
   ```

3. Or script it:
   ```bash
   for template in templates/*.json; do
       regen-doc --auto-approve "$template"
   done
   ```

**Best for**: Large projects with multiple docs

---

## Best Practices

### Template Design

**✅ DO**:
- Keep sections focused on single topics
- Write specific, actionable prompts
- Specify sources relevant to each section
- Use nested sections for hierarchical docs
- Version control your templates

**❌ DON'T**:
- Make sections too broad
- Use vague prompts like "write about X"
- Include irrelevant source files
- Nest more than 2-3 levels deep
- Hard-code absolute paths

### Prompt Engineering

**Effective prompts**:

```json
{
  "prompt": "Document the authentication flow. Include: (1) Supported auth methods, (2) Configuration options, (3) Code examples for each method, (4) Common errors and solutions. Use code blocks for examples."
}
```

**Ineffective prompts**:

```json
{
  "prompt": "Explain authentication"
}
```

**Tips**:
- Start with action verb: "List", "Explain", "Provide", "Document"
- Specify format: "In a bulleted list", "With code examples", "Step-by-step"
- Define scope: "For beginners", "Advanced usage only", "Top 5 features"
- Include structure: "For each item, provide: (1) X, (2) Y, (3) Z"

### Source Selection

**Choose sources that**:
- Contain information directly relevant to the section
- Are up-to-date and maintained
- Provide accurate implementation details
- Show real usage patterns (tests, examples)

**Limit sources to**:
- 10-20 files per section (keep context focused)
- Files under 100KB each (avoid huge files)
- Total <50KB per section (optimal AI context size)

**Use glob patterns wisely**:

```json
// Good: Specific scope
"sources": ["src/api/**/*.py", "tests/test_api.py"]

// Bad: Too broad
"sources": ["**/*.py"]  // Matches everything!
```

### Template Organization

```
project/
├── templates/              # Production templates
│   ├── readme.json        # Main README
│   ├── api-docs.json      # API documentation
│   └── contributing.json  # Contribution guide
├── examples/              # Example templates (from doc_evergreen)
│   ├── simple.json
│   └── nested.json
└── docs/
    └── generated/         # Generated documentation output
```

### Maintenance Strategy

**Regular maintenance**:
1. **After major features**: Regenerate affected docs
2. **Before releases**: Update all documentation
3. **Monthly reviews**: Check if prompts still produce quality output
4. **Source cleanup**: Remove references to deleted files

**Template updates**:
- Update prompts when output quality degrades
- Add new sections as features are added
- Remove outdated sections
- Refine source lists as structure changes

---

## Troubleshooting

### Common Issues

#### No Changes Detected

**Symptoms**: "No changes detected" message after generation

**Causes**:
- Source files haven't changed
- Generated content matches existing file exactly
- Template hasn't been modified

**Solutions**:
- This is expected behavior if nothing changed
- Update source files with new information
- Modify prompts to generate different content
- Check if you're using the right template

#### Template Parsing Failed

**Symptoms**: "Invalid JSON" or "Failed to parse template" error

**Causes**:
- JSON syntax errors (missing commas, brackets, quotes)
- Invalid template structure
- Missing required fields

**Solutions**:
```bash
# Validate JSON syntax
python -m json.tool < templates/your-template.json

# Check for common issues:
# - Missing commas between array items
# - Trailing commas (not allowed in JSON)
# - Unquoted keys or values
# - Mismatched brackets {}[]
```

#### Source Files Not Found

**Symptoms**: "Section 'X' has no sources - no files matched patterns"

**Causes**:
- Paths are relative to template location, not working directory
- Glob patterns don't match any files
- Files don't exist at specified paths

**Solutions**:
```json
// If template is in templates/ directory:
"sources": ["../README.md"]       // Correct: Go up to project root
"sources": ["README.md"]            // Wrong: Looks in templates/

// Verify files exist from template location:
cd templates/
ls ../README.md                     // Should show the file
```

See: `TEMPLATES.md#source-resolution` for detailed explanation.

#### Generation Takes Too Long

**Symptoms**: Generation seems stuck or very slow

**Causes**:
- Too many source files
- Source files are very large
- Complex prompts requiring deep analysis

**Solutions**:
- Reduce number of sources (be more specific)
- Use smaller, focused source files
- Split large sections into smaller ones
- Simplify prompts to be more directed

#### Wrong Content Generated

**Symptoms**: Generated content is off-topic or irrelevant

**Causes**:
- Prompts are too vague
- Wrong source files included
- Sources don't contain relevant information

**Solutions**:
- Make prompts more specific and detailed
- Review sources - are they relevant to the section?
- Add better source files with actual information
- Break broad sections into focused subsections

---

## Advanced Usage

### Nested Sections

Create hierarchical documentation:

```json
{
  "sections": [
    {
      "heading": "Getting Started",
      "prompt": "Introduction for new users",
      "sources": ["README.md"],
      "sections": [
        {
          "heading": "Installation",
          "prompt": "Install instructions",
          "sources": ["README.md", "INSTALL.md"]
        },
        {
          "heading": "Configuration",
          "prompt": "Configuration guide",
          "sources": ["config.py", "README.md"]
        }
      ]
    }
  ]
}
```

**Output**:
```markdown
# Getting Started

Introduction content...

## Installation

Installation content...

## Configuration

Configuration content...
```

**Use nested sections for**:
- Book-like documentation structure
- Complex topics with natural hierarchy
- Organizing related subsections under parent topics

### Complex Source Patterns

**Multiple file types**:
```json
"sources": ["src/**/*.{py,js,ts}", "docs/**/*.md"]
```

**Specific module documentation**:
```json
"sources": ["amplifier/*/README.md"]  // All module READMEs
```

**Excluding patterns** (at directory level):
```json
"sources": ["src/**/*.py"]  // Gets all Python, excludes node_modules naturally
```

### Template Variables

Currently, doc_evergreen uses simple JSON structure without variable interpolation. If you need dynamic content, handle it in prompts:

```json
{
  "prompt": "List all Python dependencies from pyproject.toml. For each dependency, show: name, version constraint, and purpose in the project.",
  "sources": ["pyproject.toml"]
}
```

### Output Path Overrides

Temporarily generate to different location:

```bash
# Test template without overwriting production docs
regen-doc --output test/README.md templates/readme.json

# Generate multiple variants
regen-doc --output docs/README-v2.md templates/readme.json
```

---

## Examples

doc_evergreen includes several example templates:

### Simple Template (`examples/simple.json`)

**What it demonstrates**:
- Basic 2-section template
- Simple structure
- Straightforward prompts

**When to use**:
- Learning the system
- Small projects
- Quick README generation

### Nested Template (`examples/nested.json`)

**What it demonstrates**:
- Hierarchical section structure
- Parent/child relationships
- Complex documentation organization

**When to use**:
- Large documentation projects
- User guides with chapters
- Technical manuals

### CLI Tool Guide (`templates/cli_tool_guide.json`)

**What it demonstrates**:
- Documenting command-line tools
- Commands and options documentation
- Workflow guides

**When to use**:
- CLI tool projects
- Developer tools
- Command reference generation

### Multi-Component Library (`templates/amplifier_readme.json`)

**What it demonstrates**:
- Multiple module documentation
- Cross-referencing
- Complex project structure
- 9 comprehensive sections

**When to use**:
- Multi-package projects
- Library documentation
- Comprehensive README generation

### Self-Documenting (`templates/self_documenting.json`)

**What it demonstrates**:
- doc_evergreen documenting itself
- Meta-documentation pattern
- Feature showcasing

**When to use**:
- Understanding doc_evergreen capabilities
- Learning advanced patterns
- Self-referential documentation

---

## Getting Help

### Documentation

- **TEMPLATES.md**: Complete template creation guide
- **USER_GUIDE.md**: This document - end-to-end usage
- **Sprint planning docs**: `ai_working/doc_evergreen/sprints/` - design decisions

### Command Help

```bash
regen-doc --help
```

### Issues

If you encounter bugs or have feature requests, check existing issues or create a new one in the project repository.

---

## What's Next?

After reading this guide:

1. **Try the quick start** - Get hands-on experience
2. **Review examples** - See real templates in action
3. **Create your template** - Start with simple, iterate to complex
4. **Regenerate regularly** - Keep docs in sync with code

**Remember**: Documentation is a living artifact. Regenerate often, iterate freely, and keep your docs truthful to your code.

---

## Version

This guide is for doc_evergreen v0.3.0

**Changelog**:
- v0.3.0: Template-based regeneration, progress feedback, iterative refinement
- v0.2.0: Chunked generation mode
- v0.1.0: Initial proof of concept

# doc_evergreen Best Practices

**Patterns and principles for effective template-based documentation**

---

## Template Design Principles

### Single Responsibility Per Section

**✅ Good**: Each section has one clear purpose

```json
{
  "heading": "Installation",
  "prompt": "Provide step-by-step installation instructions for all platforms",
  "sources": ["README.md", "pyproject.toml"]
}
```

**❌ Bad**: Section tries to do too much

```json
{
  "heading": "Setup and Configuration and Usage",
  "prompt": "Explain how to install, configure, and use the tool",
  "sources": ["**/*"]
}
```

**Why**: Focused sections produce better content and are easier to regenerate individually.

### Prompt Specificity

**✅ Good**: Detailed, structured prompts

```json
{
  "prompt": "Document the REST API. For each endpoint provide: (1) HTTP method and path, (2) Request body schema, (3) Response format with status codes, (4) curl example, (5) Error cases. Organize alphabetically by endpoint path."
}
```

**❌ Bad**: Vague, unstructured prompts

```json
{
  "prompt": "Write about the API"
}
```

**Pattern**: Use the format "For each X, provide: (1) Y, (2) Z"

### Source Curation

**✅ Good**: Targeted, relevant sources

```json
{
  "heading": "Authentication",
  "prompt": "Document auth flow and configuration",
  "sources": [
    "../src/auth/core.py",
    "../src/auth/middleware.py",
    "../docs/security.md",
    "../tests/test_auth.py"
  ]
}
```

**❌ Bad**: Kitchen-sink approach

```json
{
  "sources": [
    "../**/*.py",      // Too broad!
    "../**/*.md",      // Includes everything!
    "../**/*.json"
  ]
}
```

**Why**: Focused sources = better AI context = higher quality output.

---

## Prompt Engineering Patterns

### The "For Each" Pattern

**Use when**: Documenting multiple similar items

**Template**:
```json
{
  "prompt": "For each [ITEM], provide: (1) [ASPECT_1], (2) [ASPECT_2], (3) [ASPECT_3]. [ORGANIZATION_INSTRUCTION]."
}
```

**Example**:
```json
{
  "prompt": "For each CLI command, provide: (1) Syntax and options, (2) Description and use case, (3) Complete example with output. Organize alphabetically."
}
```

### The "Step-by-Step" Pattern

**Use when**: Creating procedural guides

**Template**:
```json
{
  "prompt": "Provide step-by-step instructions for [TASK]. Each step should: (1) Start with action verb, (2) Include command or code, (3) Explain expected outcome. Number each step."
}
```

**Example**:
```json
{
  "prompt": "Provide step-by-step setup instructions. Each step should: (1) State what to do, (2) Show exact command to run, (3) Describe what success looks like. Include verification steps."
}
```

### The "Showcase" Pattern

**Use when**: Demonstrating features

**Template**:
```json
{
  "prompt": "List the top [N] [FEATURES]. For each feature: (1) Name and one-line description, (2) Benefit to users, (3) Simple code example. Use bullet points."
}
```

**Example**:
```json
{
  "prompt": "List the top 5 features of doc_evergreen. For each: (1) Feature name and description, (2) User benefit, (3) Usage example. Use engaging language."
}
```

### The "Reference" Pattern

**Use when**: Creating API/technical references

**Template**:
```json
{
  "prompt": "Document all [ITEMS] in the [MODULE]. For each, provide: function signature, parameters with types, return value, description, example usage. Format as markdown code blocks."
}
```

**Example**:
```json
{
  "prompt": "Document all public functions in the memory module. For each: function signature, parameters with types and descriptions, return value, 2-sentence description, code example showing typical usage."
}
```

---

## Source Organization Strategies

### Layer Sources by Detail Level

**Pattern**: Order sources from high-level to detailed

```json
{
  "sources": [
    "../README.md",              // High-level overview first
    "../docs/architecture.md",   // Architecture context
    "../src/core/*.py",          // Implementation details
    "../tests/test_core.py"      // Usage examples
  ]
}
```

**Why**: AI builds context progressively - start broad, get specific.

### Module-Scoped Sources

**Pattern**: One section per module with module-specific sources

```json
{
  "heading": "Memory Module",
  "sources": [
    "../amplifier/memory/README.md",
    "../amplifier/memory/*.py",
    "../tests/test_memory.py"
  ]
},
{
  "heading": "Search Module",
  "sources": [
    "../amplifier/search/README.md",
    "../amplifier/search/*.py",
    "../tests/test_search.py"
  ]
}
```

**Why**: Keeps context focused, prevents cross-contamination.

### Version-Aware Sources

**Pattern**: Include version/changelog info for accuracy

```json
{
  "heading": "What's New",
  "prompt": "Summarize recent changes and new features",
  "sources": [
    "../CHANGELOG.md",
    "../pyproject.toml",  // Version number
    "../README.md"
  ]
}
```

---

## Template Maintenance

### When to Update Templates

**Update prompts when**:
- Output quality degrades
- Project structure changes significantly
- New features need documentation
- User feedback indicates confusion

**Update sources when**:
- Files are moved or renamed
- New relevant files are added
- Old files are deleted
- Module structure changes

### Template Versioning

**Keep templates in git**:

```bash
git add templates/readme.json
git commit -m "docs: update readme template with new features section"
```

**Tag template versions**:

```json
{
  "document": {
    "title": "My Project README",
    "metadata": {
      "template_version": "1.2.0",
      "last_updated": "2025-01-20"
    }
  }
}
```

### Review Cycle

**Monthly review checklist**:
- [ ] Do generated docs match current code?
- [ ] Are all source files still relevant?
- [ ] Do prompts produce quality output?
- [ ] Are new features documented?
- [ ] Should any sections be split or merged?

---

## Common Patterns

### Pattern: Comprehensive README

**Structure**:
```json
{
  "sections": [
    {"heading": "Overview", "prompt": "What and why (2-3 paragraphs)"},
    {"heading": "Features", "prompt": "Top 5-7 features with benefits"},
    {"heading": "Quick Start", "prompt": "5-minute getting started"},
    {"heading": "Installation", "prompt": "Step-by-step install guide"},
    {"heading": "Usage", "prompt": "Common usage examples"},
    {"heading": "API Reference", "prompt": "Complete API docs"},
    {"heading": "Contributing", "prompt": "How to contribute"},
    {"heading": "License", "prompt": "License and attribution"}
  ]
}
```

### Pattern: API Documentation

**Structure**:
```json
{
  "sections": [
    {"heading": "Overview", "prompt": "API design philosophy"},
    {"heading": "Authentication", "prompt": "Auth methods and setup"},
    {"heading": "Endpoints", "prompt": "All endpoints with examples"},
    {"heading": "Data Models", "prompt": "Request/response schemas"},
    {"heading": "Error Handling", "prompt": "Error codes and meanings"},
    {"heading": "Rate Limits", "prompt": "Rate limiting policies"},
    {"heading": "Examples", "prompt": "Complete usage examples"}
  ]
}
```

### Pattern: User Guide

**Structure**:
```json
{
  "sections": [
    {"heading": "Introduction", "prompt": "What this guide covers"},
    {"heading": "Getting Started", "sections": [
      {"heading": "Installation"},
      {"heading": "Configuration"},
      {"heading": "First Steps"}
    ]},
    {"heading": "Core Concepts", "prompt": "Key concepts explained"},
    {"heading": "Workflows", "prompt": "Common usage patterns"},
    {"heading": "Advanced Topics", "sections": [
      {"heading": "Customization"},
      {"heading": "Integration"},
      {"heading": "Performance"}
    ]},
    {"heading": "Troubleshooting", "prompt": "Common issues and solutions"}
  ]
}
```

---

## Anti-Patterns to Avoid

### Anti-Pattern: Monolithic Sections

**❌ Problem**:
```json
{
  "heading": "Everything About The Project",
  "prompt": "Write comprehensive documentation covering all aspects",
  "sources": ["**/*"]
}
```

**✅ Solution**: Break into focused sections

```json
{
  "sections": [
    {"heading": "Overview", "prompt": "Project purpose and features"},
    {"heading": "Architecture", "prompt": "System design and components"},
    {"heading": "Usage", "prompt": "How to use each component"}
  ]
}
```

### Anti-Pattern: Prompt Ambiguity

**❌ Problem**:
```json
{
  "prompt": "Make it good and explain things clearly"
}
```

**✅ Solution**: Be specific about what and how

```json
{
  "prompt": "Explain the authentication system. Include: supported methods (OAuth, JWT, API keys), configuration steps for each, code examples, and security best practices. Use h3 headings for each method."
}
```

### Anti-Pattern: Source Overload

**❌ Problem**:
```json
{
  "sources": [
    "../**/*.py",
    "../**/*.md",
    "../**/*.json",
    "../**/*.yaml"
  ]
}
```

**✅ Solution**: Curate relevant sources only

```json
{
  "sources": [
    "../src/api/routes.py",
    "../src/api/models.py",
    "../docs/api-spec.md"
  ]
}
```

### Anti-Pattern: Nested Overuse

**❌ Problem**: 5 levels of nesting

```json
{
  "sections": [{
    "heading": "Part 1",
    "sections": [{
      "heading": "Chapter 1",
      "sections": [{
        "heading": "Section 1",
        "sections": [{
          "heading": "Subsection 1",
          "sections": [...]  // Too deep!
        }]
      }]
    }]
  }]
}
```

**✅ Solution**: Keep nesting to 2-3 levels max

```json
{
  "sections": [
    {
      "heading": "Getting Started",
      "sections": [
        {"heading": "Installation"},
        {"heading": "Quick Start"}
      ]
    },
    {
      "heading": "User Guide",
      "sections": [
        {"heading": "Basic Usage"},
        {"heading": "Advanced Features"}
      ]
    }
  ]
}
```

---

## Quality Checklist

Before committing a template, verify:

- [ ] **Prompts are specific** - No vague "write about X"
- [ ] **Sources are curated** - Only relevant files included
- [ ] **Paths are relative** - Use `../` from template location
- [ ] **Sections are focused** - Each has single clear purpose
- [ ] **Structure is logical** - Flow makes sense to readers
- [ ] **Examples work** - Test with `regen-doc` command
- [ ] **Nesting is reasonable** - Max 2-3 levels
- [ ] **JSON is valid** - Validate with `json.tool`

---

## Iteration Strategies

### Strategy 1: Prompt Refinement

**Process**:
1. Run with initial prompt
2. Review output - what's missing or wrong?
3. Refine prompt to be more specific
4. Regenerate (choose 'y' when prompted)
5. Repeat until satisfied

**Example iteration**:
```
Iteration 1: "Document the API"
→ Too vague, generic output

Iteration 2: "Document all REST endpoints with examples"
→ Better, but missing error handling

Iteration 3: "Document all REST endpoints. For each: method, path, params, response, errors, curl example"
→ Perfect!
```

### Strategy 2: Source Tuning

**Process**:
1. Start with minimal sources
2. Generate and review
3. If content lacks detail, add more sources
4. If content is off-topic, remove irrelevant sources
5. Regenerate and compare

**Example**:
```
Iteration 1: sources: ["README.md"]
→ Too high-level

Iteration 2: sources: ["README.md", "src/**/*.py"]
→ Too much implementation detail

Iteration 3: sources: ["README.md", "src/api/*.py", "tests/test_api.py"]
→ Just right!
```

### Strategy 3: Structure Evolution

**Process**:
1. Start with flat sections
2. Generate and review flow
3. Identify natural groupings
4. Add nesting where it clarifies
5. Avoid over-nesting

**Evolution example**:
```
v1: Flat structure (6 top-level sections)
v2: Group related topics (3 parents, 2 children each)
v3: Adjust based on reader feedback
```

---

## Performance Optimization

### Keep Sources Focused

**Slow** (100+ files):
```json
{
  "sources": ["../src/**/*.py"]  // Might match 200+ files
}
```

**Fast** (10-20 files):
```json
{
  "sources": [
    "../src/api/*.py",
    "../src/models.py"
  ]
}
```

### Limit Context Size

**Target**: 10-50KB of source content per section

**Check source size**:
```bash
# See total size of sources
du -sh src/api/*.py | awk '{sum+=$1} END {print sum}'
```

**If too large**:
- Use more specific glob patterns
- Split section into smaller parts
- Create summary documents as sources

### Cache Awareness

doc_evergreen doesn't cache yet, so:
- Expect generation to take time for first run
- Subsequent runs with same sources take similar time
- Plan for 5-10 seconds per section

---

## Integration Patterns

### CI/CD Pipeline

**GitHub Actions example**:

```yaml
name: Update Documentation
on:
  push:
    paths:
      - 'src/**'
      - 'templates/**'

jobs:
  docs:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Setup Python
        uses: actions/setup-python@v2
      - name: Install doc_evergreen
        run: pip install doc-evergreen
      - name: Regenerate docs
        run: regen-doc --auto-approve templates/readme.json
      - name: Commit changes
        run: |
          git config user.name "Documentation Bot"
          git add README.md
          git commit -m "docs: regenerate README" || true
          git push
```

### Pre-commit Hook

**Pattern**: Regenerate docs before committing code

```bash
#!/bin/bash
# .git/hooks/pre-commit

# Regenerate critical docs
regen-doc --auto-approve templates/readme.json

# Add updated docs to commit
git add README.md
```

### Manual Review Workflow

**Pattern**: Review before auto-applying

```bash
# Generate and review manually
regen-doc templates/readme.json

# Review diff carefully
# Approve only if quality meets standards

# If rejected, refine template
# Regenerate when prompted: y
```

---

## Documentation-as-Code Principles

### Treat Templates Like Code

**Version control**:
- Commit templates to git
- Review template changes in PRs
- Document why prompts were changed

**Code review templates**:
- Review prompts for clarity
- Check sources are relevant
- Verify structure is logical

### Semantic Versioning for Templates

**When to bump version**:
- **Major** (2.0.0): Complete restructure, breaking changes to output
- **Minor** (1.1.0): New sections added, prompts enhanced
- **Patch** (1.0.1): Typo fixes, source path updates

### Test Template Changes

**Before committing template changes**:

```bash
# Regenerate with new template
regen-doc templates/readme.json

# Review diff - is this what you wanted?
# Approve if good

# Run tests to ensure no breakage
pytest

# Commit template and regenerated docs together
git add templates/readme.json README.md
git commit -m "docs: enhance API documentation template"
```

---

## Team Collaboration

### Template Ownership

**Assign owners**:
- `templates/readme.json` → @tech-writer
- `templates/api-docs.json` → @backend-team
- `templates/user-guide.json` → @product-team

**Benefits**:
- Clear responsibility
- Quality ownership
- Faster reviews

### Shared Prompt Library

**Create reusable prompt patterns**:

```markdown
# team/prompts.md

## API Endpoint Documentation
"Document this API endpoint. Provide: (1) HTTP method and path, (2) Request schema, (3) Response schema with status codes, (4) curl example, (5) Error cases."

## Installation Guide
"Provide installation instructions. For each platform (macOS, Linux, Windows): (1) Prerequisites, (2) Installation command, (3) Verification step. Use code blocks."
```

**Reference in templates**:
```json
{
  "prompt": "See team/prompts.md#api-endpoint-documentation. Apply to all endpoints in auth module."
}
```

### Documentation Standards

**Team agreement on**:
- Tone and voice (formal vs. casual)
- Code example style (full vs. minimal)
- Heading levels and structure
- Terminology (consistent naming)

**Encode in templates**:
```json
{
  "prompt": "Use friendly, conversational tone. Address reader as 'you'. Keep examples minimal but complete. Use active voice."
}
```

---

## Migration Strategy

### Migrating from Manual Docs

**Step 1**: Create template matching current structure

```json
// Mirror your existing README.md structure
{
  "sections": [
    {"heading": "Overview"},      // Maps to existing "Overview" section
    {"heading": "Installation"},  // Maps to existing "Installation" section
    {"heading": "Usage"}          // Maps to existing "Usage" section
  ]
}
```

**Step 2**: Write prompts that would recreate current docs

```json
{
  "heading": "Overview",
  "prompt": "Provide a 2-paragraph overview explaining the project purpose and key features. Match the style and tone of the existing README."
}
```

**Step 3**: Generate and compare

```bash
regen-doc templates/readme.json
# Review diff - should be minimal if prompts are good
```

**Step 4**: Iterate to match existing style

**Step 5**: Commit template, delete manual maintenance notes

---

## Advanced Techniques

### Multi-Pass Generation

**Pattern**: Generate outline first, then expand

**Template 1** (outline):
```json
{
  "prompt": "Create a detailed outline for [TOPIC]. Use h2 and h3 headings. Include bullet points for key sub-topics. No full paragraphs yet."
}
```

**Template 2** (full content):
```json
{
  "prompt": "Expand the outline in [OUTPUT_FROM_TEMPLATE_1]. For each section, write 2-3 paragraphs with examples."
}
```

### Cross-Reference Generation

**Pattern**: Later sections reference earlier ones

```json
{
  "sections": [
    {
      "heading": "Core Concepts",
      "prompt": "Define key terms: templates, sections, sources, regeneration."
    },
    {
      "heading": "Advanced Usage",
      "prompt": "Explain advanced features. Reference the terms defined in 'Core Concepts' section. Assume reader understands basics."
    }
  ]
}
```

**Why**: Context accumulates - later sections can build on earlier ones.

### Conditional Sections

**Pattern**: Include sections only when sources exist

```json
{
  "heading": "Docker Support",
  "prompt": "Document Docker setup if Dockerfile exists. Otherwise, skip this section.",
  "sources": ["../Dockerfile", "../docker-compose.yml"]
}
```

*Note: Currently requires manual template editing. Future versions may support conditional sections.*

---

## Measuring Success

### Quality Metrics

**Good documentation**:
- [ ] Accurate (matches current code)
- [ ] Complete (covers all features)
- [ ] Clear (beginners can understand)
- [ ] Concise (no unnecessary verbosity)
- [ ] Consistent (terminology and style)
- [ ] Current (recently regenerated)

### Usage Metrics

**Track**:
- How often you regenerate (weekly? after features?)
- How many iterations per regeneration (1-2 is good)
- How often you update templates (prompts or sources)
- User questions about features (indicates doc gaps)

### Iteration Efficiency

**Good iteration pattern**:
- Iteration 1: Generate initial version (approve)
- Iteration 2: Refine prompt, regenerate (approve)
- Done (2 iterations)

**Poor iteration pattern**:
- Iteration 1-5: Keep tweaking without clear improvement
- Indicates prompts need rethinking, not minor edits

---

## Summary

**Key principles**:
1. **Focused sections** - One clear purpose each
2. **Specific prompts** - Detailed, structured instructions
3. **Curated sources** - Relevant files only
4. **Regular regeneration** - Keep docs current
5. **Iterative refinement** - Use the tool's iteration feature
6. **Template versioning** - Track changes over time

**Remember**: Good templates are:
- Clear enough for AI to understand
- Specific enough to produce quality
- Flexible enough to evolve with your project
- Simple enough to maintain

**The goal**: Documentation that truthfully reflects your code, regenerated effortlessly.

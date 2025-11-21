# Sprint 13: Documentation & Production Validation

**Duration:** 1 day
**Goal:** Production-ready documentation and real-world validation
**Value Delivered:** Users have complete guides and confidence the tool works in production

---

## Why This Sprint?

Sprints 11-12 built the features. Sprint 13 validates they work in real scenarios and documents everything comprehensively. This is the polish that transforms "works for me" into "ready to ship."

---

## Deliverables

### 1. Installation & Migration Guide (~300 lines)

**What it does:**
- Complete installation instructions
- Migration guide from v0.3.0
- Breaking changes clearly explained
- Step-by-step migration checklist
- Troubleshooting common issues

**Why this sprint:**
- Users need clear onboarding path
- Breaking changes require careful communication
- Migration reduces friction for existing users
- Installation is first impression

**Files created/modified:**
- Create `INSTALLATION.md` (new)
- Create `MIGRATION_v0.3_to_v0.4.md` (new)
- Update main README.md

**Installation guide structure:**
```markdown
# Installing doc-evergreen

## Quick Install

### Using pipx (Recommended)
```bash
pipx install git+https://github.com/user/doc-evergreen.git
```

### Using pip
```bash
pip install git+https://github.com/user/doc-evergreen.git
```

## Verification
```bash
doc-evergreen --help
```

## First Project
```bash
cd your-project
doc-evergreen init
doc-evergreen regen readme
```

## Uninstalling
```bash
pipx uninstall doc-evergreen
# or
pip uninstall doc-evergreen
```

## Troubleshooting
[Common installation issues and solutions]
```

**Migration guide structure:**
```markdown
# Migrating from v0.3.0 to v0.4.0

## Breaking Changes

### 1. Source Path Resolution
**v0.3.0**: Sources relative to template location
**v0.4.0**: Sources relative to cwd (project root)

**Migration**:
- If template was in same directory as project: No change needed
- If template was in subdirectory: Update source paths

### 2. Installation Required
**v0.3.0**: Run from repository
**v0.4.0**: Install globally with pip/pipx

**Migration**:
```bash
cd /path/to/doc-evergreen
pip install -e .
```

### 3. Template Location Convention
**v0.3.0**: Templates anywhere
**v0.4.0**: Recommended in `.doc-evergreen/`

**Migration**:
```bash
mkdir .doc-evergreen
mv templates/*.json .doc-evergreen/
# Update source paths if needed
```

## Migration Checklist
- [ ] Install doc-evergreen globally
- [ ] Create `.doc-evergreen/` in project
- [ ] Move templates to `.doc-evergreen/`
- [ ] Update source paths (if needed)
- [ ] Test regeneration: `doc-evergreen regen readme`
- [ ] Update any scripts/automation
```

### 2. Updated User Guide (~400 lines modifications)

**What it does:**
- Updates all examples to use v0.4.0 conventions
- Adds section on `.doc-evergreen/` convention
- Updates workflows to use global command
- Clarifies cwd-relative path resolution

**Why this sprint:**
- Existing guide assumes v0.3.0 model
- Users need updated examples
- Conventions need clear explanation
- Workflows have changed

**Files modified:**
- `USER_GUIDE.md` - Major updates throughout

**Key sections to update:**
1. **Quick Start** - Use `init` command, show convention
2. **Creating Templates** - Explain cwd-relative sources
3. **Workflows** - Use short template names
4. **Best Practices** - Recommend `.doc-evergreen/`
5. **Troubleshooting** - Add path resolution issues

### 3. Convention Best Practices (~200 lines)

**What it does:**
- Documents `.doc-evergreen/` convention thoroughly
- Explains when to use short names vs. absolute paths
- Project structure recommendations
- Template organization patterns

**Why this sprint:**
- Convention is new concept for users
- Need examples and rationale
- Common questions answered proactively
- Shows the "why" not just "how"

**Files modified:**
- Add section to `BEST_PRACTICES.md`

**Content:**
```markdown
## The .doc-evergreen/ Convention

### Why This Convention?

Similar to `.github/` for GitHub Actions or `.vscode/` for VS Code settings,
`.doc-evergreen/` provides a standard location for documentation templates.

**Benefits**:
- Templates travel with project
- Clear ownership (part of project, not external)
- Version controlled with code
- Zero configuration
- Familiar pattern

### Structure
```
your-project/
├── .doc-evergreen/          # Documentation templates
│   ├── readme.json          # Main README
│   ├── api.json             # API documentation
│   ├── contributing.json    # Contributor guide
│   └── changelog.json       # Changelog generation
├── README.md                # Generated files
├── API.md
└── src/                     # Your code
```

### Naming Convention
- Use descriptive names: `readme.json`, `api.json`, `contributing.json`
- Match output filename when possible
- Lowercase with hyphens: `user-guide.json`

### What to Version Control
```gitignore
# Commit templates (they're your docs definition)
.doc-evergreen/*.json

# Optionally ignore generated docs (if you regenerate in CI)
README.md
API.md
```

### When to Use Absolute Paths
Convention covers 90% of cases, but use absolute paths when:
- Sharing templates across multiple projects
- Templates maintained in separate repository
- Experimenting with template before committing
```

### 4. Real-World Validation (~time-boxed)

**What it does:**
- Test on 3+ real projects with different structures
- Validate installation on clean systems
- Test migration from v0.3.0 with actual templates
- Identify edge cases and issues
- Document limitations discovered

**Why this sprint:**
- Catch issues before users do
- Validate design decisions
- Build confidence in stability
- Discover documentation gaps

**Testing projects:**
1. **Python package** (standard structure with setup.py/pyproject.toml)
2. **Multi-module project** (complex nested structure)
3. **CLI tool** (command-line application)
4. **doc_evergreen itself** (self-documenting)

**Validation checklist per project:**
- [ ] Install tool globally
- [ ] Run `init` in project
- [ ] Customize template for project
- [ ] Verify source resolution works
- [ ] Generate documentation
- [ ] Review quality of output
- [ ] Document any issues

### 5. Example Projects (~3 templates)

**What it does:**
- Provides 3 real-world example templates
- Shows best practices in action
- Demonstrates different use cases
- Gives users starting points

**Why this sprint:**
- Examples teach better than explanations
- Users can copy and modify
- Demonstrates tool capabilities
- Validates template design patterns

**Examples to create:**

**Example 1: Python Package README**
```json
{
  "document": {
    "output": "README.md",
    "sections": [
      {
        "heading": "# My Python Package",
        "prompt": "Overview of package purpose and key features",
        "sources": ["src/**/*.py", "README.md"]
      },
      {
        "heading": "## Installation",
        "prompt": "Installation instructions",
        "sources": ["pyproject.toml", "setup.py"]
      },
      {
        "heading": "## API Reference",
        "prompt": "Document main classes and functions",
        "sources": ["src/api/**/*.py"]
      }
    ]
  }
}
```

**Example 2: CLI Tool Documentation**
- Commands and options documentation
- Usage examples
- Configuration guide

**Example 3: Multi-Module Project**
- Cross-references between modules
- Architecture overview
- Module-specific docs

**Files created:**
- `examples/python-package/` directory
- `examples/cli-tool/` directory
- `examples/multi-module/` directory

---

## What Gets Punted

- **Video tutorials** - Written docs sufficient
- **Interactive tutorial** - Static docs work
- **Automated migration tool** - Manual migration acceptable
- **Advanced examples** - 3 examples sufficient
- **Performance benchmarks** - Not needed for v0.4.0

**Why**: These are enhancements. Core documentation provides enough value.

---

## Dependencies

**Requires from Sprint 11-12:**
- Working package installation
- Convention-based discovery
- Init command functionality
- Template resolution

**Provides for v0.4.0 release:**
- Complete documentation
- Migration path from v0.3.0
- Real-world validation
- Production confidence
- Example templates

---

## Acceptance Criteria

### Must Have
- ✅ Installation guide is complete and tested
- ✅ Migration guide covers all breaking changes
- ✅ User guide updated for v0.4.0
- ✅ 3 example projects work correctly
- ✅ Real-world validation on 3+ projects complete
- ✅ All discovered issues fixed or documented
- ✅ Known limitations documented
- ✅ README.md reflects v0.4.0 capabilities

### Nice to Have (Defer if time constrained)
- ❌ Video walkthrough
- ❌ More than 3 examples
- ❌ Automated migration script

---

## Technical Approach

### Documentation Strategy
**Decision**: Comprehensive but concise
**Rationale**: Cover 90% of use cases thoroughly, link to examples for rest

### Migration Communication
**Decision**: Honest about breaking changes, clear migration path
**Rationale**: Builds trust, reduces support burden

### Validation Scope
**Decision**: 3-4 diverse projects
**Rationale**: Covers common cases without excessive time investment

---

## Testing Requirements

### TDD Approach

Focus on integration and real-world scenarios:

**For documentation:**
1. 🔴 Identify gap (what's unclear?)
2. 🟢 Write documentation
3. 🔵 Test with fresh user perspective
4. ✅ Validate with real usage

### Documentation Tests (Write First)

**Test installation guide:**
```python
def test_installation_instructions_work(clean_venv):
    """Installation guide commands actually work"""
    # Follow exact steps from INSTALLATION.md
    commands = extract_commands_from_doc("INSTALLATION.md")
    for cmd in commands:
        result = subprocess.run(cmd, shell=True)
        assert result.returncode == 0
```

**Test migration guide:**
```python
def test_migration_guide_complete(v03_project):
    """Migration guide covers all v0.3.0 scenarios"""
    # Start with v0.3.0 template
    # Follow migration guide steps
    # Verify everything works in v0.4.0
    pass
```

### Real-World Validation Tests

**Test with actual projects:**
```python
def test_python_package_example():
    """Python package example works end-to-end"""
    project = setup_python_package_project()
    os.chdir(project)

    # Follow example
    cli_runner.invoke(cli, ["init"])
    customize_template_like_example()
    result = cli_runner.invoke(cli, ["regen", "readme"])

    assert result.exit_code == 0
    assert (project / "README.md").exists()
    validate_output_quality(project / "README.md")
```

### Manual Testing (Critical for This Sprint)

**Installation testing:**
- [ ] Install on clean Ubuntu system
- [ ] Install on clean macOS system
- [ ] Install on Windows (if supported)
- [ ] Verify `doc-evergreen` command available
- [ ] Test uninstall and reinstall

**Documentation testing:**
- [ ] Have someone unfamiliar follow installation guide
- [ ] Follow migration guide with real v0.3.0 project
- [ ] Verify all code examples work
- [ ] Check all links are valid
- [ ] Test troubleshooting solutions

**Real-world project testing:**
- [ ] Test on 3+ actual projects
- [ ] Different project structures
- [ ] Various source file patterns
- [ ] Multiple template configurations

**Test Coverage Target:** >80% overall for tool, 100% manual validation for docs

---

## What You Learn

After this sprint:
1. **What documentation gaps remain?** → Can address incrementally
2. **What real-world edge cases exist?** → Informs bug fixes
3. **Is migration smooth enough?** → Validates breaking change decision
4. **What support questions arise?** → Guides FAQ section

These learnings inform v0.5.0 priorities and improvements.

---

## Success Metrics

**Quantitative:**
- Installation succeeds on 3+ platforms
- Migration guide works for 100% of v0.3.0 users
- All examples generate valid output
- Zero critical issues in validation
- All documentation code samples work

**Qualitative:**
- New user succeeds with installation guide alone
- Migration feels straightforward, not painful
- Examples feel professional and realistic
- Team confident shipping v0.4.0
- "Just works" on real projects

---

## Implementation Order (TDD Daily Workflow)

### Morning (4 hours): Documentation

**Hour 1-2: Installation & Migration Guides**
- Write INSTALLATION.md
- Write MIGRATION_v0.3_to_v0.4.md
- Test commands in guides
- Get feedback on clarity
- ✅ Commit: "docs: add installation and migration guides"

**Hour 3-4: Update User Guide**
- Update USER_GUIDE.md for v0.4.0
- Update all examples to use convention
- Add troubleshooting section
- Review for completeness
- ✅ Commit: "docs: update user guide for v0.4.0"

### Afternoon (4 hours): Validation & Examples

**Hour 5-6: Real-World Validation**
- Test on 3 different projects
- Document any issues found
- Fix critical bugs
- Document limitations
- ✅ Commit: "test: validate on real-world projects"

**Hour 7: Example Projects**
- Create 3 example templates
- Test each example end-to-end
- Document in examples/README.md
- ✅ Commit: "docs: add example templates"

**Hour 8: Final Polish**
- Run full test suite
- Manual testing checklist
- Documentation review
- Update main README.md
- ✅ Final commit: "chore: prepare v0.4.0 release"
- ✅ Tag: v0.4.0

---

## Known Limitations (By Design)

1. **Git install only** - No PyPI yet (acceptable for v0.4.0)
2. **Breaking changes** - Migration required from v0.3.0
3. **Manual migration** - No automated tool (acceptable)
4. **Limited examples** - 3 examples (can add more later)
5. **English only** - Documentation in English (can translate later)

---

## Release Checklist

Before tagging v0.4.0:

**Code Quality:**
- [ ] All tests pass (>80% coverage)
- [ ] No critical bugs
- [ ] Performance acceptable
- [ ] Code reviewed

**Documentation:**
- [ ] Installation guide complete
- [ ] Migration guide complete
- [ ] User guide updated
- [ ] Best practices documented
- [ ] Examples work
- [ ] README.md updated
- [ ] CHANGELOG.md updated

**Validation:**
- [ ] Works on 3+ real projects
- [ ] Installation tested on multiple platforms
- [ ] Migration tested with v0.3.0 project
- [ ] All examples tested
- [ ] Breaking changes documented

**Release:**
- [ ] Version bumped to 0.4.0
- [ ] Git tag created: v0.4.0
- [ ] Release notes written
- [ ] Known limitations documented

---

## Post-Release Activities

After v0.4.0 ships:

**Immediate:**
- Monitor for bug reports
- Track installation issues
- Gather user feedback
- Document common questions

**Short-term (1-2 weeks):**
- Address critical bugs
- Update documentation based on feedback
- Add FAQ section if needed
- Consider v0.4.1 patch if needed

**Planning:**
- Review deferred features
- Prioritize v0.5.0 based on usage
- Plan next convergence session

---

## Next Version Preview

After v0.4.0 ships and stabilizes, consider for v0.5.0:

**Based on user feedback:**
- PyPI publishing (if demand is high)
- Watch mode (if regeneration frequency is high)
- Template marketplace (if sharing emerges)
- Additional examples (if common patterns identified)
- Performance optimization (if speed is issue)
- CI/CD helpers (if automation requested)

**Don't build until users ask for it!**

---

## Success Definition

v0.4.0 is successful if:

1. ✅ User can install in <2 minutes
2. ✅ First doc generation in <5 minutes
3. ✅ Works on any project
4. ✅ Zero configuration needed
5. ✅ Migration from v0.3.0 is smooth
6. ✅ Documentation answers 90% of questions
7. ✅ Users feel confident using it

**If all 7 are true → Ship with confidence**

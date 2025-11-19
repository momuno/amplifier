# Sprint 4: Context Control

**Duration**: 2 days (Week 2, Days 4-5)
**Goal**: User-specified source file selection for context gathering
**Value Delivered**: Control over what information influences doc generation

---

## Why This Sprint?

Sprints 1-3 have proven generation, safety, and reusability. Now add **precision control**.

**The Problem**: Context is still somewhat hardcoded
- Config file helps but is static
- Can't easily adjust context per regeneration
- No way to experiment with different source combinations
- Can't exclude noisy/irrelevant files

**The Solution**: Explicit source specification
- CLI option to specify sources
- Override config defaults
- Quick iteration on context selection
- Fine-tune generation input

**Value**: Precision control over generation quality

---

## What You'll Have After This Sprint

Enhanced CLI with source control:
```bash
# Use specific sources
amplifier doc-update README.md --sources "src/main.py,docs/architecture.md"

# Exclude certain files
amplifier doc-update API.md --sources "api/**/*.py" --exclude "api/internal/*"

# Use glob patterns
amplifier doc-update README.md --sources "**/*.py"

# Show what sources would be used (dry-run)
amplifier doc-update README.md --show-sources
```

**Complete MVP**: All three core features now implemented

---

## Deliverables

### 1. Enhanced CLI (~100 lines added)
**File**: `cli.py` (extend from Sprint 3)

**What it does**: Accept source specification via command line

**Why this sprint**: User control over context

**New options**:
```python
@click.option("--sources", "-s", help="Comma-separated source files or glob patterns")
@click.option("--exclude", "-e", help="Patterns to exclude from sources")
@click.option("--show-sources", is_flag=True, help="Show which sources would be used")
@click.option("--add-sources", help="Additional sources beyond config defaults")
```

**Implementation**:
```python
@click.command("doc-update")
@click.argument("target_file", type=click.Path())
@click.option("--template", "-t", help="Template to use")
@click.option("--sources", "-s", help="Source files (comma-separated or glob)")
@click.option("--exclude", "-e", help="Exclude patterns")
@click.option("--add-sources", "-a", help="Add to default sources")
@click.option("--show-sources", is_flag=True, help="Preview sources")
def doc_update(target_file, template, sources, exclude, add_sources, show_sources):
    """Regenerate documentation with specified sources"""

    # Determine source list
    source_list = resolve_sources(
        target_file=target_file,
        cli_sources=sources,
        add_sources=add_sources,
        exclude=exclude
    )

    # Preview mode
    if show_sources:
        print_source_preview(source_list)
        return

    # Normal generation flow
    context = gather_context(source_list)
    # ... rest of generation
```

### 2. Source Resolution (~150 lines)
**File**: `source_resolver.py`

**What it does**: Resolves source specifications into file list

**Why this sprint**: Handle various source specification formats

**Implementation notes**:
- Parse comma-separated lists
- Expand glob patterns (`**/*.py`, `src/*.md`)
- Apply exclusion patterns
- Merge with config defaults
- Validate files exist
- Handle relative paths

**Key functions**:
```python
def resolve_sources(
    target_file: str,
    cli_sources: str | None,
    add_sources: str | None,
    exclude: str | None,
    config: Config
) -> list[Path]:
    """Resolve final source list from CLI args and config"""

    # Priority: CLI --sources > --add-sources > config > defaults
    if cli_sources:
        # Complete override
        sources = parse_source_spec(cli_sources)
    elif add_sources:
        # Add to config/defaults
        config_sources = get_config_sources(target_file, config)
        additional = parse_source_spec(add_sources)
        sources = config_sources + additional
    else:
        # Use config or defaults
        sources = get_config_sources(target_file, config)

    # Expand globs
    expanded = expand_glob_patterns(sources)

    # Apply exclusions
    if exclude:
        expanded = apply_exclusions(expanded, exclude)

    # Validate existence
    return validate_sources(expanded)


def parse_source_spec(spec: str) -> list[str]:
    """Parse comma-separated source specification"""
    # Support both "file1,file2" and "file1, file2"
    return [s.strip() for s in spec.split(",")]


def expand_glob_patterns(patterns: list[str]) -> list[Path]:
    """Expand glob patterns to file lists"""
    files = []
    for pattern in patterns:
        if "*" in pattern or "?" in pattern:
            # Glob pattern
            matches = Path(".").glob(pattern)
            files.extend(matches)
        else:
            # Literal path
            files.append(Path(pattern))
    return files


def apply_exclusions(files: list[Path], exclude_pattern: str) -> list[Path]:
    """Filter out files matching exclusion pattern"""
    from fnmatch import fnmatch
    return [
        f for f in files
        if not fnmatch(str(f), exclude_pattern)
    ]
```

### 3. Source Preview (~80 lines)
**File**: `source_preview.py`

**What it does**: Shows what sources would be used without generating

**Why this sprint**: Help users understand context selection

**Implementation notes**:
- List all sources that would be included
- Show file sizes
- Estimate total context size
- Highlight any missing files
- Suggest optimizations

**Example output**:
```
Sources for README.md:
  ✓ README.md (2.3 KB)
  ✓ pyproject.toml (1.1 KB)
  ✓ amplifier/cli.py (4.5 KB)
  ✓ docs/architecture.md (8.2 KB)
  ✗ MISSING: old_docs.md (specified but not found)

Total: 16.1 KB (estimated 4,000 tokens)

Proceed with generation? (y/n)
```

**Implementation**:
```python
def print_source_preview(sources: list[Path]) -> None:
    """Show preview of sources that would be used"""
    print(f"\nSources to include:\n")

    total_size = 0
    missing = []

    for source in sources:
        if source.exists():
            size = source.stat().st_size
            size_kb = size / 1024
            total_size += size
            print(f"  ✓ {source} ({size_kb:.1f} KB)")
        else:
            missing.append(source)
            print(f"  ✗ MISSING: {source}")

    # Summary
    total_kb = total_size / 1024
    estimated_tokens = total_size / 4  # Rough estimate
    print(f"\nTotal: {total_kb:.1f} KB (~{estimated_tokens:,.0f} tokens)")

    if missing:
        print(f"\n⚠ Warning: {len(missing)} file(s) not found")
```

### 4. Smart Source Suggestions (~100 lines)
**File**: `source_suggestions.py`

**What it does**: Suggests relevant sources based on target file

**Why this sprint**: Help users discover useful context

**Implementation notes**:
- Analyze target file to infer needs
- Suggest related files (same directory, similar names)
- Look for common patterns (tests, configs, related docs)
- Rank by likely relevance

**Example**:
```python
def suggest_sources(target_file: str) -> list[str]:
    """Suggest relevant source files for target doc"""
    target_path = Path(target_file)
    suggestions = []

    # Same directory siblings
    siblings = target_path.parent.glob("*.md")
    suggestions.extend(siblings)

    # If in docs/, suggest source code
    if "docs" in target_path.parts:
        suggestions.extend(Path("src").glob("**/*.py"))

    # Always include project metadata
    suggestions.extend([
        Path("README.md"),
        Path("pyproject.toml"),
        Path("package.json"),
    ])

    # Deduplicate and filter existing
    return [
        str(s) for s in set(suggestions)
        if s.exists() and s != target_path
    ]
```

### 5. Context Size Optimization (~100 lines)
**File**: `context_optimizer.py`

**What it does**: Warns and helps when context is too large

**Why this sprint**: LLM context limits are real

**Implementation notes**:
- Estimate token count from file sizes
- Warn if approaching context limits
- Suggest summarization for large files
- Offer to auto-select most relevant portions

**Example**:
```python
def check_context_size(sources: list[Path]) -> ContextSizeCheck:
    """Check if context size is reasonable"""
    total_size = sum(s.stat().st_size for s in sources if s.exists())
    estimated_tokens = total_size / 4  # Rough estimate

    # Claude context window is ~200K tokens
    # Leave room for template, prompt, output
    max_reasonable = 50_000

    if estimated_tokens > max_reasonable:
        return ContextSizeCheck(
            ok=False,
            tokens=estimated_tokens,
            message=f"Context is very large ({estimated_tokens:,.0f} tokens). "
                   f"Consider using fewer/smaller sources or --exclude patterns."
        )

    return ContextSizeCheck(ok=True, tokens=estimated_tokens)
```

### 6. Updated Context Gatherer (~50 lines added)
**File**: `context.py` (enhance from Sprint 3)

**What it does**: Use resolved source list instead of config-only

**Why this sprint**: Support new source resolution

**Changes**:
```python
def gather_context(sources: list[Path]) -> str:
    """Gather context from resolved source list"""
    context_parts = []

    for source in sources:
        if not source.exists():
            logger.warning(f"Source not found: {source}")
            continue

        content = read_source_file(source)

        # Add context size limit per file (e.g., 10KB)
        if len(content) > 10_000:
            content = summarize_large_file(content)

        context_parts.append(f"\n--- {source} ---\n{content}")

    return "\n".join(context_parts)


def summarize_large_file(content: str) -> str:
    """Summarize or truncate large files"""
    # Option 1: Take first/last portions
    # Option 2: Use LLM to summarize
    # Option 3: Extract key sections (functions, classes)

    # For MVP: Simple truncation with notice
    max_chars = 10_000
    if len(content) <= max_chars:
        return content

    half = max_chars // 2
    return (
        content[:half] +
        f"\n\n[... {len(content) - max_chars} characters truncated ...]\n\n" +
        content[-half:]
    )
```

### 7. Tests (~150 lines)
**File**: `test_sprint4.py`

**TDD Approach - Write tests FIRST**:

**Day 4 - Source Resolution**:
- 🔴 Write test: `test_parse_source_spec()`
- 🔴 Write test: `test_expand_glob_patterns()`
- 🔴 Write test: `test_apply_exclusions()`
- 🟢 Implement: Source resolver
- 🔵 Refactor: Path handling
- ✅ Commit

**Day 5 - Integration**:
- 🔴 Write test: `test_cli_with_sources_option()`
- 🔴 Write test: `test_show_sources_preview()`
- 🟢 Implement: CLI integration
- 🟢 Implement: Source preview
- 🔵 Refactor: End-to-end flow
- ✅ Commit

**Test coverage**:
- Source spec parsing
- Glob expansion (with mock filesystem)
- Exclusion patterns
- CLI options (Click testing utilities)
- Context size checking
- Source suggestions

**Manual Testing Checklist**:
- [ ] Specify sources via CLI
- [ ] Glob patterns work (`**/*.py`)
- [ ] Exclusions work (`--exclude "test_*"`)
- [ ] `--show-sources` previews correctly
- [ ] `--add-sources` merges with defaults
- [ ] Large context warnings appear
- [ ] Missing file warnings appear

---

## What Gets Punted (Deliberately Excluded)

### ❌ Automatic relevance detection
- **Why**: User explicitly specifies what's relevant
- **Reconsider**: v2 (ML-based relevance scoring)

### ❌ Context caching between regenerations
- **Why**: Full regeneration is fine for MVP
- **Reconsider**: v2 if performance is issue

### ❌ Intelligent file summarization
- **Why**: Simple truncation works for MVP
- **Reconsider**: v2 (LLM-based summarization)

### ❌ Interactive source selection UI
- **Why**: CLI specification is sufficient
- **Reconsider**: v2 (TUI or web interface)

### ❌ Source dependency analysis
- **Why**: User knows what files matter
- **Reconsider**: v2 (auto-detect imports/references)

### ❌ Historical context (git blame, commit messages)
- **Why**: Current state is enough for MVP
- **Reconsider**: v2 (richer context)

---

## Dependencies

**Requires from previous sprints**:
- Sprint 3: CLI framework
- Sprint 3: Configuration system
- Sprint 1: Context gathering foundation

**Provides for v2**:
- Source resolution patterns
- Context optimization patterns
- User control mechanisms

---

## Acceptance Criteria

### Must Have
- ✅ `--sources` option specifies source files
- ✅ Glob patterns work (`**/*.py`)
- ✅ `--exclude` filters out unwanted files
- ✅ `--show-sources` previews without generating
- ✅ Context size warnings appear when too large
- ✅ Missing file warnings appear
- ✅ CLI sources override config defaults

### Nice to Have (Defer if time constrained)
- ❌ Smart source suggestions
- ❌ Automatic summarization of large files
- ❌ Interactive source selection

---

## Technical Approach

### TDD Red-Green-Refactor Cycle

**Every feature follows this pattern**:

1. **🔴 RED Phase** (~40% of time):
   - Write test that fails
   - Example: `assert "src/main.py" in expand_glob("src/*.py")`

2. **🟢 GREEN Phase** (~40% of time):
   - Write minimal code to pass test
   - Example: Basic glob using Path.glob()

3. **🔵 REFACTOR Phase** (~20% of time):
   - Improve code quality
   - Example: Handle edge cases, improve error messages

4. **✅ COMMIT**:
   - All tests green = commit point

### Glob Pattern Handling

**Use pathlib** (Python standard library):
```python
Path(".").glob("**/*.py")  # Recursive
Path("src").glob("*.py")   # Single directory
```

**Why not third-party libs**: Simple cases, standard library sufficient

### Priority System

**Source priority** (highest to lowest):
1. CLI `--sources` (complete override)
2. CLI `--add-sources` (additive)
3. Config file per-target settings
4. Config file defaults
5. Built-in defaults

**Clear and predictable**: Users know what takes precedence

---

## Implementation Order

### Day 4: Source Resolution (Core Logic)

**Morning** (4 hours):
- 🔴 Write test: Parse source specifications
- 🔴 Write test: Expand glob patterns
- 🟢 Implement: `source_resolver.py`
- 🔵 Refactor: Pattern matching
- ✅ Commit

- 🔴 Write test: Exclusion patterns
- 🟢 Implement: Exclusion logic
- 🔵 Refactor: Filter pipeline
- ✅ Commit

**Afternoon** (4 hours):
- 🔴 Write test: Priority resolution (CLI vs config)
- 🟢 Implement: Priority system
- Test with various combinations
- ✅ Commit (source resolution working)

### Day 5: Integration + Polish (User Features)

**Morning** (4 hours):
- 🔴 Write test: CLI options
- 🟢 Implement: Enhanced CLI with source options
- 🟢 Implement: `--show-sources` preview
- 🔵 Refactor: CLI structure
- ✅ Commit

**Afternoon** (4 hours):
- Implement context size checking
- Implement source suggestions (nice-to-have)
- End-to-end manual testing
- Polish error messages
- Update documentation
- ✅ Final commit

**End of day**: Demo complete MVP with all features

---

## Testing Requirements

### TDD Workflow Per Feature

**Example: Glob Expansion**

1. **🔴 RED - Write Test First**:
```python
def test_expand_glob_single_dir(tmp_path):
    # Create test files
    (tmp_path / "file1.py").touch()
    (tmp_path / "file2.py").touch()
    (tmp_path / "file3.txt").touch()

    result = expand_glob_patterns([f"{tmp_path}/*.py"])

    assert len(result) == 2
    assert all(f.suffix == ".py" for f in result)


def test_expand_glob_recursive(tmp_path):
    # Create nested structure
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "main.py").touch()
    (tmp_path / "src" / "lib").mkdir()
    (tmp_path / "src" / "lib" / "util.py").touch()

    result = expand_glob_patterns([f"{tmp_path}/**/*.py"])

    assert len(result) == 2
```

2. **🟢 GREEN - Minimal Implementation**:
```python
def expand_glob_patterns(patterns: list[str]) -> list[Path]:
    files = []
    for pattern in patterns:
        if "*" in pattern:
            files.extend(Path(".").glob(pattern))
        else:
            files.append(Path(pattern))
    return files
```

3. **🔵 REFACTOR - Improve Quality**:
```python
def expand_glob_patterns(patterns: list[str]) -> list[Path]:
    """Expand glob patterns to file lists"""
    files = []
    for pattern in patterns:
        if has_glob_chars(pattern):
            # Handle relative vs absolute patterns
            base = Path(".")
            matches = base.glob(pattern)
            files.extend(matches)
        else:
            # Literal path
            files.append(Path(pattern))

    return sorted(set(files))  # Deduplicate and sort
```

### Unit Tests (Write First)
- `test_parse_source_spec()` - Comma-separated parsing
- `test_expand_single_dir_glob()` - `*.py`
- `test_expand_recursive_glob()` - `**/*.py`
- `test_apply_exclusions()` - Filter patterns
- `test_source_priority()` - CLI vs config
- `test_context_size_check()` - Size warnings

### Integration Tests (Write First When Possible)
- `test_cli_sources_override()` - CLI overrides config
- `test_cli_add_sources()` - Additive sources
- `test_show_sources_preview()` - Preview mode

### Manual Testing Checklist (After Automated Tests)
- [ ] `amplifier doc-update README.md --sources "src/*.py"`
- [ ] `amplifier doc-update README.md --sources "**/*.md" --exclude "node_modules/*"`
- [ ] `amplifier doc-update README.md --show-sources`
- [ ] `amplifier doc-update README.md --add-sources "docs/extra.md"`
- [ ] Warning appears for very large context
- [ ] Warning appears for missing files
- [ ] Works with config file sources
- [ ] Works without config file

**Test Coverage Target**: >80% for new code

**Commit Strategy**: Commit after each red-green-refactor cycle

---

## What You Learn

After this sprint ships, you discover:

1. **Context Needs**
   - How much context is actually needed?
   - Which files are most valuable?
   - Do users need fine-grained control or are defaults fine?

2. **Usage Patterns**
   - Do users specify sources manually or rely on config?
   - Are glob patterns used frequently?
   - Is exclusion pattern needed often?

3. **Context Size Issues**
   - How often do users hit size limits?
   - Is automatic summarization needed?
   - Should we implement smarter chunking?

4. **MVP Completeness**
   - Is this enough control?
   - What's missing for real-world use?
   - What should v2 prioritize?

**These learnings directly inform**:
- v2: Advanced context features
- v2: Performance optimizations
- v2: Automation opportunities

---

## Known Limitations (By Design)

1. **Manual source specification** - No automatic relevance detection
   - **Why acceptable**: User knows what's relevant
   - **Future**: v2 could add ML-based suggestions

2. **Simple glob patterns** - No advanced pattern matching
   - **Why acceptable**: Standard globs cover most cases
   - **Future**: v2 could add regex patterns

3. **Basic size warnings** - No automatic optimization
   - **Why acceptable**: Users can adjust sources manually
   - **Future**: v2 could add smart summarization

4. **No context caching** - Full re-read every time
   - **Why acceptable**: Generation is already fast enough
   - **Future**: v2 could add caching for large projects

---

## Success Criteria

### Code Quality
- ✅ All tests pass (>80% coverage)
- ✅ TDD cycle followed for all features
- ✅ Clean, maintainable code
- ✅ Proper error handling

### User Experience
- ✅ Source specification is intuitive
- ✅ Glob patterns work as expected
- ✅ Preview mode is helpful
- ✅ Error messages are clear

### Functionality
- ✅ CLI options work correctly
- ✅ Priority system is predictable
- ✅ Context size is manageable
- ✅ Missing files are handled gracefully

### MVP Completion
- ✅ All three core features implemented
- ✅ Tool is usable for real documentation
- ✅ User confident to use on multiple docs
- ✅ Ready for real-world testing

---

## MVP Completion Celebration

This sprint completes the MVP! All three core features are now implemented:

1. ✅ **Template-Based Regeneration** (Sprint 1, 3)
2. ✅ **Context Gathering** (Sprint 1, 3, 4)
3. ✅ **Review & Accept Workflow** (Sprint 2)

**Plus valuable additions**:
- Professional CLI interface
- Multiple templates
- Configuration file support
- Source control

**The tool is now**:
- End-to-end functional
- Safe to use (review workflow)
- Reusable (multiple docs)
- Controllable (source selection)

**Ready for**: Real-world usage and feedback gathering

---

## Post-Sprint: Next Steps

After Sprint 4 completes, the focus shifts to:

1. **Real-World Testing**
   - Use on amplifier documentation
   - Try on 5-10 different doc types
   - Gather user feedback
   - Document learnings

2. **Iteration Based on Feedback**
   - What works well?
   - What's frustrating?
   - What's missing?
   - What should v2 prioritize?

3. **Documentation & Polish**
   - User guide
   - Template creation guide
   - Configuration examples
   - Troubleshooting

4. **v2 Planning**
   - Prioritize features based on real usage
   - Consider automation opportunities
   - Evaluate template marketplace
   - Explore advanced context features

---

## Quick Reference

**Key Files**:
- `source_resolver.py` - Source resolution logic
- `source_preview.py` - Preview functionality
- `context_optimizer.py` - Size checking

**Key Commands**:
```bash
# Specify sources
amplifier doc-update README.md --sources "src/*.py,docs/*.md"

# Exclude patterns
amplifier doc-update README.md --sources "**/*.py" --exclude "test_*"

# Preview sources
amplifier doc-update README.md --show-sources

# Add to defaults
amplifier doc-update README.md --add-sources "extra.md"
```

**Source Patterns**:
- Literal: `src/main.py`
- Single dir: `src/*.py`
- Recursive: `**/*.py`
- Multiple: `src/*.py,docs/*.md`

---

**Remember**: This sprint **completes the MVP**. Focus on getting it working well enough for real use, not perfecting every feature. Real-world usage will guide v2 priorities.

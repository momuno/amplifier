# RED Phase Complete: Chunked Generator Tests

**Status**: ✅ All 16 tests written and FAILING (as expected)

## What These Tests Verify

### 1. DFS Traversal (3 tests)
- `test_dfs_traversal_flat_sections` - Sequential order for flat sections
- `test_dfs_traversal_nested_sections` - Depth-first order for nested sections
- `test_dfs_traversal_empty_sections` - Handle empty section list

**Validates**: Core DFS algorithm for section ordering

### 2. Section Generation (3 tests)
- `test_generate_section_with_sources` - Single section with sources
- `test_generate_section_with_context` - Section with prior context
- `test_generate_section_uses_prompt` - Uses section's explicit prompt

**Validates**: LLM generation per section with sources + context

### 3. Complete Document Generation (4 tests)
- `test_generate_validates_sources_first` - Fail early validation
- `test_generate_produces_complete_document` - Assembled markdown output
- `test_generate_sections_in_dfs_order` - Correct generation order
- `test_generate_passes_context_between_sections` - Context flows correctly

**Validates**: End-to-end generation workflow

### 4. Integration (3 tests)
- `test_integration_with_source_validator` - Uses SourceValidator
- `test_integration_with_context_manager` - Uses ContextManager
- `test_end_to_end_generation` - Complete workflow (CRITICAL TEST)

**Validates**: Integration with existing components

### 5. Error Handling (2 tests)
- `test_generate_fails_with_invalid_sources` - Fails early with bad sources
- `test_generate_section_with_empty_prompt` - Handles missing prompts

**Validates**: Robust error handling

### 6. Progress Reporting (1 test)
- `test_generate_reports_progress` - Shows progress during generation

**Validates**: User visibility during generation

## Why Tests Fail (Expected)

All tests fail with `ModuleNotFoundError: No module named 'doc_evergreen.chunked_generator'`

This is **CORRECT** - we haven't implemented the module yet!

## What Needs to Be Implemented (GREEN Phase)

### 1. Create `doc_evergreen/chunked_generator.py`

```python
class ChunkedGenerator:
    def __init__(self, template: Template, base_dir: Path):
        """Initialize generator."""

    async def generate(self) -> str:
        """Generate complete document section-by-section."""

    async def generate_section(
        self,
        section: Section,
        sources: list[Path],
        context: str
    ) -> str:
        """Generate single section."""

def traverse_dfs(sections: list[Section]) -> Iterator[Section]:
    """DFS traversal yielding sections in generation order."""
```

### 2. Core Implementation Requirements

**Must implement**:
- DFS traversal algorithm
- Source validation integration (call `validate_all_sources()`)
- ContextManager integration (track sections, provide context)
- Async LLM generation per section
- Document assembly (join sections into markdown)
- Progress reporting (print which section generating)

**Must integrate with**:
- `SourceValidator` from `doc_evergreen/core/source_validator.py`
- `ContextManager` from `doc_evergreen/context_manager.py`
- `Template`, `Section` from `doc_evergreen/core/template_schema.py`

### 3. Generation Flow (from sprint plan)

```python
async def generate(self) -> str:
    # 1. Validate sources (fail early)
    validation = validate_all_sources(self.template, self.base_dir)
    if not validation.valid:
        raise SourceValidationError(validation.errors)

    # 2. Generate sections in DFS order
    output = []
    for i, section in enumerate(traverse_dfs(self.template.document.sections)):
        # Get sources for this section
        sources = validation.section_sources[section.heading]

        # Get context from previous sections
        context = self.context_manager.get_context_for_section(i)

        # Generate section
        print(f"Generating: {section.heading} (sources: {len(sources)})")
        content = await self.generate_section(section, sources, context)

        # Track in context manager
        self.context_manager.add_section(section.heading, content)

        # Add to output
        output.append(f"# {section.heading}\n\n{content}")

    # 3. Assemble complete document
    return "\n\n".join(output)
```

### 4. DFS Algorithm

```python
def traverse_dfs(sections: list[Section]) -> Iterator[Section]:
    """Depth-first traversal of section tree."""
    for section in sections:
        yield section
        if section.sections:
            yield from traverse_dfs(section.sections)
```

## Next Steps (GREEN Phase)

1. Create `doc_evergreen/chunked_generator.py`
2. Implement `traverse_dfs()` function
3. Implement `ChunkedGenerator` class
4. Implement `generate()` method with source validation
5. Implement `generate_section()` method with LLM calls
6. Add progress reporting
7. Run tests → watch them PASS

## Success Criteria

All 16 tests pass, validating:
- ✅ DFS traversal works correctly
- ✅ Sections generated with sources + context
- ✅ Context flows between sections
- ✅ Complete documents assembled
- ✅ Integration with SourceValidator and ContextManager works
- ✅ Progress reporting shows status

## Why This Matters (Sprint 5 Core Hypothesis)

**Question**: Does section-by-section generation with explicit prompts improve control and predictability over single-shot?

**These tests validate**:
- Section-level control (explicit prompts per section)
- Context flow (each section sees previous work)
- Source targeting (specific sources per section)
- Predictable order (DFS traversal)

**If tests pass** → Hypothesis validated, chunked generation works
**If tests fail** → Need to reconsider approach

This is the **most critical deliverable** of Sprint 5.

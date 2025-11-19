# Sprint 5 Deliverable 1: Extended Template Schema - Test Summary

## RED Phase Complete ✓

**Status**: Tests written and verified to FAIL (as expected in TDD)

---

## Test File Location

**File**: `doc_evergreen/tests/test_sprint5_template_schema.py`

**Size**: 530 lines of comprehensive test coverage

---

## What the Tests Verify

### 1. Basic Section Schema with Prompts (TestSectionSchema)

**Tests**: 4 tests covering Section dataclass

- ✅ `test_section_with_prompt_parses()` - Section accepts prompt field
- ✅ `test_section_without_prompt_defaults_none()` - Prompt is optional (defaults to None)
- ✅ `test_section_with_empty_sources_list()` - Sections work with empty sources
- ✅ `test_section_minimal_only_heading()` - Minimal section (heading only) has proper defaults

**Expected Schema**:
```python
@dataclass
class Section:
    heading: str
    prompt: Optional[str] = None
    sources: list[str] = field(default_factory=list)
    sections: list['Section'] = field(default_factory=list)
```

---

### 2. Nested Sections Support (TestNestedSections)

**Tests**: 4 tests covering nested section trees

- ✅ `test_nested_sections_with_prompts()` - Two-level nesting with prompts
- ✅ `test_deeply_nested_sections_three_levels()` - Three-level deep nesting
- ✅ `test_mixed_nested_sections_some_with_prompts_some_without()` - Mixed prompt presence

**Key Validation**: Recursive Section structure preserves prompts at all nesting levels

---

### 3. Mode-Based Validation (TestTemplateSchemaValidation)

**Tests**: 6 tests covering chunked vs single-shot validation

**Single-shot mode (backward compatible)**:
- ✅ `test_single_shot_mode_prompts_optional()` - Prompts NOT required
- ✅ `test_mode_defaults_to_single_if_not_specified()` - Default is single-shot

**Chunked mode (new requirement)**:
- ✅ `test_chunked_mode_requires_prompts()` - Fails if ANY section lacks prompt
- ✅ `test_chunked_mode_all_sections_need_prompts()` - Reports ALL missing prompts
- ✅ `test_chunked_mode_nested_sections_need_prompts()` - Validates nested sections
- ✅ `test_chunked_mode_all_prompts_present_passes()` - Passes when all prompts present

**Expected Validation Result Schema**:
```python
@dataclass
class ValidationResult:
    valid: bool
    errors: list[str]
```

---

### 4. Complete Template Structure (TestTemplateStructure)

**Tests**: 4 tests covering full template parsing

- ✅ `test_parse_complete_template()` - Parses JSON into Template/Document/Section hierarchy
- ✅ `test_parse_template_invalid_json_raises_error()` - Clear error for bad JSON
- ✅ `test_parse_template_missing_document_raises_error()` - Validates 'document' key
- ✅ `test_parse_template_missing_required_fields_raises_error()` - Validates required fields

**Expected Schema**:
```python
@dataclass
class Document:
    title: str
    output: str
    sections: list[Section]

@dataclass
class Template:
    document: Document
```

---

### 5. Backward Compatibility (TestBackwardCompatibility)

**Tests**: 2 tests ensuring v0.1.0 templates still work

- ✅ `test_existing_templates_without_prompts_still_work()` - v0.1.0 templates parse correctly
- ✅ `test_mode_defaults_to_single_if_not_specified()` - Safe defaults maintain compatibility

**Critical**: Existing templates from v0.1.0 (without prompts) continue to work unchanged

---

## Why These Tests FAIL Currently

```
ModuleNotFoundError: No module named 'doc_evergreen.core'
```

**This is EXPECTED and CORRECT** in the RED phase of TDD.

The tests import from `doc_evergreen.core.template_schema`, which doesn't exist yet:
- `Section` - Not implemented
- `Document` - Not implemented
- `Template` - Not implemented
- `parse_template()` - Not implemented
- `validate_template()` - Not implemented

---

## What Implementation Needs to Happen (GREEN Phase)

### Step 1: Create Module Structure

```bash
mkdir -p doc_evergreen/core
touch doc_evergreen/core/__init__.py
touch doc_evergreen/core/template_schema.py
```

### Step 2: Implement Dataclasses

**File**: `doc_evergreen/core/template_schema.py`

```python
from dataclasses import dataclass, field
from typing import Optional
from pathlib import Path
import json

@dataclass
class Section:
    heading: str
    prompt: Optional[str] = None
    sources: list[str] = field(default_factory=list)
    sections: list['Section'] = field(default_factory=list)

@dataclass
class Document:
    title: str
    output: str
    sections: list[Section]

@dataclass
class Template:
    document: Document

@dataclass
class ValidationResult:
    valid: bool
    errors: list[str] = field(default_factory=list)
```

### Step 3: Implement parse_template()

Parse JSON file into Template object:
1. Read JSON file
2. Validate JSON syntax
3. Validate 'document' key exists
4. Validate required fields (title, output)
5. Recursively parse sections
6. Return Template object

### Step 4: Implement validate_template()

Validate template for specific mode:
1. Default mode = "single" (backward compatible)
2. Single-shot: Always valid (prompts optional)
3. Chunked: Traverse all sections, check prompts present
4. Return ValidationResult with errors list

---

## Test Coverage Summary

| Test Class | Tests | Focus Area |
|------------|-------|------------|
| TestSectionSchema | 4 | Basic Section dataclass |
| TestNestedSections | 4 | Recursive section trees |
| TestTemplateSchemaValidation | 6 | Mode-based validation |
| TestTemplateStructure | 4 | Full template parsing |
| TestBackwardCompatibility | 2 | v0.1.0 compatibility |
| **TOTAL** | **20** | **Comprehensive coverage** |

---

## Edge Cases Covered

✅ Sections with no sources
✅ Sections with no prompts (backward compatible)
✅ Deep nesting (3+ levels)
✅ Mixed prompt presence in siblings
✅ Invalid JSON syntax
✅ Missing required fields
✅ Empty template files
✅ Legacy v0.1.0 templates

---

## Test Execution

**Run all Sprint 5 tests**:
```bash
cd doc_evergreen
uv run pytest tests/test_sprint5_template_schema.py -v
```

**Run specific test class**:
```bash
uv run pytest tests/test_sprint5_template_schema.py::TestSectionSchema -v
```

**Run single test**:
```bash
uv run pytest tests/test_sprint5_template_schema.py::TestSectionSchema::test_section_with_prompt_parses -v
```

---

## Success Criteria

**RED phase complete** ✓ when:
- [x] All tests written
- [x] Tests follow AAA pattern (Arrange-Act-Assert)
- [x] Tests fail with import errors (proving they test real behavior)
- [x] Clear test names describing behavior

**GREEN phase complete** when:
- [ ] All 20 tests pass
- [ ] Implementation is minimal (just enough to pass tests)
- [ ] No extra features not covered by tests

**REFACTOR phase complete** when:
- [ ] Code is clean and maintainable
- [ ] Proper error messages
- [ ] Type hints throughout
- [ ] All tests still pass

---

## Next Steps

1. **Create module structure**: `doc_evergreen/core/`
2. **Implement dataclasses**: Section, Document, Template, ValidationResult
3. **Implement parse_template()**: JSON → Template object
4. **Implement validate_template()**: Mode-based validation
5. **Run tests**: Verify GREEN phase (all tests pass)
6. **Refactor**: Clean up code while maintaining passing tests

---

## Notes for Implementation

### Recursive Section Parsing

Sections contain nested sections, so parsing must be recursive:

```python
def _parse_section(data: dict) -> Section:
    nested_sections = [
        _parse_section(s) for s in data.get('sections', [])
    ]
    return Section(
        heading=data['heading'],
        prompt=data.get('prompt'),
        sources=data.get('sources', []),
        sections=nested_sections
    )
```

### Validation Traversal

Validation must traverse the entire section tree:

```python
def _validate_sections_for_chunked(sections: list[Section], errors: list[str]) -> None:
    for section in sections:
        if section.prompt is None:
            errors.append(f"Section '{section.heading}' missing prompt (required for chunked mode)")
        if section.sections:
            _validate_sections_for_chunked(section.sections, errors)
```

### Error Messages

Tests expect specific error message patterns:
- Must mention "prompt" for prompt validation failures
- Must mention section heading (e.g., "Overview", "Features")
- Must mention "json" for JSON parsing errors
- Must mention "document" for missing document key

---

**RED Phase Status**: ✅ COMPLETE

**Next**: Implement template_schema.py (GREEN phase)

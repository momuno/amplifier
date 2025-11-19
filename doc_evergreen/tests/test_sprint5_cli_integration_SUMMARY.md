# Sprint 5 Deliverable 5: CLI Integration Tests - RED Phase Summary

## Test File Created
`doc_evergreen/tests/test_sprint5_cli_integration.py`

## Test Results: ✅ RED Phase Complete
**15 tests failing, 3 tests passing** (expected in RED phase)

---

## What the Tests Verify

### 1. CLI Parsing Tests (`TestCLIModeFlag`)
**Tests that MUST fail until `--mode` flag is added:**

- `test_cli_has_mode_option()` - Verifies `--mode` appears in help text ❌
- `test_cli_mode_accepts_single_value()` - Accepts `--mode single` ✅ (graceful handling)
- `test_cli_mode_accepts_chunked_value()` - Accepts `--mode chunked` ✅ (graceful handling)
- `test_cli_mode_rejects_invalid_value()` - Rejects invalid mode values ❌
- `test_cli_mode_defaults_to_single()` - Defaults to single-shot mode ❌

### 2. Generator Routing Tests (`TestGeneratorRouting`)
**Tests that verify correct generator is instantiated:**

- `test_single_mode_uses_single_generator()` - Routes to `Generator` ❌
- `test_chunked_mode_uses_chunked_generator()` - Routes to `ChunkedGenerator` ❌
- `test_mode_determines_generator_choice()` - Different modes = different generators ❌

**Failure reason:** CLI doesn't import or use these generators yet

### 3. Validation Tests (`TestChunkedModeValidation`)
**Tests that verify prompt validation in chunked mode:**

- `test_chunked_mode_validates_prompts_exist()` - Checks prompts exist ❌
- `test_chunked_mode_fails_without_prompts()` - Errors if prompts missing ❌
- `test_chunked_mode_succeeds_with_all_prompts()` - Passes with valid template ❌
- `test_chunked_mode_validates_nested_sections()` - Validates nested section prompts ❌

**Failure reason:** No validation logic in CLI yet

### 4. Backward Compatibility Tests (`TestBackwardCompatibility`)
**Tests that verify existing templates still work:**

- `test_existing_templates_work_without_mode()` - Old templates use single-shot ❌
- `test_mode_flag_optional()` - Can omit `--mode` flag ❌
- `test_single_mode_ignores_prompts()` - Single mode works with prompts ❌
- `test_help_mentions_default_mode()` - Help shows default ✅

**Failure reason:** No mode handling logic exists yet

### 5. Output Override Tests (`TestCLIOutputPath`)
**Tests for optional `--output` flag:**

- `test_output_flag_overrides_template_path()` - Override output path ❌
- `test_output_flag_works_with_single_mode()` - Works in single mode too ❌

**Failure reason:** No `--output` flag implemented yet

---

## Why Tests Fail (Expected)

### Primary Failures

1. **`--mode` flag doesn't exist** (AttributeError in help text)
   - CLI has no `--mode` option defined
   - Need to add `@click.option('--mode', ...)`

2. **No generator imports** (AttributeError when mocking)
   - CLI doesn't import `Generator` or `ChunkedGenerator`
   - Tests try to mock non-existent imports

3. **No routing logic** (tests expect conditional behavior)
   - CLI doesn't choose generator based on mode
   - No validation of prompts in chunked mode

4. **No `--output` flag** (missing option)
   - CLI doesn't support output path override
   - Need to add `@click.option('--output', ...)`

### What's Working

Tests that passed gracefully handle the missing flag:
- Templates can be parsed (JSON loading works)
- File system operations work
- Help text is generated (just missing new options)

---

## Implementation Requirements (GREEN Phase)

To make these tests pass, the CLI needs:

### 1. Add `--mode` Option
```python
@click.option(
    '--mode',
    type=click.Choice(['single', 'chunked']),
    default='single',
    help='Generation mode: single-shot or chunked section-by-section'
)
```

### 2. Add `--output` Option
```python
@click.option(
    '--output',
    type=click.Path(),
    help='Override output path from template'
)
```

### 3. Import Required Components
```python
from doc_evergreen.chunked_generator import ChunkedGenerator
from doc_evergreen.core.template_schema import parse_template, validate_template
# Keep existing imports...
```

### 4. Add Template Parsing Logic
```python
def doc_update(target_file, template, mode, output, ...):
    # Parse JSON template (new path)
    if target_file.endswith('.json'):
        template_obj = parse_template(Path(target_file))

        # Validate based on mode
        validation = validate_template(template_obj, mode=mode)
        if not validation.valid:
            click.echo(f"Template validation failed:", err=True)
            for error in validation.errors:
                click.echo(f"  - {error}", err=True)
            raise SystemExit(1)

        # Determine output path
        output_path = output or template_obj.document.output

        # Route to generator
        if mode == 'chunked':
            generator = ChunkedGenerator(template_obj, base_dir=Path.cwd())
        else:
            generator = Generator(template_obj, ...)  # Need to implement

        # Generate
        result = await generator.generate()

        # Review workflow...
    else:
        # Existing template manager path (backward compatible)
        ...
```

### 5. Handle Both Template Types
- **New:** JSON templates with `parse_template()` → use generators
- **Old:** Markdown templates via `template_manager` → existing flow

### 6. Async Execution
CLI needs to handle async generators:
```python
import asyncio

def doc_update(...):
    if mode in ['single', 'chunked']:
        result = asyncio.run(generator.generate())
    else:
        # Old sync path
        ...
```

---

## Test Coverage Map

| Feature | Tests | Status |
|---------|-------|--------|
| `--mode` flag parsing | 5 tests | 2/5 ❌ |
| Generator routing | 3 tests | 0/3 ❌ |
| Validation in chunked mode | 4 tests | 0/4 ❌ |
| Backward compatibility | 4 tests | 1/4 ❌ |
| Output override | 2 tests | 0/2 ❌ |
| **TOTAL** | **18 tests** | **3/18** |

---

## Next Steps (GREEN Phase)

1. **Add CLI options** (`--mode`, `--output`)
2. **Import generators** (ChunkedGenerator, template_schema)
3. **Add template parsing** (JSON templates)
4. **Add validation** (check prompts in chunked mode)
5. **Add routing logic** (mode → generator)
6. **Handle async** (asyncio.run for generators)
7. **Preserve backward compatibility** (old template path still works)

Once implemented, all 18 tests should pass.

---

## Design Notes

### Backward Compatibility Strategy
- Default mode is `single` (no breaking changes)
- Old markdown templates still work through existing path
- New JSON templates use new generator path
- Two parallel paths converge at review workflow

### User Experience
```bash
# Existing users - no changes needed
doc-update README.md

# New chunked workflow
doc-update --mode chunked template.json

# With output override
doc-update --mode chunked template.json --output custom-output.md
```

### Error Handling
Chunked mode fails fast with clear errors:
- Missing prompts → shows which sections need prompts
- Invalid mode → shows valid choices
- Parsing errors → helpful JSON error messages

---

## RED Phase Success Criteria ✅

- [x] Tests written FIRST
- [x] Tests use AAA pattern (Arrange-Act-Assert)
- [x] Tests FAIL when run (15/18 failing as expected)
- [x] Tests verify behavior, not implementation
- [x] Tests cover all requirements from sprint plan
- [x] Tests include backward compatibility
- [x] Tests use mocks for external dependencies
- [x] Tests are isolated and independent

**Ready for GREEN phase implementation!**

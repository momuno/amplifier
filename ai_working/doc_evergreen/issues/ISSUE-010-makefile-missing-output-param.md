# ISSUE-010: Makefile `regen-doc` Missing OUTPUT Parameter

**Status:** Open
**Priority:** Medium
**Type:** Bug (Missing Feature)
**Created:** 2025-11-20
**Updated:** 2025-11-20

## Description

The Makefile `regen-doc` target does not expose the `--output` CLI option, even though the underlying `regen-doc` command supports it. This creates a mismatch between what the CLI can do and what the Makefile wrapper exposes.

Additionally, the error message shown when TEMPLATE is missing only mentions TEMPLATE and AUTO parameters, giving users no indication that OUTPUT customization is possible.

## Reproduction Steps

1. Run `make regen-doc` without parameters
2. Observe error message:
   ```
   Error: TEMPLATE parameter required
   Usage: make regen-doc TEMPLATE=examples/simple.json
          make regen-doc TEMPLATE=templates/amplifier_readme.json AUTO=true
   ```
3. Note that there's no mention of OUTPUT parameter
4. Try: `make regen-doc TEMPLATE=templates/amplifier_readme.json OUTPUT=custom/path.md`
5. OUTPUT parameter is ignored (not passed to CLI)

## Expected Behavior

Users should be able to:
- Specify custom output path via `OUTPUT` parameter
- See OUTPUT in usage/help text
- Have OUTPUT properly passed to underlying CLI command

**Example usage:**
```bash
make regen-doc TEMPLATE=templates/readme.json OUTPUT=docs/custom.md
```

## Actual Behavior

- No OUTPUT parameter support in Makefile
- Usage message doesn't mention OUTPUT option
- Users must call CLI directly to use --output flag:
  ```bash
  PYTHONPATH=.. uv run python -m cli regen-doc --output custom/path.md template.json
  ```

## Root Cause

**Location:** `doc_evergreen/Makefile` lines 30-41

**Current implementation:**
```makefile
regen-doc: ## Regenerate documentation from template (TEMPLATE=path/to/template.json [AUTO=true])
	@if [ -z "$(TEMPLATE)" ]; then \
		echo "Error: TEMPLATE parameter required"; \
		echo "Usage: make regen-doc TEMPLATE=examples/simple.json"; \
		echo "       make regen-doc TEMPLATE=templates/amplifier_readme.json AUTO=true"; \
		exit 1; \
	fi
	@if [ "$(AUTO)" = "true" ]; then \
		PYTHONPATH=.. uv run python -m cli regen-doc --auto-approve $(TEMPLATE); \
	else \
		PYTHONPATH=.. uv run python -m cli regen-doc $(TEMPLATE); \
	fi
```

**Problems:**
1. No OUTPUT parameter variable checked or passed
2. Help text description doesn't mention OUTPUT
3. Error message doesn't mention OUTPUT option
4. CLI invocation doesn't include `--output $(OUTPUT)` flag

**CLI supports:** (from `doc_evergreen/cli.py` line 118)
```python
@click.option("--output", type=click.Path(), help="Override output path from template")
```

## Impact Analysis

**Severity:** Medium - workaround exists (call CLI directly)

**User Impact:**
- Reduced discoverability - users don't know OUTPUT is available
- Inconsistent interface - Makefile doesn't match CLI capabilities
- Extra friction - must learn CLI invocation instead of using Makefile
- Poor DX - confusing to have partial parameter coverage

**Workaround:**
Users can call CLI directly:
```bash
cd doc_evergreen
PYTHONPATH=.. uv run python -m cli regen-doc --output custom/path.md templates/readme.json
```

## Acceptance Criteria

To consider this issue resolved:

- [ ] Makefile `regen-doc` target accepts OUTPUT parameter
- [ ] OUTPUT is properly passed to CLI as `--output` flag
- [ ] Help text comment includes OUTPUT in parameter list
- [ ] Error message shows OUTPUT in usage examples
- [ ] Empty OUTPUT (not specified) doesn't break existing behavior
- [ ] When OUTPUT specified, it overrides template's output path
- [ ] Can combine OUTPUT with AUTO flag

## Proposed Solution

**Update Makefile lines 30-41:**

```makefile
regen-doc: ## Regenerate documentation from template (TEMPLATE=path [AUTO=true] [OUTPUT=path])
	@if [ -z "$(TEMPLATE)" ]; then \
		echo "Error: TEMPLATE parameter required"; \
		echo "Usage: make regen-doc TEMPLATE=examples/simple.json"; \
		echo "       make regen-doc TEMPLATE=templates/amplifier_readme.json AUTO=true"; \
		echo "       make regen-doc TEMPLATE=templates/readme.json OUTPUT=custom/path.md"; \
		exit 1; \
	fi
	@CMD="PYTHONPATH=.. uv run python -m cli regen-doc"; \
	if [ "$(AUTO)" = "true" ]; then \
		CMD="$$CMD --auto-approve"; \
	fi; \
	if [ -n "$(OUTPUT)" ]; then \
		CMD="$$CMD --output $(OUTPUT)"; \
	fi; \
	$$CMD $(TEMPLATE)
```

**Key changes:**
1. Help text mentions OUTPUT parameter
2. Error message includes OUTPUT example
3. Build CLI command with conditional flags
4. Add `--output $(OUTPUT)` only if OUTPUT is set

**Alternative approach (simpler but more verbose):**
```makefile
regen-doc: ## Regenerate documentation from template (TEMPLATE=path [AUTO=true] [OUTPUT=path])
	@if [ -z "$(TEMPLATE)" ]; then \
		echo "Error: TEMPLATE parameter required"; \
		echo "Usage: make regen-doc TEMPLATE=examples/simple.json"; \
		echo "       make regen-doc TEMPLATE=templates/readme.json OUTPUT=custom.md"; \
		echo "       make regen-doc TEMPLATE=templates/readme.json AUTO=true"; \
		exit 1; \
	fi
	@if [ "$(AUTO)" = "true" ] && [ -n "$(OUTPUT)" ]; then \
		PYTHONPATH=.. uv run python -m cli regen-doc --auto-approve --output $(OUTPUT) $(TEMPLATE); \
	elif [ "$(AUTO)" = "true" ]; then \
		PYTHONPATH=.. uv run python -m cli regen-doc --auto-approve $(TEMPLATE); \
	elif [ -n "$(OUTPUT)" ]; then \
		PYTHONPATH=.. uv run python -m cli regen-doc --output $(OUTPUT) $(TEMPLATE); \
	else \
		PYTHONPATH=.. uv run python -m cli regen-doc $(TEMPLATE); \
	fi
```

## Testing Notes

**Manual verification:**

1. Test without parameters (should show updated error):
   ```bash
   make regen-doc
   # Should mention OUTPUT in usage
   ```

2. Test with OUTPUT only:
   ```bash
   make regen-doc TEMPLATE=examples/simple.json OUTPUT=test-output.md
   # Should generate to test-output.md
   ```

3. Test with AUTO only (existing):
   ```bash
   make regen-doc TEMPLATE=examples/simple.json AUTO=true
   # Should auto-approve (existing behavior)
   ```

4. Test with both OUTPUT and AUTO:
   ```bash
   make regen-doc TEMPLATE=examples/simple.json AUTO=true OUTPUT=test.md
   # Should auto-approve AND write to test.md
   ```

5. Test without OUTPUT (default behavior):
   ```bash
   make regen-doc TEMPLATE=examples/simple.json
   # Should use template's output path (existing behavior)
   ```

**Expected CLI invocations:**

| Makefile Command | Expected CLI Call |
|------------------|-------------------|
| `TEMPLATE=x.json` | `regen-doc x.json` |
| `TEMPLATE=x.json AUTO=true` | `regen-doc --auto-approve x.json` |
| `TEMPLATE=x.json OUTPUT=y.md` | `regen-doc --output y.md x.json` |
| `TEMPLATE=x.json AUTO=true OUTPUT=y.md` | `regen-doc --auto-approve --output y.md x.json` |

## Implementation Complexity

**Low** - 10-15 lines of Makefile changes

**Affected files:**
- `doc_evergreen/Makefile` (lines 30-41)

**No code changes needed:**
- CLI already supports --output flag
- No tests to update (Makefile not tested)

## Sprint Assignment

**Recommended:** Next polish/UX sprint

**Rationale:**
- Low complexity (quick win)
- Improves user experience
- Completes Makefile wrapper feature parity with CLI
- No blocker - workaround exists

## Related Issues

- ISSUE-004: CLI help text unclear - Resolved (Sprint 8)
- ISSUE-006: Unclear sources specification - Resolved (Sprint 9)

**Pattern:** Several issues about incomplete parameter exposure/documentation. This continues that theme.

## Comments / Updates

### 2025-11-20 - Issue Created
Initial capture from user feedback. User tried to use OUTPUT parameter and discovered it wasn't supported by Makefile wrapper, only by direct CLI invocation.

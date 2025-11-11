# AI Assistant Workflow Guide for doc-evergreen

**For AI assistants helping users generate and maintain documentation**

This guide explains how to help users use doc-evergreen effectively through conversational interaction.

## Tool Overview

doc-evergreen is a CLI tool that generates documentation from source code using LLM intelligence. It has two main commands:

1. **create** - Generate new documentation
2. **regenerate** - Update existing documentation from saved configuration

## When to Use This Tool

Suggest doc-evergreen when users:

- Want to create or update project documentation (README, API docs, guides)
- Need to maintain documentation as code changes
- Want AI-generated docs that match their project style
- Have multiple documents to keep synchronized with code

## Workflow: Helping Users Create Documentation

### Step 1: Understand the Goal

**Ask clarifying questions:**

```
"What type of documentation do you want to create?"
- Project README
- API reference
- User guide
- Developer guide
- Contributing guide
- Other

"What should this documentation cover?"
(Get 1-2 sentence description from user)
```

**Examples of good `--about` descriptions:**
- "Main project README covering installation, usage, and features"
- "API reference documenting all REST endpoints and authentication"
- "Developer guide for setting up local environment and contributing"
- "User guide showing how to use the CLI commands"

### Step 2: Determine Source Files

**Offer two options:**

**Option A: Auto-discovery (Recommended for first-time users)**
```
"I can auto-discover the relevant source files based on your description.
This usually works well for common documentation types."
```

**Option B: Explicit patterns (For specific needs)**
```
"What files should I include? You can specify glob patterns like:
- 'src/**/*.py' - All Python files in src/
- '*.md' - All markdown files in root
- 'api/**/*.ts' - All TypeScript files in api/

You can specify multiple patterns."
```

**Auto-discovery keywords to mention:**
- "readme" → Will include README.md, main source files, pyproject.toml
- "api" → Will include src/**/*.py, api/**/*.py
- "cli" → Will include src/cli/**/*.py, src/commands/**/*.py
- "guide" → Will include docs/**/*.md, examples files

### Step 3: Determine Output Path

**Ask:**
```
"Where should I save the generated documentation?

Common patterns:
- README.md (project root)
- docs/API.md (in docs folder)
- CONTRIBUTING.md (project root)
- docs/guides/USER_GUIDE.md (nested)"
```

**Validation:**
- Path must include filename with extension
- Common extensions: .md, .txt, .rst
- Warn if unusual extension

### Step 4: Template Selection (Optional)

**Most users don't need to specify - auto-selection works well.**

If user asks about templates:
```
"doc-evergreen will automatically choose the best template.

Available templates:
- readme - Project overview (auto-selected for 'readme', 'overview')
- api-reference - API documentation (auto-selected for 'api', 'endpoints')
- user-guide - Tutorial-style (auto-selected for 'user', 'guide', 'tutorial')
- developer-guide - Technical reference (auto-selected for 'developer', 'contributing')

Do you want to explicitly specify a template?"
```

### Step 5: Preview or Generate

**Always offer dry-run first:**

```
"Would you like to:
1. Preview what would be generated (dry-run) - Recommended first time
2. Generate immediately"
```

**For dry-run:**
```bash
uv run python -m doc_evergreen.cli create \
    --about "Main project README" \
    --output README.md \
    --sources "src/**/*.py" "pyproject.toml" \
    --dry-run
```

**For actual generation:**
```bash
uv run python -m doc_evergreen.cli create \
    --about "Main project README" \
    --output README.md \
    --sources "src/**/*.py" "pyproject.toml"
```

### Step 6: Handle Results

**On success:**
```
"Documentation generated successfully!

Generated: [output_path]
Backup saved: .doc-evergreen/versions/[backup_file]
Configuration saved: .doc-evergreen/history.yaml

You can regenerate this document anytime with:
  doc-evergreen regenerate [output_path]"
```

**On error:**
- Check error message and guide user to fix
- Common issues: missing API key, no source files, invalid UTF-8

## Workflow: Helping Users Regenerate Documentation

### Step 1: Check What's Configured

**Show available documents:**
```bash
# Look at history.yaml
cat .doc-evergreen/history.yaml
```

```
"You have these documents configured:
- README.md
- docs/API.md
- CONTRIBUTING.md

Which would you like to regenerate?
Or say 'all' to regenerate everything."
```

### Step 2: Regenerate Single or All

**For single document:**
```bash
uv run python -m doc_evergreen.cli regenerate README.md
```

**For all documents:**
```bash
uv run python -m doc_evergreen.cli regenerate --all
```

**Always offer dry-run:**
```
"Would you like to preview first? (--dry-run)"
```

### Step 3: Explain What Will Happen

```
"Regeneration will:
1. Load configuration from .doc-evergreen/history.yaml
2. Gather source files using saved patterns
3. Use your customized template (or built-in if not found)
4. Generate updated documentation with LLM
5. Backup current version to .doc-evergreen/versions/
6. Save new version and update history

This takes 30-60 seconds per document."
```

## API Key Setup Workflow

**If user gets "No API key found" error:**

```
"doc-evergreen needs an Anthropic API key to generate documentation.

You have two options:

Option 1: File (Recommended)
  echo "your-api-key-here" > .claude/api_key.txt

Option 2: Environment Variable
  export ANTHROPIC_API_KEY="your-api-key-here"

Do you have an Anthropic API key? If not, get one at:
  https://console.anthropic.com/

The file approach is better because it persists across sessions
and the tool can find it automatically."
```

**After setup:**
```bash
# Test if key is found
uv run python -m doc_evergreen.cli create \
    --about "test" \
    --output test.md \
    --dry-run
```

## Example Conversations

### Example 1: First-Time User Creating README

**User:** "I want to create a README for my project"

**Assistant:**
```
"I'll help you create a README using doc-evergreen.

What should the README cover? Give me 1-2 sentences about your project."
```

**User:** "It's a Python CLI tool for analyzing code complexity"

**Assistant:**
```
"Great! I'll use auto-discovery to find relevant files (Python source, pyproject.toml, etc).

Let me preview what would be generated first:
```

```bash
uv run python -m doc_evergreen.cli create \
    --about "Python CLI tool for analyzing code complexity" \
    --output README.md \
    --dry-run
```

```
"This shows what files would be included. Look good?

If yes, I'll run without --dry-run to actually generate it.
This takes about 30-60 seconds."
```

### Example 2: Regenerating After Code Changes

**User:** "I updated my API, need to regenerate the API docs"

**Assistant:**
```
"I'll regenerate your API documentation from the saved configuration.

Let me check what's configured..."
```

```bash
cat .doc-evergreen/history.yaml | grep -A 5 "API.md"
```

```
"Found docs/API.md configured with these sources:
- src/api/**/*.py
- src/models/**/*.py

I'll regenerate it now. Your current version will be backed up to:
  .doc-evergreen/versions/API.md.[timestamp].bak
```

```bash
uv run python -m doc_evergreen.cli regenerate docs/API.md
```

### Example 3: User Wants Multiple Documents

**User:** "I need README, API docs, and a contributing guide"

**Assistant:**
```
"I'll help you create all three documents. Let's do them one at a time.

Starting with README:
What should it cover?"
```

**User:** "Project overview, installation, and basic usage"

**Assistant:**
```
"Perfect. Creating README first..."
```

```bash
uv run python -m doc_evergreen.cli create \
    --about "Project overview, installation, and basic usage" \
    --output README.md
```

```
"✓ README.md created

Now for API docs:
What should the API documentation cover?"
```

**User:** "All REST endpoints and authentication"

```bash
uv run python -m doc_evergreen.cli create \
    --about "REST API endpoints and authentication" \
    --output docs/API.md \
    --sources "src/api/**/*.py"
```

```
"✓ docs/API.md created

Finally, the contributing guide:
This will include CONTRIBUTING.md and .github files. Sound good?"
```

```bash
uv run python -m doc_evergreen.cli create \
    --about "Contributing guidelines for developers" \
    --output CONTRIBUTING.md \
    --template developer-guide
```

```
"✓ All three documents created!

You can regenerate all at once later with:
  doc-evergreen regenerate --all"
```

## Troubleshooting Guide for Assistants

### Issue: "No source files found"

**Check:**
1. Are the glob patterns correct? Test with `ls pattern`
2. Are files being excluded by .gitignore? Check `git check-ignore -v file`
3. Try using auto-discovery instead of explicit patterns

**Help user fix:**
```
"Let me check what files exist:
  ls -la src/**/*.py

The pattern didn't match any files. Try:
- Checking if files exist at that path
- Using a different pattern
- Letting doc-evergreen auto-discover files"
```

### Issue: "Rate limit exceeded"

**Explain:**
```
"The Anthropic API has rate limits. doc-evergreen will automatically retry
with exponential backoff.

If it keeps failing:
1. Wait 60 seconds and try again
2. Check your API quota at console.anthropic.com
3. Try fewer documents at once (not --all)"
```

### Issue: "Invalid UTF-8"

**Explain:**
```
"Some source files aren't valid UTF-8 text (might be binary files).

doc-evergreen only works with text files. The tool will skip invalid files
and continue with valid ones.

If important files are being skipped, they might be:
- Binary files (images, compiled code)
- Files with wrong encoding

Try excluding those patterns from --sources"
```

### Issue: Generation takes too long

**Explain:**
```
"LLM generation typically takes 30-60 seconds per document.

For large projects with many source files:
- The tool includes up to 50KB of source content
- Larger projects may take longer
- You can reduce sources to speed up generation

The tool shows progress messages:
  📁 Step 1: Gathering source files...
  📝 Step 2: Loading template...
  🤖 Step 3: Generating documentation...
  (this is where it takes time)
  💾 Step 4: Backing up existing document...
  💾 Step 5: Saving document...
  📋 Step 6: Updating history..."
```

## Command Construction Rules

### For create command:

**Minimal (auto-discovery):**
```bash
doc-evergreen create --about "DESCRIPTION" --output PATH
```

**With explicit sources:**
```bash
doc-evergreen create \
    --about "DESCRIPTION" \
    --output PATH \
    --sources "pattern1" "pattern2"
```

**With template:**
```bash
doc-evergreen create \
    --about "DESCRIPTION" \
    --output PATH \
    --template readme
```

**Dry run:**
```bash
doc-evergreen create \
    --about "DESCRIPTION" \
    --output PATH \
    --dry-run
```

### For regenerate command:

**Single document:**
```bash
doc-evergreen regenerate PATH
```

**All documents:**
```bash
doc-evergreen regenerate --all
```

**Dry run:**
```bash
doc-evergreen regenerate PATH --dry-run
doc-evergreen regenerate --all --dry-run
```

## Best Practices for Assistants

### 1. Always Start with Questions

Don't assume what the user wants. Ask:
- What type of documentation?
- What should it cover?
- Where to save it?

### 2. Offer Dry-Run First

Especially for first-time users, always suggest `--dry-run` to preview.

### 3. Explain Time Expectations

Generation takes 30-60 seconds. Set expectations upfront.

### 4. Show the Command

Always show the exact command you're running so users can:
- Learn the syntax
- Modify it themselves later
- Understand what's happening

### 5. Check Configuration State

Before regenerating, check `.doc-evergreen/history.yaml` to show what's configured.

### 6. Handle Errors Gracefully

When errors occur:
- Read the error message carefully
- Explain in simple terms what went wrong
- Provide specific fix steps
- Offer to try again

### 7. Teach as You Go

Use comments in commands:
```bash
# Generate README with auto-discovered sources
uv run python -m doc_evergreen.cli create \
    --about "Main project README" \
    --output README.md
```

### 8. Track What's Been Created

After creating documents, remind users:
```
"You now have:
- README.md (generated)
- .doc-evergreen/history.yaml (configuration)
- .doc-evergreen/versions/ (backups)

Regenerate anytime with: doc-evergreen regenerate README.md"
```

## Common User Goals and Responses

### "I need a README"
→ Use auto-discovery, ask about project description

### "My docs are outdated"
→ Use regenerate command

### "I changed my API"
→ Regenerate API.md specifically

### "I need multiple docs"
→ Create one at a time, then mention regenerate --all

### "How do I customize the template?"
→ Templates are auto-customized, but saved to .doc-evergreen/templates/ for manual editing

### "Can I edit the generated docs?"
→ Yes, but they'll be overwritten on regeneration. Either:
  1. Edit and don't regenerate
  2. Edit the template in .doc-evergreen/templates/
  3. Use additional manual docs alongside generated ones

## Success Criteria

A successful interaction results in:

1. ✅ User understands what documentation will be generated
2. ✅ Appropriate sources and template selected
3. ✅ Document generated successfully
4. ✅ User knows how to regenerate later
5. ✅ Configuration saved in .doc-evergreen/history.yaml

## Anti-Patterns to Avoid

❌ Running commands without explaining them
❌ Not offering dry-run for first-time users
❌ Assuming users have API key set up
❌ Not checking for errors before proceeding
❌ Creating documents without user confirmation of approach
❌ Not explaining what .doc-evergreen/ directory is for

## Quick Reference

**User wants to create docs:**
1. Ask what type and what to cover (--about)
2. Ask where to save (--output)
3. Offer auto-discovery or manual --sources
4. Show dry-run command
5. Run actual command after confirmation

**User wants to update docs:**
1. Check .doc-evergreen/history.yaml
2. Show configured documents
3. Run regenerate for specific or --all
4. Explain backup and versioning

**User hits an error:**
1. Read error message carefully
2. Check common issues (API key, source files, UTF-8)
3. Provide specific fix steps
4. Retry after fix

**User is confused:**
1. Show README.md examples
2. Explain the 6-step generation process
3. Start with simplest case (auto-discovery)
4. Build complexity gradually

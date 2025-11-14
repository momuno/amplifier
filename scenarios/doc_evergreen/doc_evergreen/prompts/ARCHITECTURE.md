# Prompt Architecture

## Overview

All LLM prompts are externalized into individual `.txt` files for easy editing and version control. This architecture separates business logic (Python code) from prompt engineering (text templates).

## Directory Structure

```
doc_evergreen/prompts/
├── __init__.py                          # load_prompt() helper function
├── README.md                            # Usage documentation
├── ARCHITECTURE.md                      # This file
├── summarize_file.txt                   # Step 2: File summarization
├── create_customized_template.txt       # Step 3: Template customization
├── customize_template.txt               # Legacy (not used)
└── generate_document.txt                # Step 4: Document generation
```

## Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    CREATE COMMAND FLOW                       │
└─────────────────────────────────────────────────────────────┘

Step 1: File Sourcing
    [Gather source files based on patterns]
                    ↓

Step 2: File Summarization
    [For each source file:]

    ┌─────────────────────────────────┐
    │ load_prompt("summarize_file")   │
    │   ↓                              │
    │ prompts/summarize_file.txt      │
    │   ↓                              │
    │ .format(file_path, file_content)│
    │   ↓                              │
    │ call_llm(prompt)                │
    └─────────────────────────────────┘
                    ↓
    [Cache summary in summaries.yaml]
                    ↓

Step 3: Template Customization
    [Load template guide]

    ┌──────────────────────────────────────────┐
    │ load_prompt("create_customized_template")│
    │   ↓                                       │
    │ prompts/create_customized_template.txt   │
    │   ↓                                       │
    │ .format(template_guide, about, summaries)│
    │   ↓                                       │
    │ call_llm(prompt)                         │
    └──────────────────────────────────────────┘
                    ↓
    [Save customized template]
                    ↓

Step 4: Document Generation
    [Load customized template]

    ┌──────────────────────────────────┐
    │ load_prompt("generate_document") │
    │   ↓                               │
    │ prompts/generate_document.txt    │
    │   ↓                               │
    │ .format(template, about)         │
    │   ↓                               │
    │ call_llm(prompt)                 │
    └──────────────────────────────────┘
                    ↓
    [Save final documentation]
```

## Prompt Loading Mechanism

### Code Usage

```python
from doc_evergreen.prompts import load_prompt

# Load prompt template
prompt_template = load_prompt("summarize_file")

# Format with variables
prompt = prompt_template.format(
    file_path="example.py",
    file_content="def hello(): pass"
)

# Send to LLM
response = call_llm(prompt)
```

### File Format

Prompts use Python's `.format()` style placeholders:

```
Analyze this source file and provide a summary.

File: {file_path}

Content:
{file_content}

Instructions:
1. Identify the primary purpose
2. List key functionality
3. Note how it fits into the larger system
```

## Benefits

1. **Separation of Concerns**: Prompt engineering is separate from code logic
2. **Easy Editing**: No code changes needed to iterate on prompts
3. **Version Control**: Each prompt has its own git history
4. **Collaboration**: Non-programmers can contribute to prompt improvements
5. **Testing**: Prompts can be tested independently
6. **Reusability**: Same prompt loader works for all prompts

## Adding New Prompts

1. Create new `.txt` file in `doc_evergreen/prompts/`
2. Use `{variable_name}` for placeholders
3. Load with `load_prompt("your_prompt_name")`
4. Format with `.format(variable_name=value)`
5. Update this documentation

## Prompt Dependencies

```
summarize_file.txt
    ↓
    Used by: Step 2 (File Summarization)
    Depends on: None
    Format vars: file_path, file_content

create_customized_template.txt
    ↓
    Used by: Step 3 (Template Customization)
    Depends on: summaries from Step 2
    Format vars: template_guide, about, formatted_summaries

generate_document.txt
    ↓
    Used by: Step 4 (Document Generation)
    Depends on: customized template from Step 3
    Format vars: template, about
```

## Error Handling

The `load_prompt()` function will raise `FileNotFoundError` if:
- Prompt file doesn't exist
- Prompt file name is misspelled
- Directory structure is incorrect

Always verify prompt files exist before deployment.

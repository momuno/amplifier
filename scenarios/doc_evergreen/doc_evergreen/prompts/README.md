# LLM Prompts

This directory contains all the prompt templates used by doc-evergreen for LLM interactions.

## Structure

Each prompt is stored in a separate `.txt` file for easy editing and version control.

## Available Prompts

- **summarize_file.txt**: Generates a concise summary of a source file
- **create_customized_template.txt**: Creates a customized template with section-to-file mappings
- **customize_template.txt**: Customizes a built-in template for a specific project (legacy, not currently used)
- **generate_document.txt**: Generates final documentation from a template and context

## Usage

Import and use the `load_prompt()` function:

```python
from doc_evergreen.prompts import load_prompt

# Load a prompt template
prompt_template = load_prompt("summarize_file")

# Format with your variables
prompt = prompt_template.format(file_path="example.py", file_content="def hello(): pass")
```

## Template Variables

Each prompt uses Python's `.format()` string formatting. Variables are specified with `{variable_name}`.

### summarize_file.txt
- `{file_path}`: Path to the file being summarized
- `{file_content}`: Full content of the file

### create_customized_template.txt
- `{template_guide}`: Base template guide content
- `{about}`: User's description of what documentation is about
- `{formatted_summaries}`: Pre-formatted list of file summaries

### customize_template.txt
- `{builtin_template}`: Built-in template content
- `{about}`: Description of documentation topic
- `{source_context}`: Optional formatted source files preview
- `{existing_doc_context}`: Optional existing document structure

### generate_document.txt
- `{template}`: Customized template with instructions
- `{about}`: Description of what documentation is about

## Modifying Prompts

To modify a prompt:
1. Edit the `.txt` file directly
2. Test your changes with the actual LLM calls
3. No code changes needed - prompts are loaded at runtime

## Best Practices

- Keep prompts clear and concise
- Use specific instructions rather than vague requests
- Include examples where helpful
- Document expected input/output formats
- Test prompt changes thoroughly before committing

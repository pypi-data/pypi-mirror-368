# Usage Guide for process_instructions.py

## Overview
This script processes instructions from `INSTRUCT.md` to build a context from various files and perform AI completions.

## Quick Example
See the `example/` directory for a complete working example. Run it with:
```bash
python3 test_example.py
```

## Installation

```bash
pip install -r requirements.txt
```

## Configuration

### Using OpenAI API
```bash
export OPENAI_API_KEY="your-openai-api-key"
export OPENAI_BASE_URL="https://api.openai.com/v1"  # Optional, for custom endpoints
export OPENAI_MODEL="gpt-4"  # Optional, default is gpt-4
python3 process_instructions.py
```

### Using OpenRouter
```bash
export OPENROUTER_API_KEY="your-openrouter-api-key"
export OPENROUTER_BASE_URL="https://openrouter.ai/api/v1"  # Optional, this is the default
export OPENROUTER_MODEL="openai/gpt-4"  # Optional, specify your preferred model
python3 process_instructions.py
```

### Available OpenRouter Models
Some popular models you can use with OpenRouter:
- `openai/gpt-4`
- `openai/gpt-3.5-turbo`
- `anthropic/claude-3-opus`
- `anthropic/claude-3-sonnet`
- `google/gemini-pro`
- `meta-llama/llama-3-70b-instruct`

## Instruction Format

In `INSTRUCT.md`, you can use:
- `@filename.md` - Include file content inline
- `@directory/` - Include all files from directory with XML-style tags
- `/completion` - Perform AI completion on current context
- `/model MODEL_NAME` - Set the model for subsequent completions
- Empty lines are ignored

You can use multiple `/completion` instructions to perform sequential completions, with each completion result added to the context for the next one.

### Model Override

The `/model` instruction allows you to change the model for subsequent completions:

```
@context.md
/model gpt-3.5-turbo
/completion
@more_context.md
/model gpt-4
/completion
```

This is useful when you want to:
- Use a faster/cheaper model for initial drafts
- Switch to a more capable model for complex tasks
- Test the same prompt with different models

## Custom System Prompt

You can customize the AI's system prompt by creating a `SYSTEM.md` file in the same directory as `INSTRUCT.md`. This allows you to define the AI's behavior, role, or specific instructions.

Example `SYSTEM.md`:
```
You are an expert Python developer. Provide concise, idiomatic Python code with clear explanations. Focus on best practices and performance.
```

If no `SYSTEM.md` file exists, the default system prompt is: "You are a helpful assistant providing advice."

## Example INSTRUCT.md

```
@header.md
@resources/
@reasoning.md
/completion
@footer.md
```

## Example with Multiple Completions

```
@initial_context.md
/completion
@additional_context.md
/completion
```

This will:
1. Load initial_context.md
2. Perform first completion and add result to context
3. Load additional_context.md
4. Perform second completion with all previous content as context

## Output Files

- `CONTEXT.md` - The assembled context from all files including all completion results
- `COMPLETION.json` - Raw API response from the last completion (overwrites previous)
- `COMPLETION.md` - The completion text from the last completion (overwrites previous)
- Note: If the API response contains a "reasoning" field instead of "content", it's wrapped in `<reasoning>` tags

## Token Usage Tracking

The script automatically tracks and displays token usage for each completion:
- Shows input tokens, output tokens, and total for each completion
- Provides a summary of total token usage across all completions
- Helps monitor API costs and usage limits

Example output:
```
  Token usage - Input: 73, Output: 200, Total: 273
Performed completion #1 and added to context

=== Token Usage Summary ===
Completion #1: Input: 73, Output: 200, Total: 273
Completion #2: Input: 287, Output: 200, Total: 487

Total across all completions:
  Input tokens: 360
  Output tokens: 400
  Total tokens: 760
```

## Troubleshooting

1. **No API key**: The script will use a mock response if no API keys are configured
2. **File not found**: Script will skip missing files with a warning
3. **API errors**: Check your API key and internet connection
4. **OpenRouter errors**: Ensure your API key has credits and the model is available
# Example Test Case

This directory contains a simple test case for the passive-agent instruction processor.

## Files

- `INSTRUCT.md` - The instruction file that defines the processing flow
- `SYSTEM.md` - Custom system prompt for the AI (climate advisor persona)
- `header.md` - Contains "today is hot day."
- `resources/` - Directory with two resource files:
  - `resource1.md` - "this summer is hotter than last year."
  - `resource2.md` - "rain is less than last year."
- `reasoning.md` - Contains "how about next year?"
- `footer.md` - Contains "what should I do this year?"

## Instruction Flow

The `INSTRUCT.md` file contains:
```
@header.md
@resources/
@reasoning.md
/completion
@footer.md
/completion
```

This will:
1. Load header.md content
2. Load all files from resources/ directory with XML tags
3. Load reasoning.md content
4. Perform first AI completion (using SYSTEM.md prompt)
5. Load footer.md content
6. Perform second AI completion (using SYSTEM.md prompt)

## Custom System Prompt

The `SYSTEM.md` file defines a climate advisor persona that provides evidence-based insights and practical recommendations for dealing with climate patterns.

## Output

After running, you'll find:
- `CONTEXT.md` - The complete assembled context with all completions
- `COMPLETION.json` - The raw API response from the last completion
- `COMPLETION.md` - The text content from the last completion

## Running the Test

From the parent directory, run:
```bash
python3 test_example.py
```

Or manually:
```bash
cd example
passive-agent
```
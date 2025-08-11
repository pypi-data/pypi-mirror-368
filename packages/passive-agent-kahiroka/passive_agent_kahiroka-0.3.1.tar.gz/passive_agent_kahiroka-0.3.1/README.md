# passive-agent

A passive agent for prompt engineering experiments with instruction-based context building.

## Overview

Passive Agent is a flexible tool for building complex contexts by processing instructions that combine file content with AI completions. It's designed for prompt engineering experiments where you need to iteratively build context from multiple sources.

## Features

- 📄 Load content from files and directories
- 🤖 Integrate AI completions into context (supports OpenAI and OpenRouter)
- 🔄 Sequential processing with context accumulation
- 📊 Token usage tracking and reporting
- 🎯 Simple instruction-based workflow
- 🎭 Custom system prompts via SYSTEM.md
- 🔀 Dynamic model switching with /model instruction

## Installation

```bash
pip install passive-agent
```

Or install from source:
```bash
git clone https://github.com/yourusername/passive-agent
cd passive-agent
pip install -e .
```

## Quick Start

1. Create an `INSTRUCT.md` file with your instructions:
   ```
   @header.md
   @data/
   /completion
   @footer.md
   ```

2. Run passive-agent:
   ```bash
   passive-agent
   ```

3. Check the generated files:
   - `CONTEXT.md` - Complete context with all content
   - `COMPLETION.json` - Raw API response
   - `COMPLETION.md` - Completion text

## Example

See the `example/` directory for a complete working example:

```bash
cd example
passive-agent
```

## Configuration

### OpenAI
```bash
export OPENAI_API_KEY="your-key"
export OPENAI_MODEL="gpt-4"  # Optional, default is gpt-4
export OPENAI_BASE_URL="https://api.openai.com/v1"  # Optional, for custom endpoints
passive-agent
```

### OpenRouter
```bash
export OPENROUTER_API_KEY="your-key"
export OPENROUTER_MODEL="anthropic/claude-3-opus"
passive-agent
```

## Documentation

For detailed usage instructions, see [USAGE.md](USAGE.md).

## License

MIT License - see [LICENSE](LICENSE) file for details.

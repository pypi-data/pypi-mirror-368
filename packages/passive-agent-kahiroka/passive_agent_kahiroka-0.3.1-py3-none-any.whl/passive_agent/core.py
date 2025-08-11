#!/usr/bin/env python3
"""
Process instructions from INSTRUCT.md file.

This script reads instructions from INSTRUCT.md and executes them:
- @FILE_NAME: Adds file content inline to context
- @DIRECTORY_NAME: Adds directory files with <file name="...">content</file> tags
- /completion: Performs OpenAI API completion
- /model MODEL_NAME MAX_TOKENS: Sets the model and max_tokens for subsequent completions
- Writes intermediate context to CONTEXT.md
- Writes final completion to COMPLETION.json and COMPLETION.md

If SYSTEM.md exists in the working directory, its content will be used as the system prompt
for AI completions. Otherwise, a default prompt is used.

Supports both OpenAI and OpenRouter APIs:
- OpenAI: Set OPENAI_API_KEY and optionally OPENAI_BASE_URL and OPENAI_MODEL
- OpenRouter: Set OPENROUTER_API_KEY and optionally OPENROUTER_BASE_URL and OPENROUTER_MODEL
"""

import os
import json
import sys
from pathlib import Path
from typing import List, Dict, Any

try:
    import openai
except ImportError:
    print("Warning: OpenAI package not installed. Install with: pip install openai")
    print("Completion will use mock response.")
    openai = None


def read_file(filepath: Path) -> str:
    """Read content from a file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read().strip()
    except FileNotFoundError:
        print(f"Error: File {filepath} not found")
        return ""
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        return ""


def read_directory(dirpath: Path) -> List[Dict[str, str]]:
    """Read all files from a directory."""
    files = []
    try:
        for file in sorted(dirpath.iterdir()):
            if file.is_file():
                content = read_file(file)
                if content:
                    files.append({
                        'name': file.name,
                        'content': content
                    })
    except FileNotFoundError:
        print(f"Error: Directory {dirpath} not found")
    except Exception as e:
        print(f"Error reading directory {dirpath}: {e}")
    return files


def process_instructions(instructions: List[str]) -> tuple[str, List[Dict[str, int]]]:
    """Process instructions and build context. Returns (context, token_stats)."""
    context_parts = []
    completion_count = 0
    token_stats = []
    override_model = None  # Track model override from /model instruction
    override_max_tokens = None  # Track max_tokens override from /model instruction
    
    for instruction in instructions:
        instruction = instruction.strip()
        if not instruction:
            continue
            
        if instruction.startswith('@'):
            path = Path(instruction[1:])
            
            if path.is_file():
                # @FILE_NAME - add inline
                content = read_file(path)
                if content:
                    context_parts.append(content)
                    print(f"Added file: {path}")
            
            elif path.is_dir():
                # @DIRECTORY_NAME - add with file tags
                files = read_directory(path)
                for file in files:
                    tagged_content = f'<file name="{file["name"]}">\n{file["content"]}\n</file>'
                    context_parts.append(tagged_content)
                    print(f"Added file from directory: {path}/{file['name']}")
            
            else:
                print(f"Warning: Path {path} not found")
        
        elif instruction == '/completion':
            # Perform completion and add to context
            current_context = '\n'.join(context_parts)
            completion_count += 1
            completion_content, tokens = perform_completion(current_context, completion_count, override_model, override_max_tokens)
            if completion_content:
                context_parts.append(completion_content)
                print(f"Performed completion #{completion_count} and added to context")
            if tokens:
                token_stats.append(tokens)
        
        elif instruction.startswith('/model '):
            # Set model and max_tokens override for subsequent completions
            parts = instruction[7:].strip().split()
            if len(parts) >= 1:
                override_model = parts[0]
                print(f"Model override set to: {override_model}")
            if len(parts) >= 2:
                try:
                    override_max_tokens = int(parts[1])
                    print(f"Max tokens override set to: {override_max_tokens}")
                except ValueError:
                    print(f"Warning: Invalid max_tokens value '{parts[1]}', ignoring")
            if len(parts) > 2:
                print(f"Warning: Extra parameters ignored: {' '.join(parts[2:])}")
    
    return '\n'.join(context_parts), token_stats


def perform_completion(context: str, completion_num: int = 1, override_model: str = None, override_max_tokens: int = None) -> tuple[str, Dict[str, int]]:
    """Perform OpenAI API completion or return mock response. Returns (content, token_stats)."""
    # Check for system prompt from SYSTEM.md
    system_prompt = "You are a helpful assistant providing advice."
    system_path = Path('SYSTEM.md')
    if system_path.exists():
        try:
            with open(system_path, 'r', encoding='utf-8') as f:
                system_prompt = f.read().strip()
                print(f"  Using custom system prompt from SYSTEM.md")
        except Exception as e:
            print(f"  Warning: Could not read SYSTEM.md: {e}")
    
    # Check for OpenRouter configuration
    openrouter_api_key = os.getenv('OPENROUTER_API_KEY')
    openrouter_base_url = os.getenv('OPENROUTER_BASE_URL', 'https://openrouter.ai/api/v1')
    
    # Check for standard OpenAI configuration
    openai_api_key = os.getenv('OPENAI_API_KEY')
    
    if openai and (openrouter_api_key or openai_api_key):
        try:
            if openrouter_api_key:
                # Use OpenRouter
                client = openai.OpenAI(
                    api_key=openrouter_api_key,
                    base_url=openrouter_base_url
                )
                model = override_model or os.getenv('OPENROUTER_MODEL', 'google/gemini-2.0-flash-exp:free')
                if override_model:
                    print(f"Using OpenRouter with overridden model: {model}")
                else:
                    print(f"Using OpenRouter with model: {model}")
            else:
                # Use standard OpenAI
                openai_base_url = os.getenv('OPENAI_BASE_URL')
                if openai_base_url:
                    client = openai.OpenAI(
                        api_key=openai_api_key,
                        base_url=openai_base_url
                    )
                else:
                    client = openai.OpenAI(api_key=openai_api_key)
                model = override_model or os.getenv('OPENAI_MODEL', 'gpt-4')
                if override_model:
                    print(f"Using OpenAI with overridden model: {model}")
                else:
                    print(f"Using OpenAI with model: {model}")
            
            max_tokens = override_max_tokens or 4096
            if override_max_tokens:
                print(f"  Using overridden max_tokens: {max_tokens}")
            else:
                print(f"  Using default max_tokens: {max_tokens}")
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": context}
                ],
                temperature=0.7,
                max_tokens=max_tokens
            )
            
            # Save raw response
            response_dict = response.model_dump()
            # Always overwrite COMPLETION.json with the latest completion
            with open('COMPLETION.json', 'w', encoding='utf-8') as f:
                json.dump(response_dict, f, indent=2)
            
            # Extract token usage
            token_stats = None
            if hasattr(response, 'usage') and response.usage:
                usage = response.usage
                token_stats = {
                    'input': usage.prompt_tokens,
                    'output': usage.completion_tokens,
                    'total': usage.total_tokens
                }
                print(f"  Token usage - Input: {token_stats['input']}, Output: {token_stats['output']}, Total: {token_stats['total']}")
            
            # Extract content or reasoning
            message = response.choices[0].message
            if hasattr(message, 'content') and message.content:
                content = message.content
            elif hasattr(message, 'reasoning') and message.reasoning:
                # Use reasoning field wrapped in tags
                content = f"<reasoning>{message.reasoning}</reasoning>"
            else:
                # Fallback - check dict representation
                message_dict = message.model_dump() if hasattr(message, 'model_dump') else message
                if isinstance(message_dict, dict):
                    if message_dict.get('content'):
                        content = message_dict['content']
                    elif message_dict.get('reasoning'):
                        content = f"<reasoning>{message_dict['reasoning']}</reasoning>"
                    else:
                        content = "No content or reasoning found in response"
                else:
                    content = "No content or reasoning found in response"
            
            # Always overwrite COMPLETION.md with the latest completion
            with open('COMPLETION.md', 'w', encoding='utf-8') as f:
                f.write(content)
            
            return content, token_stats
            
        except Exception as e:
            print(f"Error with OpenAI API: {e}")
            print("Using mock response instead")
    
    # Mock response when OpenAI is not available
    # Calculate approximate tokens based on context length
    context_tokens = len(context.split()) * 1.3  # Rough approximation
    mock_response = {
        "model": "gpt-4",
        "choices": [{
            "message": {
                "role": "assistant",
                "content": "Hi there. This is a mock response."
            },
            "finish_reason": "stop",
            "index": 0
        }],
        "usage": {
            "prompt_tokens": int(context_tokens),
            "completion_tokens": 95,
            "total_tokens": int(context_tokens) + 95
        }
    }
    
    # Save mock response
    # Always overwrite COMPLETION.json with the latest completion
    with open('COMPLETION.json', 'w', encoding='utf-8') as f:
        json.dump(mock_response, f, indent=2)
    
    # Extract token usage for mock response
    usage = mock_response["usage"]
    token_stats = {
        'input': usage['prompt_tokens'],
        'output': usage['completion_tokens'],
        'total': usage['total_tokens']
    }
    print(f"  Token usage - Input: {token_stats['input']}, Output: {token_stats['output']}, Total: {token_stats['total']}")
    
    # Extract content or reasoning from mock response
    message = mock_response["choices"][0]["message"]
    if message.get("content"):
        content = message["content"]
    elif message.get("reasoning"):
        content = f"<reasoning>{message['reasoning']}</reasoning>"
    else:
        content = "No content or reasoning found in response"
    
    # Always overwrite COMPLETION.md with the latest completion
    with open('COMPLETION.md', 'w', encoding='utf-8') as f:
        f.write(content)
    
    return content, token_stats


def main():
    """Main execution function."""
    # Display configuration info
    print("=== Configuration ===")
    if os.getenv('OPENROUTER_API_KEY'):
        print("API: OpenRouter")
        print(f"Base URL: {os.getenv('OPENROUTER_BASE_URL', 'https://openrouter.ai/api/v1')}")
        print(f"Model: {os.getenv('OPENROUTER_MODEL', 'google/gemini-2.0-flash-exp:free')}")
    elif os.getenv('OPENAI_API_KEY'):
        print("API: OpenAI")
        openai_base_url = os.getenv('OPENAI_BASE_URL')
        if openai_base_url:
            print(f"Base URL: {openai_base_url}")
        print(f"Model: {os.getenv('OPENAI_MODEL', 'gpt-4')}")
    else:
        print("API: None (will use mock response)")
    print("=" * 20 + "\n")
    
    # Read instructions
    instruct_path = Path('INSTRUCT.md')
    if not instruct_path.exists():
        print("Error: INSTRUCT.md not found in current directory")
        sys.exit(1)
    
    with open(instruct_path, 'r', encoding='utf-8') as f:
        instructions = [line.strip() for line in f if line.strip()]
    
    print(f"Found {len(instructions)} instructions")
    
    # Process instructions
    final_context, token_stats = process_instructions(instructions)
    
    # Write intermediate context
    with open('CONTEXT.md', 'w', encoding='utf-8') as f:
        f.write(final_context)
    print("\nWrote intermediate context to CONTEXT.md")
    
    # Perform final completion if not already done
    if '/completion' not in instructions:
        print("\nPerforming final completion...")
        _, tokens = perform_completion(final_context)
        if tokens:
            token_stats.append(tokens)
    
    # Count completions in instructions
    completion_count = instructions.count('/completion')
    
    print("\nProcess completed successfully!")
    print("Generated files:")
    print("- CONTEXT.md (intermediate context)")
    
    if completion_count > 0:
        print("- COMPLETION.json (raw API response from last completion)")
        print("- COMPLETION.md (completion content from last completion)")
    
    # Display token usage summary
    if token_stats:
        print("\n=== Token Usage Summary ===")
        total_input = sum(stat['input'] for stat in token_stats)
        total_output = sum(stat['output'] for stat in token_stats)
        total_tokens = sum(stat['total'] for stat in token_stats)
        
        for i, stat in enumerate(token_stats, 1):
            print(f"Completion #{i}: Input: {stat['input']}, Output: {stat['output']}, Total: {stat['total']}")
        
        if len(token_stats) > 1:
            print(f"\nTotal across all completions:")
            print(f"  Input tokens: {total_input}")
            print(f"  Output tokens: {total_output}")
            print(f"  Total tokens: {total_tokens}")


if __name__ == '__main__':
    main()

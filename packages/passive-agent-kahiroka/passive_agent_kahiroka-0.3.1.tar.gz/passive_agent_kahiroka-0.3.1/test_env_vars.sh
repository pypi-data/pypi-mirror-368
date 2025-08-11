#!/bin/bash
# Test script to demonstrate environment variable configurations

echo "=== Testing Environment Variable Configurations ==="
echo ""

# Test 1: OpenAI with custom base URL and model
echo "1. Testing OpenAI with custom settings:"
export OPENAI_API_KEY="test-key"
export OPENAI_BASE_URL="https://custom.openai.proxy.com/v1"
export OPENAI_MODEL="gpt-3.5-turbo"

echo "   OPENAI_API_KEY=$OPENAI_API_KEY"
echo "   OPENAI_BASE_URL=$OPENAI_BASE_URL"
echo "   OPENAI_MODEL=$OPENAI_MODEL"
echo ""

# Clear OpenRouter vars to ensure OpenAI is used
unset OPENROUTER_API_KEY

# Note: This will show the configuration but fail due to invalid API key
cd example && python3 ../src/passive_agent/core.py 2>&1 | head -n 10

echo ""
echo "2. Testing OpenRouter configuration:"
unset OPENAI_API_KEY
export OPENROUTER_API_KEY="test-openrouter-key"
export OPENROUTER_MODEL="anthropic/claude-3-opus"

echo "   OPENROUTER_API_KEY=$OPENROUTER_API_KEY"
echo "   OPENROUTER_MODEL=$OPENROUTER_MODEL"
echo ""

cd ../example && python3 ../src/passive_agent/core.py 2>&1 | head -n 10

echo ""
echo "Note: The above tests show configuration display only."
echo "Actual API calls will fail with test keys."
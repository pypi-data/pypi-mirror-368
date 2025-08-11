# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python-based project for experimenting with passive agents and prompt engineering. Currently, the repository is in its initial state with no implementation.

## Development Setup

### Python Environment
This project is intended to use Python. When implementing:
- Create a virtual environment before installing dependencies
- Use standard Python project structure (src/, tests/, etc.)
- Follow PEP 8 style guidelines

### Project Structure (To Be Implemented)
When building out this project, consider:
- `src/` - Main source code
- `tests/` - Test files
- `docs/` - Documentation
- `examples/` - Example usage and experiments

## Key Concepts

### Passive Agent
This project focuses on building a "passive agent" for prompt engineering experiments. When implementing:
- Consider how the agent observes and responds without taking active actions
- Focus on prompt handling and response generation
- Design for experimentation and iterative prompt refinement

## Development Guidelines

### When Adding Features
1. Since this is a playground for experimentation, prioritize flexibility and ease of testing different approaches
2. Consider implementing logging and metrics to track prompt effectiveness
3. Design with modularity in mind to easily swap different prompt strategies

### Testing Approach
When tests are added:
- Use pytest as the standard Python testing framework
- Create unit tests for core agent logic
- Include integration tests for prompt processing pipelines

## Notes

- The project is currently empty - all architecture decisions are open
- The .gitignore is configured for Python development
- No external dependencies or frameworks are currently in use
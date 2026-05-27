# Phase 0: Minimal LLM Agent

This repository contains a minimal Anthropic-powered agent loop in `phase0.py`.

## Goal

Build a small loop that:

1. Sends a prompt to an LLM
2. Parses the response
3. Calls tools when needed
4. Feeds tool results back into the next prompt
5. Stops when the model gives a final answer or when the iteration cap is reached

## What you need

- An Anthropic account
- An Anthropic API key
- Python 3.10+
- A billing method with at least $20 available for testing

## Setup

1. Create an Anthropic account
2. Generate an API key
3. Add a billing method and ensure you have at least $20 available
4. Install Python 3.10+
5. Create a virtual environment if you want
6. Export your API key

## Example environment setup

```bash
export ANTHROPIC_API_KEY="your-api-key"
```

Optional model override:

```bash
export ANTHROPIC_MODEL="claude-3-5-sonnet-20241022"
```

Optional iteration cap override:

```bash
export MAX_ITERATIONS="6"
```

## Run the script

```bash
python phase0.py
```

## What the script does

The script demonstrates a minimal agent loop:

- Prompt the model
- Inspect the response for text or tool calls
- Run tools if needed
- Send tool results back to the model
- Stop on a final answer or after the iteration cap

The available tools are:

- `run_python`
- `read_file`
- `write_file`

## Example task

The current task is:

- Find the largest file in this directory and summarize it.

## Learning goals

By completing this phase, you should understand that an agent is mechanically just:

- a loop
- a model call
- optional tool execution
- feedback from tool results into the next prompt

## Notes

- Keep an eye on Anthropic usage while testing.
- The current script is intentionally minimal and framework-free.
- Use the iteration cap to avoid infinite loops.
# Phase0AgentTesting

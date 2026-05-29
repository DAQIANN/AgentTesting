# Phase 0: Minimal LLM Agent

- Write a Python script that calls the API in a loop: prompt → response → parse → next prompt. No frameworks.
- Add tool use: give the model a Python execution tool and a file read/write tool. Have it solve a small task (e.g., "find the largest file in this directory and summarize it").
- Add a termination condition and a max-iteration cap.
- Checkpoint: Writing something that constitutes a minimal agent.

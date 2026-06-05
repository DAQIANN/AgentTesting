# Phase 0: Minimal LLM Agent

- Write a Python script that calls the API in a loop: prompt → response → parse → next prompt. No frameworks.
- Add tool use: give the model a Python execution tool and a file read/write tool. Have it solve a small task (e.g., "find the largest file in this directory and summarize it").
- Add a termination condition and a max-iteration cap.
- Checkpoint: Writing something that constitutes a minimal agent.

## Phase 1: Build one real agent for one real task

A natural next step is to build an agent around a bounded, verifiable coding task. A strong fit is HumanEval or MBPP, since these problems include hidden tests and provide a built-in verifier.

The aim here is to create an agent loop that:

- reads a problem statement,
- writes code,
- runs that code against visible tests,
- iterates on failures,
- and submits a final result.

The work should also preserve full trajectories on disk, including prompts, responses, tool calls, test results, and token usage. Running this setup across 50 problems makes it possible to measure overall pass rate, and repeating the same 50-problem run five times helps surface variance in agent behavior.

This phase is meant to produce a working agent, verifier, stored traces, and an empirical pass-rate result with error bars.

Running HumanEval tests:
```
@article{chen2021codex,
  title={Evaluating Large Language Models Trained on Code},
  author={Mark Chen and Jerry Tworek and Heewoo Jun and Qiming Yuan and Henrique Ponde de Oliveira Pinto and Jared Kaplan and Harri Edwards and Yuri Burda and Nicholas Joseph and Greg Brockman and Alex Ray and Raul Puri and Gretchen Krueger and Michael Petrov and Heidy Khlaaf and Girish Sastry and Pamela Mishkin and Brooke Chan and Scott Gray and Nick Ryder and Mikhail Pavlov and Alethea Power and Lukasz Kaiser and Mohammad Bavarian and Clemens Winter and Philippe Tillet and Felipe Petroski Such and Dave Cummings and Matthias Plappert and Fotios Chantzis and Elizabeth Barnes and Ariel Herbert-Voss and William Hebgen Guss and Alex Nichol and Alex Paino and Nikolas Tezak and Jie Tang and Igor Babuschkin and Suchir Balaji and Shantanu Jain and William Saunders and Christopher Hesse and Andrew N. Carr and Jan Leike and Josh Achiam and Vedant Misra and Evan Morikawa and Alec Radford and Matthew Knight and Miles Brundage and Mira Murati and Katie Mayer and Peter Welinder and Bob McGrew and Dario Amodei and Sam McCandlish and Ilya Sutskever and Wojciech Zaremba},
  year={2021},
  eprint={2107.03374},
  archivePrefix={arXiv},
  primaryClass={cs.LG}
}
```
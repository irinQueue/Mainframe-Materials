# Techniques and templates (from "Mastering Claude Code", Module 2)

Rule: pick the technique first (how Claude reasons), then wrap it in a
template (how the ask is structured).

## Techniques

| Technique | Use when | Watch out |
|---|---|---|
| Zero-shot | Well-scoped, low-stakes, simple format | Unreliable for domain formats |
| Few-shot (2-5 examples) | Output format keeps coming back wrong | Examples must be correct and diverse; best example last |
| Prompt chaining | Task too big for one prompt | Human checkpoint between steps; `/compact` between long chains |
| Chain of thought | Debugging, architecture, multi-step change | Ask it to reason before it edits |
| Tree of thought | Design choice with several viable options | Ask for pros, cons, complexity, then a recommendation |

## Templates

| Template | Parts | Use for |
|---|---|---|
| RTF | Role, Task, Format | Quick starting point |
| RTFC | RTF + Constraints | Controlling scope and length |
| RTCIF | Role, Task, Context, Input, Format (+ constraints) | Production-grade, critical tasks |
| CO-STAR | Context, Objective, Style, Tone, Audience, Response | Context-heavy writing and review |
| AUTOMAT | Act as, User context, Task, Output, Mode, Audience, Temperature cue | Pipelines, autonomous or CI steps |
| BRAIN | Background, Request, Action steps, Input, Notes | Enterprise research and comparisons |
| GIO | Goal, Inputs, Constraints, Output, Verify | Proposals, automation, real tasks |

## Seven principles

Be specific. Set a role. Define the format. Use examples. State constraints.
Go step by step. Iterate: prompts are code.

## Weak-to-strong pairs

| Weak | Strong |
|---|---|
| Fix the bug | Fix the KeyError in `user_service.py` line 42 when `user_id` is missing from the cache dict. |
| Write good code | Write clean Python 3.12. Type hints on all functions. No bare except. |
| Make it better | Refactor `auth.py` for readability. Keep the same signatures. No new dependencies. |
| Write a test | Write a pytest test for `UserService.create()`. Cover 201, 400, 422. |

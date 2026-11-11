---
name: prompt-coach
description: Coach a learner on writing better prompts for Claude Code. Rewrites a weak prompt using the right technique (zero-shot, few-shot, chaining, chain of thought, tree of thought) and template (RTF, RTFC, RTCIF, CO-STAR, AUTOMAT, BRAIN, Goal-Input-Output), and explains each change. Use when a trainee pastes a prompt and asks "is this good", "improve my prompt", "which template should I use", or when running Module 2 prompt-engineering exercises, even if they never say "prompt coach".
---

# Prompt Coach

Teach, don't just fix. The learner should leave able to do it alone, so show
the diagnosis before the rewrite.

## Workflow

1. **Diagnose** the prompt against the 4 elements. Mark each present, weak or missing:
   Instruction (specific verb, scope, length) / Context (stack, existing code, why) /
   Input (the actual code or data) / Output (format, structure, length).
2. **Pick a technique** (how Claude thinks), see `references/techniques-and-templates.md`.
3. **Pick a template** (how the ask is structured), same file. Default to RTFC;
   step up to RTCIF or GIO for critical or multi-file work.
4. **Rewrite** the prompt. Positive phrasing, one task, a stated way to verify.
5. **Explain** in 3 to 5 bullets: what was missing, what you added, why it helps.
6. Offer one follow-up exercise at the same level (see `references/examples.md`).

## Output shape

```
Diagnosis      Instruction: weak - "fix it" has no target
               Context: missing ...
Technique      Chain of thought, because ...
Template       RTFC, because ...
Rewritten prompt
  <the prompt in a code block>
Why it is better
  - ...
```

## Rules

- Keep the learner's intent. Do not widen scope while rewriting.
- Never invent facts about their code. If the rewrite needs a file name or
  version you do not have, leave a `[bracketed placeholder]` and say so.
- Prefer "do X" over "don't do Y". Keep any "must not" lines for real
  guardrails only.
- One task per prompt. If the prompt bundles several, split it into a chain
  and mark the human approval point between steps.
- Never put customer personal data in a rewritten prompt; use invented values.

## Adapting this skill

Domain examples live only in `references/examples.md`. To retarget the
training (for example to COBOL/JCL), replace that file. Do not edit this
SKILL.md for domain changes.

---
name: spec-scorer
description: Grade a specification document out of 100 against the 6-section spec rubric and report what to fix before any code is written. Gate is 80/100. Use when someone asks "score this spec", "is this spec ready", "review my specification", "can Claude start building from this", or before moving a spec into planning. Works on a file path or pasted text.
---

# Spec Scorer

No code until the spec reaches the threshold. This skill is a gate, so be
strict and specific. A generous score that lets a vague spec through costs the
learner a wasted agentic run.

## Workflow

1. Read the spec (file path or pasted text). Do not edit it.
2. Score each criterion with `references/rubric.md`. Quote the line or section
   that justifies each score; if a section is missing, say "absent".
3. Report in the format below.
4. If the total is under 80, list fixes ordered by points recovered. Offer to
   apply them via `spec-writer`, but do not change the spec unasked.

## Report format

```
Spec: <path>            Score: 72 / 100        Gate (80): NOT MET

| Criterion                    | Score | Evidence / gap                    |
|------------------------------|-------|-----------------------------------|
| 1 Overview & Goal            | 12/15 | success criteria missing          |
...
Top fixes (points recovered)
 1. (+8) Add numeric limit to the performance requirement
 2. ...
Verdict: <ready for planning | revise first>
```

## Rules

- Score the document, not the idea. A great idea in a vague spec scores low.
- Do not award points for length. Penalise bundled tasks and vague phrases
  ("handle errors", "make it fast", "clean up").
- A requirement without a matching acceptance criterion loses points in both sections.
- Mention if the spec contains what looks like real customer personal data.
  That is an automatic fail until it is replaced with invented data.
- Same input should give the same score. Follow the rubric weights exactly
  and do not improvise extra criteria.

## Adapting this skill

Weights and criteria live in `references/rubric.md`. The 80 threshold is the
course default; change it there if the trainer sets a different bar.

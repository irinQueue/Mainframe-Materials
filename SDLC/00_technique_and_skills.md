# 00 — Technique choice and skill map

## 1. Prompting techniques and templates

**Source note.** The HTML file in this folder (`Developer-and-Claude-Code-Workflow.html`) covers the seven SDLC phases, not prompting techniques. The techniques and templates come from the Module 2 deck (*Claude Code for Mainframe COBOL Developers*, slides 36–52).

| Kind | Name | Deck slide | Best for |
|---|---|---|---|
| Technique | Zero-shot | 37 | Quick, clear questions |
| Technique | Few-shot | 38 | Matching a format or style |
| Technique | Prompt chaining | 39 | Big tasks done in checked steps |
| Technique | Chain of Thought | 41 | Debugging, calculations |
| Technique | Tree of Thought | 42 | Choosing between designs |
| Template | RTF / RTFC / RTCIF | 46 | Everyday asks, focused asks, critical asks |
| Template | CO-STAR | 48 | When the audience matters |
| Template | AUTOMAT | 49 | Output read by a program |
| Template | BRAIN | 50 | Research and analysis |
| Template | Goal-Input-Output | 51 | Real code changes, with VERIFY |

### Chosen: Goal-Input-Output (slide 51)

**Why:** this demo ends in working, tested code. Goal-Input-Output is the only template with a built-in **VERIFY** line, so every phase must prove itself (tests run, criteria checked) before moving on. It matches the SDLC gates exactly. The same template is reused once per phase, which also shows prompt chaining in practice.

## 2. Skills in `.claude/skills` and the phase each one supports

| Skill | SDLC phase (this demo) | Used here? |
|---|---|---|
| session-init | Start, before Requirements | Yes |
| score-specs | A. Requirements (spec gate, 80+) | Yes |
| specs-code-relevance-audit | B. Design (validate before planning) | Yes |
| web-application | C. Implementation (web apps) | No: app is a CLI (see Design) |
| python-web-application | C. Implementation (Python web apps) | No: app is a CLI |
| java-web-application | C. Implementation (Java web apps) | No: Python chosen |
| java-17-web-application | C. Implementation (Java 17) | No |
| container-application | F. Deployment (Docker/Podman) | No: no container needed |
| elastic-beanstalk-application | F. Deployment (AWS) | No: no cloud, by rule |
| run-tests | D. Testing (after every code cycle) | Yes |
| test-web-application | D. Testing (web apps) | No: app is a CLI |
| pull-review | E. Review (Tech Lead PR comments) | Partly: no GitHub PR in this demo |
| push-to-github | F. Deployment (branch, PR, CI) | No remote: explained in phase F |
| update-specs | F. Documentation (sync spec after push) | Applied locally in phase F |

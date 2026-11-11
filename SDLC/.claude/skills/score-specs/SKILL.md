---
name: score-specs
description: "Score developer specifications against a completeness rubric before allowing Claude Code to generate any code. This skill MUST be triggered whenever a developer provides specifications, instructions, feature requests, or task descriptions. It evaluates specs across 5 categories (Task Definition, Technical Context, Expected Output, Constraints & Requirements, Edge Cases & Error Handling) and returns a score out of 100. If score < 80%, the developer must iterate on their specs before proceeding. Use this skill any time you see new specs, updated specs, or when the developer asks to 'score my specs', 'check my specs', 'rate my instructions', or 'are my specs good enough'."
---

# Specification Completeness Scoring Skill

## Purpose

Evaluate developer specifications against a standardized rubric to ensure they are complete enough for Claude Code to generate high-quality code with minimal iterations. This is the **quality gate** of the SDLC workflow.

**Goal: Score >= 80% before proceeding to code generation.**

---

## How to Use This Skill

When triggered (either automatically via claude.md or manually by the developer), do the following:

### Step 1: Receive the Specifications

Accept the developer's specifications as input. These may be:
- Free-form text describing a feature or fix
- A structured spec document
- A set of instructions or requirements
- A ticket or issue description

### Step 2: Evaluate Against the Rubric

Score each of the 5 categories below. For each category, evaluate the 4 sub-criteria and assign 0-5 points each (20 points max per category, 100 total).

### Step 3: Output the Results

Return the score in the following format:

```
╔══════════════════════════════════════════════════════════════╗
║                 SPECIFICATION SCORE REPORT                   ║
╠══════════════════════════════════════════════════════════════╣
║  Overall Score: XX/100    Status: [PASS ✅ / FAIL ❌]       ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  1. Task Definition:             XX/20 [██████░░░░]          ║
║  2. Technical Context:           XX/20 [████████░░]          ║
║  3. Expected Output:             XX/20 [████░░░░░░]          ║
║  4. Constraints & Requirements:  XX/20 [██████████]          ║
║  5. Edge Cases & Error Handling: XX/20 [██░░░░░░░░]          ║
║                                                              ║
╠══════════════════════════════════════════════════════════════╣
║  Action: [Submit with confidence / Fill gaps / Rework]       ║
╚══════════════════════════════════════════════════════════════╝
```

Then provide detailed feedback for each category.

---

## THE RUBRIC

### Category 1: TASK DEFINITION (20 points)

| Criteria | Points | What to Look For |
|----------|--------|------------------|
| **What** - Clear action verb | 0-5 | Does it use a clear action verb? (build, fix, refactor, add, create, migrate, implement) A vague "make it better" scores 0. "Refactor the login flow to use JWT" scores 5. |
| **Scope** - Boundaries defined | 0-5 | Are boundaries explicit? What's included AND excluded? "Don't modify the registration flow" is good scope definition. |
| **Why** - Context/purpose | 0-5 | Is there context on WHY this change is needed? Business reason, bug description, performance issue? |
| **Single responsibility** | 0-5 | Is this ONE coherent task? Multiple bundled tasks (build auth AND redesign dashboard) score low. |

**Weak example:** "Make the auth better"
**Strong example:** "Refactor the login flow to use JWT tokens instead of session cookies. Don't modify the registration flow. This is needed because session cookies don't work well with our new mobile app."

### Category 2: TECHNICAL CONTEXT (20 points)

| Criteria | Points | What to Look For |
|----------|--------|------------------|
| **Stack/Framework** | 0-5 | Are languages, frameworks, and versions mentioned? "Spring Boot 3.x with Java 17" scores high. |
| **File locations** | 0-5 | Are relevant paths or target locations specified? "Changes go in `src/auth/`" scores high. |
| **Dependencies** | 0-5 | Are existing libraries to use (or avoid) mentioned? "Use the existing `jjwt` library" scores high. |
| **Architecture patterns** | 0-5 | Are codebase conventions referenced? "Follow the repository pattern in `src/repositories/`" scores high. |

**Weak example:** "Add a database"
**Strong example:** "Add PostgreSQL integration using Prisma ORM. Follow the existing repository pattern in `src/repositories/`. Use the connection string from `DATABASE_URL` env var."

### Category 3: EXPECTED OUTPUT (20 points)

| Criteria | Points | What to Look For |
|----------|--------|------------------|
| **Deliverable format** | 0-5 | What files/changes are expected? "Create a new service class and update the controller" is clear. |
| **Behavior description** | 0-5 | What should happen when it works? "User should receive a JWT token in the response body" is clear. |
| **Interface/API shape** | 0-5 | Are function signatures, endpoints, props defined? `POST /api/auth/login → { token: string, expiresIn: number }` scores high. |
| **Example usage** | 0-5 | Is there an example of how the code will be called/used? Concrete examples score highest. |

**Weak example:** "Create a utility function"
**Strong example:** "Create `parseCSV(filePath: string): Promise<Record<string, string>[]>` in `src/utils/csv.ts`. Should handle quoted fields and return empty array for empty files."

### Category 4: CONSTRAINTS & REQUIREMENTS (20 points)

| Criteria | Points | What to Look For |
|----------|--------|------------------|
| **Must-haves** | 0-5 | Are non-negotiable requirements listed? "Must support multi-tenancy" is a clear must-have. |
| **Must-not-haves** | 0-5 | Are things to explicitly avoid stated? "Don't add new dependencies" or "Don't break existing API contracts." |
| **Performance/limits** | 0-5 | Are size, speed, memory constraints defined? "Must handle 100MB files without loading into memory." |
| **Compatibility** | 0-5 | Are browser/runtime/OS requirements stated? "Must work in Node 18+." |

**Weak example:** "Make it fast"
**Strong example:** "Must handle files up to 100MB without loading entirely into memory. Don't use any dependencies not already in package.json. Must work in Node 18+."

### Category 5: EDGE CASES & ERROR HANDLING (20 points)

| Criteria | Points | What to Look For |
|----------|--------|------------------|
| **Invalid inputs** | 0-5 | What happens with bad data? Is behavior defined for malformed input? |
| **Empty/null cases** | 0-5 | What happens with missing data? "Return null if user not found" is explicit. |
| **Failure modes** | 0-5 | How to handle errors? Throw, return default, log, retry? |
| **Boundary conditions** | 0-5 | Are min/max values and limits addressed? |

**Weak example:** "Handle errors"
**Strong example:** "Throw `ValidationError` for malformed input. Return `null` if user not found (don't throw). Log network errors to stderr but retry 3x before failing."

---

## SCORING GUIDE

| Score | Readiness | Action |
|-------|-----------|--------|
| 90-100 | ✅ Excellent | Proceed to Plan Mode with confidence |
| 80-89 | ✅ Good | Proceed to Plan Mode, expect minor clarifications |
| 60-79 | ⚠️ Incomplete | Show gaps, ask developer to fill them before proceeding |
| 40-59 | ❌ Vague | Significant rework needed, highlight all weak categories |
| 0-39 | ❌ Idea only | Needs full specification, walk developer through each category |

---

## SCORING RULES

1. **Be fair but firm.** Don't inflate scores to let specs pass. The goal is to reduce iterations later.

2. **Give partial credit.** If a criterion is partially addressed, give 2-3 points instead of 0 or 5.

3. **Context matters.** A simple bug fix doesn't need the same level of detail as a new feature. Adjust expectations:
   - **Bug fix:** Task Definition and Expected Output are most important
   - **New feature:** All categories carry equal weight
   - **Refactor:** Technical Context and Constraints are most important

4. **Provide actionable feedback.** For every criterion that scores below 4, provide a specific suggestion for improvement. Don't just say "needs more detail" — say exactly what detail is missing.

5. **Show examples.** When suggesting improvements, show what a strong version of that section would look like for their specific case.

---

## IMPROVEMENT SUGGESTIONS FORMAT

When specs score below 80%, provide feedback like this:

```
### Areas to Improve:

**Task Definition (12/20)** — Missing scope boundaries
→ Suggestion: Add what's explicitly OUT of scope. For example:
  "This change should NOT affect the existing user profile endpoints."

**Edge Cases (8/20)** — No error handling defined  
→ Suggestion: Define what happens when:
  - The input file is empty
  - The database connection fails
  - The user provides invalid format
  
### Quick Fix Template:
[Provide a template the developer can fill in to address gaps]
```

---

## SESSION STATE UPDATES

Every scoring run — first attempt or any re-score — appends one entry to `spec_score_history`:

```yaml
spec_score_history:
  - { score: 64, timestamp: "<ISO-8601>" }
  - { score: 78, timestamp: "<ISO-8601>" }
  - { score: 86, timestamp: "<ISO-8601>" }   # final accepted
```

Set `spec_score` only when a run scores ≥ 80 and the developer proceeds to Phase 2. The history field is read by `push-to-github` so the panel can see whether the developer cleared the gate on first try or iterated — both are valid; the data tells the story.

**Do not skip the history append on re-scores.** A score of 88 with no history reads to the panel as "passed first try"; a score of 88 with three history entries reads as "iterated thoughtfully on the spec." These are different kinds of evidence and both belong on the PR.

---

## RE-SCORING

When the developer submits revised specifications:
1. Re-run the full rubric (don't just re-score changed sections)
2. Append the new score to `spec_score_history` (mandatory)
3. Show the before/after comparison
4. Highlight what improved and what still needs work
5. If now >= 80%, set `spec_score`, congratulate, and proceed to Phase 2
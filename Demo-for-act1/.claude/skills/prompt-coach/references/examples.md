# Domain examples (SWAP THIS FILE to retarget the training)

Currently the generic examples from the course PDF (Python / Django / To-Do API).
When training mainframe developers, replace the examples below with COBOL, JCL,
copybook and VSAM equivalents. Keep the same structure: weak prompt, strong
prompt, what changed.

## Example 1: bug fix
Weak: `Fix the login bug`
Strong (RTFC):
```
Role: Senior Python developer.
Task: Fix the AttributeError in apps/auth/views.py when an anonymous user hits /api/profile/.
Format: Show the diff only, then one sentence on root cause.
Constraints: Do not change the public serializer. Existing tests must still pass.
```

## Example 2: chain of thought
```
Before writing any code, think step by step about what could make login()
return None when valid credentials are provided. Then fix the root cause.
```

## Example 3: tree of thought
```
I need rate limiting for a FastAPI app under 1000 requests/day.
Explore three approaches: A) Redis + slowapi, B) in-memory dict with TTL,
C) DB counter. For each give pros, cons, complexity. Then recommend one.
```

## Practice exercise
You are building a To-Do REST API. Write the prompt that adds "mark task as
complete". Use /plan mode. State stack, conventions and what "done" means.

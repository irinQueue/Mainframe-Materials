---
name: run-tests
description: "Run unit tests and integration tests after every code generation cycle. This skill MUST be triggered automatically after Claude Code generates or modifies any code. It detects the project's testing framework, runs the appropriate test commands, parses results, and presents a clear pass/fail report. Use this skill whenever code has been generated, modified, or refactored — even for small changes. Also trigger when the developer says 'run tests', 'test this', 'check if it works', 'did the tests pass', or any variation. Never skip this skill between code generation and developer review."
---

# Run Tests Skill

## Purpose

Automatically run the project's unit tests and integration tests after every code generation cycle. This is a mandatory guardrail — no code should be presented to the developer as "ready" without test results.

---

## Workflow

### Step 1: Detect the Testing Framework

Inspect the project to determine which test framework(s) are in use:

```bash
# Check for common test configuration files and dependencies
ls -la package.json pom.xml build.gradle pyproject.toml setup.cfg pytest.ini tox.ini Makefile 2>/dev/null
```

**Detection rules:**

| Indicator | Framework | Test Command |
|-----------|-----------|--------------|
| `package.json` with jest/vitest/mocha | Node.js test runner | `npm test` or `npx jest` or `npx vitest run` |
| `pom.xml` (Maven) | JUnit / Maven Surefire | `mvn test` |
| `build.gradle` (Gradle) | JUnit / Gradle | `./gradlew test` |
| `pytest.ini` or `pyproject.toml` with pytest | pytest | `pytest -v` |
| `setup.cfg` with test config | pytest or unittest | `python -m pytest -v` |
| `manage.py` (Django) | Django TestCase | `python manage.py test` |
| `tox.ini` | tox | `tox` |
| `Makefile` with test target | Custom | `make test` |

If multiple frameworks are detected, run all of them and report results separately.

If no framework is detected, inform the developer:
> "No test framework detected. Would you like me to set up tests? I can configure [pytest/JUnit/Jest] based on your project stack."

### Step 2: Determine Test Scope

Decide what tests to run based on what changed:

**After initial code generation:**
- Run ALL tests (unit + integration) to check for regressions

**After an iteration/fix:**
- Run tests related to the changed files first (fast feedback)
- Then run the full suite to check for regressions

**Scope detection:**
```bash
# Find which files changed
git diff --name-only HEAD

# Map changed files to their test files
# Convention patterns:
#   src/auth/login.ts      → tests/auth/login.test.ts
#   src/main/java/.../Service.java → src/test/java/.../ServiceTest.java
#   app/models/user.py     → tests/test_user.py
```

### Step 3: Run Unit Tests

Execute the appropriate test command:

**Node.js (Jest/Vitest):**
```bash
# Run with verbose output and coverage
npx jest --verbose --coverage 2>&1
# OR
npx vitest run --reporter=verbose 2>&1
```

**Java (Maven):**
```bash
# Unit tests only (skip integration)
mvn test -Dtest='!*IntegrationTest,!*IT' -pl <module> 2>&1
```

**Java (Gradle):**
```bash
./gradlew test --info 2>&1
```

**Python (pytest):**
```bash
# Unit tests (exclude integration markers)
pytest -v --tb=short -m "not integration" 2>&1
```

**Django:**
```bash
python manage.py test --verbosity=2 2>&1
```

Capture the full output including exit code.

### Step 4: Run Integration Tests

After unit tests pass (or in parallel if the framework supports it):

**Node.js:**
```bash
npx jest --testPathPattern='integration|e2e' --verbose 2>&1
```

**Java (Maven):**
```bash
mvn verify -Dtest='*IntegrationTest,*IT' 2>&1
# OR if using failsafe plugin:
mvn failsafe:integration-test failsafe:verify 2>&1
```

**Python (pytest):**
```bash
pytest -v --tb=short -m "integration" 2>&1
```

**Django:**
```bash
python manage.py test --tag=integration --verbosity=2 2>&1
```

If integration tests require external services (database, API), check if they're available first:
```bash
# Check if Docker is running for test containers
docker info >/dev/null 2>&1 && echo "Docker available" || echo "Docker not available"

# Check if test database is accessible
# (framework-specific)
```

If external services are unavailable, skip integration tests and note it in the report.

### Step 5: Parse and Present Results

Parse the test output and present a clear report:

```
╔════════════════════════════════════════════════════════════════╗
║                          TEST RESULTS                          ║
╠════════════════════════════════════════════════════════════════╣
║                                                                ║
║  Unit Tests:        ✅ PASSED  (24/24)                         ║
║  Integration Tests: ⚠️ PARTIAL (8/10 — 2 skipped)              ║
║  Coverage:          78.3%                                      ║
║                                                                ║
╠════════════════════════════════════════════════════════════════╣
║  Duration: 12.4s                                               ║
║  Framework: pytest 7.4.0                                       ║
╚════════════════════════════════════════════════════════════════╝
```

**If tests PASS:**
- Show the summary above
- Note any warnings or skipped tests
- Proceed with developer review

**If tests FAIL:**
- Show the summary with failure count
- List each failing test with:
  - Test name and file location
  - Error message / assertion failure
  - Relevant stack trace (truncated to key lines)
- Suggest fixes for each failure
- Ask: "Would you like me to fix these failures?"

**Failure report format:**
```
❌ FAILURES (3):

1. test_login_with_invalid_token (tests/auth/test_login.py:45)
   AssertionError: Expected 401, got 500
   → Likely cause: Missing error handler for expired tokens
   → Suggested fix: Add try/catch in token validation middleware

2. test_user_creation_duplicate (tests/models/test_user.py:78)
   IntegrityError: duplicate key value violates unique constraint
   → Likely cause: Test setup not cleaning up previous test data
   → Suggested fix: Add setUp/tearDown to reset test database

3. TestPaymentProcessing.test_refund (tests/integration/test_payments.py:120)
   ConnectionError: Could not connect to payment gateway mock
   → Likely cause: Mock server not started
   → Suggested fix: Check test fixtures for mock server setup
```

### Step 6: Handle Test Failures

If tests fail, offer the developer options:

1. **Auto-fix:** "I can attempt to fix these failures automatically"
2. **Fix specific:** "Which failures should I address?"
3. **Skip and note:** "Continue to review with known failures (not recommended)"

If auto-fixing, after generating fixes:
- **Re-run this skill** (recursive — run tests again after fixes)
- Track the fix as an additional iteration in the changes_log

---

## SPECIAL CASES

### No Existing Tests
If the generated code has no corresponding tests:
1. Inform the developer: "No tests exist for the generated code."
2. Offer to generate tests: "Would you like me to create unit tests for the new code?"
3. If yes, generate tests following the project's existing test patterns and conventions
4. Run the newly created tests

### Flaky Tests
If a test fails intermittently:
1. Re-run the specific failing test up to 2 additional times
2. If it passes on retry, flag it as flaky in the report:
   ```
   ⚠️ FLAKY: test_concurrent_access (passed on retry 2/3)
   ```
3. Don't block the workflow for flaky tests, but note them

### Long-Running Tests
If tests take longer than 120 seconds:
1. Show a progress indicator if possible
2. Run unit tests first (fast feedback)
3. Run integration tests in parallel if the framework supports it
4. If integration tests exceed 300 seconds, offer to skip them:
   > "Integration tests are taking a long time. Skip them for now and run manually later?"

---

## SESSION STATE UPDATE

After running tests, update the session state in two places:

**1. Last test run snapshot (ephemeral — overwritten each cycle):**

```yaml
last_test_run:
  unit_tests: { passed: N, failed: N, skipped: N }
  integration_tests: { passed: N, failed: N, skipped: N }
  coverage: "XX%"
  duration: "Xs"
  all_passed: true/false
```

**2. Cumulative verification counters (mandatory — never reset):**

Increment `verification_runs` by 1 every time this skill executes (regardless of pass or fail). If `all_passed` is `false`, also increment `verification_failures_before_pass` by 1.

```yaml
verification_runs: <previous + 1>
verification_failures_before_pass: <previous + (0 if all_passed else 1)>
```

These counters are read by `push-to-github` for the PR analytics block. Do not reset them when tests subsequently pass — a high `verification_failures_before_pass` is positive evidence (Category D in the rubric: "identification, validation, and correction of issues") that the developer caught and fixed problems before opening the PR. The panel cares about the catch-rate, not a clean history.
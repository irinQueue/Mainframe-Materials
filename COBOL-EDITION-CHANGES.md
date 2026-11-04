# COBOL edition: what changed from the original deck

File: `Claude Code for Mainframe COBOL Developers.pptx` (72 slides, editable, 16:9).
The original `Claude Code for Developers.pdf` is untouched. The deck is rebuilt from
scratch in a similar dark style, not edited from the Canva file, so the look is close but
not identical. Generator: `cobol-deck/` (`node build.js`, needs pptxgenjs).

## Kept as in the original (generic)
Account setup, Git and Claude Code install, PATH, first session (only the example folder
changed to `ledger-me`), what Claude Code is, tools reference, model tiers, tokens and
context, PACT theory, skills, commands, agents and MCP, prompt theory, techniques vs
templates, optimization, the 5 spec categories, the pre-flight checklist, the 6-phase SDLC.

## Rewritten with COBOL / LEDGER-ME examples
PACT example and practice, CLAUDE.md slides, custom command (now `/cobol-review`),
prompt anatomy, zero-shot, few-shot (abend and file-status classifier), chaining, chain of
thought (the ROUNDED and signed-field defects), tree of thought (dormant-account date
logic), best practices, RTF/RTFC/RTCIF, CO-STAR, AUTOMAT, BRAIN, GIO, the spec example
(now CR-2026-014), the writing-specs activity, and the capstone lab.

## New slides (not in the original)
- Your Mainframe Training Environment (Module 0)
- The LEDGER-ME Capstone scenario
- Capstone: 10 Days at 90 Minutes
- Capstone: Value Scoreboard and Retrospective

## Changes to facts you should check
- **Model IDs** now read `claude-opus-5-5`, `claude-sonnet-5-5`, `claude-haiku-5-5` everywhere.
  The original quick-reference card said `4-6` while the model slide said `5-5`.
- **Capstone slide** said "Module 10". It now says Module 04.
- **Auto-compaction** claim "fires at 100,000 tokens by default" is replaced with a softer
  statement. I could not verify the number.
- **Token example** "100-line code file ~700 tokens" is kept but marked "varies by language".
  COBOL token counts were not measured.
- **Install command** is kept from the original. The Step 3 slide (curl installer) and the
  quick-reference card (`npm i -g ...`) disagree. A note on the card asks you to check.
- **Spec example score**: the original said "Score-ready ~92/100". The CR-2026-014 spec has
  not been run through spec-scorer, so the slides say "not yet scored".
- **Skill names** on the 6-phase slide (score-specs, specs-code-relevance-audit,
  push-to-github, update-specs, pull-review) are the original organisation's. They were not
  checked. `test-web-application` was replaced by "regression harness and oracle checks".
- **AI Usage Policy** slide has a placeholder for your organisation's policy. The one line
  about customer data is from the capstone rules.
- **Example constraint** "no intrinsic functions" on the BRAIN slide is illustrative only.

## Not done
- The deck was **not rendered or opened in PowerPoint**. This PC has no renderer, so text fit
  was checked by an estimate in the build script (0 warnings) and the file passes the
  package validator. Open it and page through before use.
- Slide text sizes are 10.5 to 14 pt in dense slides. A few are below the usual 14 pt body size.
- No speaker notes.

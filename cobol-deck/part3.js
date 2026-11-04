// Part 3: spec example (CR-2026-014), Module 03 workflow, Module 04 capstone, quick reference.
const { COL, content, section, txt, box, badge, pill, banner, code } = require('./lib');
const { steps, table, titled } = require('./helpers');

const SPEC_FOOT = 'Feature Specification: CR-2026-014 · not yet scored: run spec-scorer first (gate 80/100)';

module.exports = function part3(pres) {
  // ---- spec example title
  section(pres, 'SPECIFICATION EXAMPLE · LEDGER-ME COBOL', 'CR-2026-014',
    'Maintenance fee, dormant accounts and a control report for the LEDGER-ME month-end batch.',
    ['GnuCOBOL 3.2 locally, Enterprise COBOL on z/OS later', 'Fixed format, DD-name file mapping', 'Python oracle for the tests', 'Not yet scored: run spec-scorer (gate 80)'], COL.orange);

  // ---- task definition and technical context
  {
    const s = content(pres, 'Spec Example: 1 Overview & Goal, 2 Technical Context', 'Module 02');
    titled(s, 0.5, 1.25, 6.0, 4.9, '1  Overview & Goal',
      'What we are building:\nA monthly maintenance fee, a dormant-account rule and a reconciliation control report for the LEDGER-ME month-end batch, plus fixes for the defects found in docs/business-rules.md.\n\nWhy now:\nOperations needs the fee and dormant handling for the November statement run, and cannot trust the reject file or the totals until the control report proves they agree.\n\nSuccess looks like:\n13 accounts pay the fee (65.00 total), 7 accounts are flagged DORMANT with 0.00 interest, and the control report says IN BALANCE.', COL.teal, { size: 12.5, gap: 2 });
    txt(s, '2  Technical Context', 6.8, 1.25, 6, 0.4, { size: 16, bold: true, color: COL.teal });
    table(s, [['Item', 'Value'],
      ['Language', 'COBOL, fixed format. GnuCOBOL 3.2 locally, Enterprise COBOL on z/OS later'],
      ['Create', 'data/PARMS.DAT'],
      ['Modify', 'ACCTREC.cpy, ACCTUPD.cbl, INTCALC.cbl, STMTRPT.cbl, pipeline.sh'],
      ['Pattern', 'DD-name file mapping; numbered paragraphs; PERFORM ... THRU as in INTCALC'],
      ['Record length', 'ACCTREC stays 60 bytes. New fields come out of the filler'],
      ['Tests', 'Day 3 regression harness plus a check per requirement']],
      6.8, 1.75, [1.5, 4.53], { size: 12, rowH: 0.7, boldCol: 0 });
    txt(s, SPEC_FOOT, 0.5, 6.55, 12.3, 0.35, { size: 11, color: COL.muted });
  }

  // ---- functional requirements
  {
    const s = content(pres, 'Spec Example: 3 Functional Requirements', 'Module 02');
    const r = [
      ['Parameter file', 'data/PARMS.DAT is one 40-byte record: threshold 9(7)V99, fee 9(5)V99, as-of date CCYYMMDD, 16 spaces.'],
      ['Parameter errors', 'INTCALC reads PARMIN once. Missing or non-numeric: end with return code 12 and a message.'],
      ['Fee rule', 'An active account with a balance under the threshold pays the fee, negative and dormant accounts included. Closed accounts do not.'],
      ['New fields', 'ACCTREC gains ACCT-FEE S9(5)V99 and ACCT-FLAG X, taken from the filler. INTCALC sets both for every account.'],
      ['Dormant test', 'Active and last activity before the as-of date minus one year. YYMMDD: a year above 50 means 19YY, else 20YY.'],
      ['Dormant effect', 'A dormant account earns no interest and gets flag D.'],
      ['Statement', 'STMTRPT shows the fee, prints DORMANT, and adds a line with total fees and the dormant count.'],
      ['Control report', 'ACCTUPD writes CONTROL.RPT: records and transactions read, posted, rejected and written, plus balances before and after.'],
      ['Reconciliation', 'IN BALANCE only when the figures agree. Otherwise OUT OF BALANCE and return code 8.'],
      ['Defects', 'Fix D1 to D6 from docs/business-rules.md. Each fix has a test and a line in docs/defect-log.md.'],
    ];
    const cs = [COL.purple, COL.teal, COL.orange, COL.cyan, COL.green];
    r.forEach((k, i) => {
      const col = Math.floor(i / 5), row = i % 5;
      const x = 0.5 + col * 6.25, y = 1.2 + row * 1.04;
      box(s, x, y, 6.08, 0.97, { fill: COL.panel });
      badge(s, String(i + 1), x + 0.1, y + 0.12, 0.42, cs[i % 5]);
      txt(s, k[0], x + 0.65, y + 0.03, 5.3, 0.3, { size: 12.5, bold: true });
      txt(s, k[1], x + 0.65, y + 0.32, 5.3, 0.62, { size: 11, color: COL.muted });
    });
    txt(s, SPEC_FOOT, 0.5, 6.5, 12.3, 0.35, { size: 11, color: COL.muted });
  }

  // ---- NFR and out of scope
  {
    const s = content(pres, 'Spec Example: 4 Non-Functional, 5 Out of Scope', 'Module 02');
    txt(s, '4  Non-Functional Requirements', 0.5, 1.25, 6, 0.4, { size: 16, bold: true, color: COL.teal });
    [['Return codes', '0 normal, 8 out of balance, 12 I/O or parameter error. A non-zero code stops the rest of the job.'], ['No hard-coding', 'Fee threshold, fee amount and as-of date come only from PARMS.DAT.'],
      ['Data', 'Invented data only. No real customer information anywhere.'], ['Style', 'Match the existing code. Every OPEN and WRITE in the programs you change checks file status.']].forEach((k, i) => {
      titled(s, 0.5, 1.75 + i * 1.15, 6.0, 1.1, k[0], k[1], COL.teal, { size: 12, tsize: 13.5 });
    });
    txt(s, '5  Out of Scope', 6.9, 1.25, 6, 0.4, { size: 16, bold: true, color: COL.red });
    [['Posting to the balance', 'Posting the fee or interest to the account balance (not done today for interest either).'], ['29 February', 'As-of dates of 29 February.'],
      ['Parameterising rates', 'Moving the interest rates or the savings bonus into a parameter file.'], ['z/OS port', 'Porting to z/OS (Day 9).']].forEach((k, i) => {
      titled(s, 6.9, 1.75 + i * 1.15, 5.93, 1.1, '✗  ' + k[0], k[1], COL.red, { size: 12, tsize: 13.5 });
    });
    txt(s, SPEC_FOOT, 0.5, 6.4, 12.3, 0.35, { size: 11, color: COL.muted });
  }

  // ---- acceptance criteria
  {
    const s = content(pres, 'Spec Example: 6 Acceptance Criteria', 'Module 02');
    txt(s, 'Definition of done. Claude self-checks against every item before considering the task complete.', 0.5, 1.2, 12.3, 0.4, { size: 13, color: COL.muted });
    const r = [
      'Changing the fee amount in PARMS.DAT changes the statement with no recompile.',
      'ACCT000016 (-250.00) is charged the fee. ACCT000040 (closed) is not.',
      'ACCT000030 to ACCT000036 are flagged DORMANT with 0.00 interest, including the two 1999 dates.',
      'ACCT000017 interest is 1.63. ACCT000010 is 1.25. ACCT000011 is 20.83.',
      'ACCT000016 balance is -250.00.',
      'REJECTS.DAT has one line for every rejected transaction (153).',
      'Control report: 200 read, 200 written, 980 read, 827 posted, 153 rejected, IN BALANCE.',
      'An unwritable MASTOUT ends ACCTUPD with return code 12 and INTCALC does not run.',
      'A missing PARMS.DAT ends INTCALC with return code 12.',
      'Day 3 regression differences appear only in files this spec changes.',
    ];
    r.forEach((t, i) => {
      const col = Math.floor(i / 5), row = i % 5;
      const x = 0.5 + col * 6.25, y = 1.75 + row * 0.95;
      box(s, x, y, 6.08, 0.87, { fill: COL.panel });
      txt(s, '☐', x + 0.1, y, 0.45, 0.87, { size: 18, color: COL.green, valign: 'middle', align: 'center' });
      txt(s, t, x + 0.6, y, 5.35, 0.87, { size: 12, valign: 'middle' });
    });
    txt(s, SPEC_FOOT, 0.5, 6.55, 12.3, 0.35, { size: 11, color: COL.muted });
  }

  // ---- module 3 divider
  section(pres, 'MODULE 03', 'Claude Code in Our SDLC', 'How we operationalise Claude Code as a structured, auditable six-phase workflow.',
    ['Score the spec', 'Validate against existing code', 'Plan and approve', 'Build and test', 'Push', 'Review'], COL.cyan);

  // ---- six phases
  {
    const s = content(pres, 'The Six-Phase SDLC Workflow', 'Module 03');
    const c = [
      ['1', 'Score specs', 'Score 80 or more required', 'The score-specs skill evaluates spec quality. No code until the threshold is met.', COL.purple],
      ['2', 'Validate', 'No duplicate work', 'specs-code-relevance-audit classifies every requirement against the existing code.', COL.teal],
      ['3', 'Plan', 'Explicit approval required', 'Claude presents an implementation plan. No code generation until approved.', COL.orange],
      ['4', 'Build & test', 'Tests pass every cycle', 'Run the regression harness and oracle checks after every codegen cycle. No exceptions.', COL.cyan],
      ['5', 'Push', 'Annotated PR created', 'push-to-github creates a labelled PR. update-specs syncs the spec document.', COL.green],
      ['6', 'Review', 'Tech Lead reviews', 'pull-review fetches and categorises PR comments for the next iteration.', COL.red],
    ];
    c.forEach((k, i) => {
      const x = 0.5 + (i % 3) * 4.18, y = 1.3 + Math.floor(i / 3) * 2.55;
      box(s, x, y, 3.95, 2.4, { fill: COL.panel });
      badge(s, k[0], x + 0.15, y + 0.15, 0.55, k[4]);
      txt(s, k[1], x + 0.85, y + 0.15, 2.95, 0.55, { size: 17, bold: true, valign: 'middle' });
      txt(s, k[2], x + 0.15, y + 0.85, 3.65, 0.4, { size: 13.5, bold: true, color: k[4] });
      txt(s, k[3], x + 0.15, y + 1.3, 3.65, 1.0, { size: 12.5, color: COL.muted });
    });
  }

  // ---- activity: write specs
  {
    const s = content(pres, 'Writing Specifications — Add Features to LEDGER-ME', 'Module 02');
    box(s, 0.5, 1.2, 6.08, 0.95, { fill: COL.panel });
    txt(s, 'YOUR EXISTING SYSTEM', 0.65, 1.22, 5.8, 0.3, { size: 11, bold: true, color: COL.teal, cs: 2 });
    txt(s, 'LEDGER-ME with the fee, dormant rule and control report', 0.65, 1.5, 5.8, 0.6, { size: 13, bold: true });
    box(s, 6.75, 1.2, 6.08, 0.95, { fill: COL.panel });
    txt(s, 'NEW FEATURES TO SPEC', 6.9, 1.22, 5.8, 0.3, { size: 11, bold: true, color: COL.orange, cs: 2 });
    txt(s, 'OVERLMT reject reason · Page totals on the statement', 6.9, 1.5, 5.8, 0.6, { size: 13, bold: true });
    txt(s, 'Write ONE combined specification covering both features, using the 5-category framework you just learned.', 0.5, 2.25, 12.3, 0.4, { size: 13, color: COL.muted });
    const c = [
      ['1', 'Task Definition', '"Add OVERLMT reject and page totals to STMTRPT. No new files."', COL.purple],
      ['2', 'Technical Context', '"Follow the reject-reason pattern in ACCTUPD 3500-REJECT."', COL.teal],
      ['3', 'Expected Output', '"REJECTS.DAT shows reason OVERLMT. STMT.RPT shows page totals."', COL.orange],
      ['4', 'Constraints', '"No new copybooks. Record stays 60 bytes. Fixed format."', COL.cyan],
      ['5', 'Edge Cases','"Exactly at the limit is allowed. Return code 12 on I/O error."', COL.green],
    ];
    c.forEach((k, i) => {
      const x = 0.5 + i * 2.5;
      box(s, x, 2.8, 2.38, 3.1, { fill: COL.panel });
      badge(s, k[0], x + 0.12, 2.9, 0.42, k[3]);
      txt(s, k[1], x + 0.62, 2.9, 1.7, 0.42, { size: 12.5, bold: true, valign: 'middle' });
      txt(s, k[2], x + 0.12, 3.5, 2.15, 2.3, { size: 12, italic: true, color: COL.cyan });
    });
    txt(s, 'Write the spec yourself · run the pre-flight checklist · target score 80 / 100 · time box: 15 min', 0.5, 6.15, 12.3, 0.4, { size: 13, color: COL.muted });
  }

  // ---- AI usage policy
  section(pres, 'MODULE 03', 'AI Usage Policy', '[Facilitator: insert your organisation’s AI usage policy on this slide.]',
    ['No customer personal data in any file, prompt, log or screenshot. This course uses invented data only.', 'Review everything Claude writes before it reaches shared code.', 'Treat Claude’s statements about business rules as unverified until you check them against the code and the data.'], COL.cyan);

  // ---- capstone divider
  section(pres, 'MODULE 04', 'Capstone', 'Everything comes together. Change a real batch system end to end with the complete Claude Code workflow.',
    ['Inherit', 'Understand', 'Change', 'Prove'], COL.red);

  // ---- NEW: the LEDGER-ME scenario
  {
    const s = content(pres, 'The LEDGER-ME Capstone: Inherit, Understand, Change, Prove', 'Module 04');
    titled(s, 0.5, 1.25, 6.0, 2.2, 'The scenario',
      'You have just joined the team that owns LEDGER-ME, a month-end batch for a small retail bank. It is 20+ years old. The original developers have left, documentation is almost nonexistent and names are cryptic. Operations has raised change request CR-2026-014.', COL.red, { size: 12.5 });
    table(s, [['Program', 'Job'], ['ACCTUPD', 'Applies the daily transactions to the account master. Writes rejects.'], ['INTCALC', 'Calculates monthly interest by balance tier.'], ['STMTRPT', 'Prints the statement report.']],
      0.5, 3.65, [1.5, 4.5], { size: 12, rowH: 0.62, mono: [0], boldCol: 0 });
    txt(s, 'Copybooks ACCTREC and TRANREC hold the record layouts. All data is invented.', 0.5, 6.3, 6.0, 0.55, { size: 11.5, color: COL.muted });
    txt(s, 'Change request CR-2026-014', 6.9, 1.25, 6, 0.4, { size: 16, bold: true, color: COL.red });
    [['Monthly maintenance fee', 'Accounts under a threshold are charged. Amount and threshold come from a parameter file.'], ['Dormant accounts', 'No transaction in 12 months: no interest and flagged DORMANT on the statement.'],
      ['Control report', 'Records read, written, rejected and balance totals. In must equal out plus rejects.'], ['Defects', 'Fix every defect you find. Each fix gets a test and a one-line defect-log entry.']].forEach((k, i) => {
      titled(s, 6.9, 1.75 + i * 1.18, 5.93, 1.08, (i + 1) + '  ' + k[0], k[1], COL.orange, { size: 12, tsize: 13.5 });
    });
    banner(s, 'Rules: no code before the spec scores 80 or more and you have approved a plan. Verify every claim Claude makes.', COL.teal);
  }

  // ---- NEW: 10-day plan
  {
    const s = content(pres, 'Capstone: 10 Days at 90 Minutes', 'Module 04');
    table(s, [['Day', 'Focus', 'Deliverable'],
      ['1', 'Setup and orient', 'CLAUDE.md, docs/overview.md, estimate log started'],
      ['2', 'Reverse-engineer', 'docs/business-rules.md, data-flow.md, verified-rules table'],
      ['3', 'Baseline', 'tests/run_all.sh and the golden master, passing baseline'],
      ['4', 'Specify', 'specs/cr-2026-014.md scoring 80 or more'],
      ['5', 'Plan and approve', 'docs/plan.md with approval note and a rejected alternative'],
      ['6', 'Build part 1', 'Fee feature and parameter file working, tests green'],
      ['7', 'Build part 2', 'Dormant logic and control report working, tests green'],
      ['8', 'Hunt defects', 'docs/defect-log.md, new tests, review notes'],
      ['9', 'Prove and harden', 'Custom command, zos-differences.md, updated CLAUDE.md (JCL is a stretch)'],
      ['10', 'Demo and retrospective', 'Demo, value scoreboard, docs/retrospective.md']],
      0.5, 1.25, [0.8, 3.0, 8.53], { size: 12.5, rowH: 0.47, boldCol: 1 });
    txt(s, 'Catch-up: each day has a tagged checkpoint. If you fall behind, check out the previous day’s tag and continue.', 0.5, 6.35, 12.3, 0.45, { size: 13, color: COL.orange });
  }

  // ---- capstone lab steps
  {
    const s = content(pres, 'Capstone Lab — CR-2026-014 Step by Step', 'Module 04');
    const c = [
      ['A', 'Environment setup', 'Verify CLAUDE.md is current. Add COBOL conventions, compiler and DD-name rules.', COL.purple],
      ['D', 'Iterative development', 'Review each changed program. Compile, run, diff against the golden master. Verify tests pass.', COL.red],
      ['B', 'Write the specification', 'Complete the 6-section spec for CR-2026-014. Save as specs/cr-2026-014.md. Score 80 or more.', COL.teal],
      ['E', 'Run custom commands', 'Run your COBOL review command on each changed program. Run /security-review before pushing.', COL.cyan],
      ['C', 'Prompt-driven planning', 'Ask Claude to read the spec and present a plan before any code is written.', COL.orange],
      ['F', 'Push & retrospective', 'Push the PR with Claude Code. Answer the 5 retrospective questions. Document lessons learned.', COL.green],
    ];
    c.forEach((k, i) => {
      const x = 0.5 + (i % 2) * 6.25, y = 1.3 + Math.floor(i / 2) * 1.7;
      box(s, x, y, 6.08, 1.55, { fill: COL.panel });
      badge(s, k[0], x + 0.15, y + 0.15, 0.6, k[3]);
      txt(s, k[1], x + 0.95, y + 0.12, 5.0, 0.45, { size: 16, bold: true });
      txt(s, k[2], x + 0.95, y + 0.6, 5.0, 0.9, { size: 12.5, color: COL.muted });
    });
  }

  // ---- NEW: scoreboard + retrospective
  {
    const s = content(pres, 'Capstone: Value Scoreboard and Retrospective', 'Module 04');
    txt(s, 'Value scoreboard (fill in as you go)', 0.5, 1.25, 6.5, 0.4, { size: 16, bold: true, color: COL.teal });
    table(s, [['Task', 'Manual estimate', 'With Claude', 'Claude got wrong'],
      ['Understand the three programs', '', '', ''], ['Document business rules', '', '', ''], ['Build the regression harness', '', '', ''], ['Implement the change', '', '', ''], ['Find defects', '', '', '']],
      0.5, 1.75, [2.4, 1.3, 1.2, 1.5], { size: 12, rowH: 0.62 });
    txt(s, 'Retrospective questions (Day 10)', 7.3, 1.25, 5.5, 0.4, { size: 16, bold: true, color: COL.teal });
    ['Where did Claude save you the most time, and how do you know?', 'Where was Claude wrong, and how did you catch it?', 'What would have gone wrong if you had skipped the spec or the plan approval?', 'What can GnuCOBOL not tell you about production on z/OS?', 'Which rule did you add to CLAUDE.md or a command, and why?'].forEach((t, i) => {
      const y = 1.75 + i * 0.85;
      badge(s, String(i + 1), 7.3, y + 0.1, 0.42, COL.orange);
      txt(s, t, 7.9, y, 4.9, 0.75, { size: 12.5, valign: 'middle' });
    });
    banner(s, 'Be honest in the scoreboard. The entries where Claude was wrong are the most valuable ones you will write.', COL.orange);
  }

  // ---- quick reference
  {
    const s = content(pres, 'Quick Reference Card', 'Reference');
    titled(s, 0.5, 1.25, 3.95, 2.0, 'Model strings', 'Opus:   claude-opus-5-5\nSonnet: claude-sonnet-5-5\nHaiku:  claude-haiku-5-5\n(alias claude-haiku-4-5)', COL.teal, { size: 12.5, gap: 4 });
    titled(s, 4.69, 1.25, 3.95, 2.0, '7 Prompt principles', '01 Be specific   02 Set a role\n03 Define format   04 Use examples\n05 State constraints   06 Step by step\n07 Iterate', COL.purple, { size: 12.5, gap: 4 });
    titled(s, 8.88, 1.25, 3.95, 2.0, '6-Section spec', '1 Overview & Goal   2 Technical Context\n3 Functional Reqs   4 Non-Functional\n5 Out of Scope   6 Acceptance Criteria', COL.orange, { size: 12.5, gap: 4 });
    code(s, 'COBOL quick commands (GnuCOBOL)', [['cobc -x -I copybooks -o bin/INTCALC src/INTCALC.cbl', COL.green], ['DD_ACCTIN=data/in.dat DD_ACCTOUT=out/o.dat ./bin/INTCALC', COL.green], ['sh scripts/run_all.sh', COL.green], ['python tests/oracle_check.py', COL.green]], 0.5, 3.45, 7.6, 1.75, 12);
    titled(s, 8.35, 3.45, 4.48, 1.75, 'Install and docs', 'Install: npm i -g @anthropic-ai/claude-code\ncode.claude.com/docs\ndocs.anthropic.com/en/docs/claude-code', COL.cyan, { size: 12, gap: 3 });
    ['1 Score', '2 Validate', '3 Plan', '4 Build', '5 Push', '6 Review'].forEach((t, i) => pill(s, t, 0.5 + i * 2.07, 5.5, 1.95, 0.55, [COL.purple, COL.teal, COL.orange, COL.cyan, COL.green, COL.red][i], 14));
    txt(s, 'Check the install command against the one on the Step 3 slide for your environment.', 0.5, 6.25, 12.3, 0.35, { size: 11, color: COL.muted });
  }

  // ---- closing
  {
    const s = pres.addSlide({ masterName: 'SECTION' });
    s.addText("You're Ready.", { placeholder: 'title' });
    txt(s, 'Now go change something safely.', 0.9, 3.5, 7, 0.6, { size: 22, color: COL.teal });
    box(s, 8.4, 1.7, 4.43, 4.5, { fill: COL.panel });
    const a = ['Apply the full workflow to a real change request this week', 'Write and peer-review your shop’s CLAUDE.md', 'Create 3 custom commands for your most repeated COBOL review tasks', 'Design a skill for your team’s highest-value task, such as copybook impact analysis'];
    txt(s, a.map((t, i) => ({ text: t, options: { bullet: true, breakLine: i < 3 } })), 8.65, 1.95, 3.95, 4.0, { size: 15, gap: 10 });
    txt(s, 'code.claude.com/docs · docs.anthropic.com/en/docs/claude-code · console.anthropic.com', 0.9, 6.4, 7.2, 0.4, { size: 11, color: COL.muted });
  }
};

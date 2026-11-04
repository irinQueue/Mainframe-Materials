// Part 2: Module 02, prompt engineering (techniques and templates) and the start of specifications.
const { COL, content, section, txt, box, badge, pill, banner, code } = require('./lib');
const { steps, table, titled } = require('./helpers');

module.exports = function part2(pres) {
  // 32 ---- divider
  section(pres, 'MODULE 02', 'Prompt Engineering',
    'From prompt basics to techniques, reasoning methods, optimization and templates, with COBOL examples.',
    ['What is a prompt?', 'Input-based techniques', 'Reasoning techniques', 'Prompt optimization', 'Prompt templates'], COL.orange);

  // 33 ---- what is a prompt
  {
    const s = content(pres, 'What Is a Prompt? And Prompt Engineering?', 'Module 02');
    titled(s, 0.5, 1.25, 6.2, 1.35, 'What is a prompt?', 'Any input you send to an LLM: a question, an instruction, a code snippet, or all three. It is the main way you tell the model what you want.', COL.teal, { size: 13 });
    titled(s, 0.5, 2.7, 6.2, 1.35, 'What is prompt engineering?', 'Designing and refining inputs so the model reliably produces accurate, relevant, high-quality output. It is the skill of making the model do exactly what you need.', COL.teal, { size: 13 });
    txt(s, 'COBOL developer example', 0.5, 4.2, 6, 0.35, { size: 14, bold: true, color: COL.orange });
    code(s, 'weak', [['Fix the abend', COL.red]], 0.5, 4.55, 6.2, 0.9, 13);
    code(s, 'strong', [['Fix the S0C7 in INTCALC paragraph 2000-PROCESS: ACCT-BAL', COL.green], ['holds spaces for ACCT000118. Show the cause, then the', COL.green], ['smallest fix.', COL.green]], 0.5, 5.5, 6.2, 1.35, 11);
    txt(s, 'Same model, wildly different results', 7.0, 1.25, 5.8, 0.4, { size: 16, bold: true, color: COL.orange });
    txt(s, 'Phrasing changes everything, not the model.', 7.0, 1.7, 5.8, 0.4, { size: 13, color: COL.muted });
    [['Every Claude Code prompt you type', 'Your /plan context, CLAUDE.md and custom commands.'], ['System prompts and API calls', 'When you build AI features into your own tools and batch utilities.'], ['Spec writing for Claude', 'Telling Claude exactly what to build and how.']].forEach((k, i) => {
      titled(s, 7.0, 2.2 + i * 1.5, 5.83, 1.35, k[0], k[1], COL.purple, { size: 13, tsize: 15 });
    });
  }

  // 34 ---- LLM basics
  {
    const s = content(pres, 'LLM Basics — How Models Process Prompts', 'Module 02');
    box(s, 0.5, 1.25, 12.33, 0.95, { fill: COL.panel, line: COL.orange });
    txt(s, "Key insight: LLMs are next-token predictors. They don't 'understand' your intent. They predict the most statistically likely continuation of your input. Good prompts make the output you want the most likely one.", 0.7, 1.27, 11.9, 0.9, { size: 13.5, valign: 'middle' });
    [['1', 'Tokenisation', 'Your text splits into tokens (sub-word fragments). Context limits are measured in tokens, not words.', COL.purple],
      ['2', 'Context window', 'The full conversation (system prompt + history + your message) is loaded as one token sequence.', COL.teal],
      ['3', 'Prediction loop', 'The model samples the next most likely token repeatedly until a stop condition or the max token limit.', COL.orange],
      ['4', 'Temperature', 'Controls randomness. 0 = deterministic. 1 and above = creative. Claude Code uses 1 by default.', COL.cyan]].forEach((k, i) => {
      const x = 0.5 + i * 3.1;
      box(s, x, 2.4, 2.95, 2.45, { fill: COL.panel });
      badge(s, k[0], x + 0.15, 2.52, 0.5, k[3]);
      txt(s, k[1], x + 0.8, 2.52, 2.1, 0.5, { size: 15, bold: true, valign: 'middle' });
      txt(s, k[2], x + 0.15, 3.15, 2.65, 1.65, { size: 12.5, color: COL.muted });
    });
    txt(s, 'What this means for your prompts', 0.5, 5.0, 12, 0.4, { size: 15, bold: true, color: COL.orange });
    const b1 = ['Longer context = higher cost and risk of degraded quality', 'Earlier tokens carry more weight: put important context first'];
    const b2 = ['The model cannot ask for clarification unless you explicitly let it', 'Every token you provide reduces the tokens left for output'];
    txt(s, b1.map((t, k) => ({ text: t, options: { bullet: true, breakLine: k < 1 } })), 0.5, 5.45, 6.0, 1.0, { size: 13, gap: 6 });
    txt(s, b2.map((t, k) => ({ text: t, options: { bullet: true, breakLine: k < 1 } })), 6.9, 5.45, 5.9, 1.0, { size: 13, gap: 6 });
  }

  // 35 ---- anatomy
  {
    const s = content(pres, 'Prompt Elements — The 4-Part Anatomy', 'Module 02');
    txt(s, 'Not every prompt needs all four elements, but knowing them lets you include or leave out each one on purpose.', 0.5, 1.2, 12.3, 0.4, { size: 13, color: COL.muted });
    const q = [
      ['01', 'Instruction', 'Be specific about format, scope and output length.', 'Summarise paragraph 2000-PROCESS of INTCALC in one sentence, focusing on when interest is skipped.', 'Summarise this.', COL.purple],
      ['02', 'Context', 'Context shifts the model’s frame of reference before it predicts.', 'You are reviewing a batch COBOL program for z/OS. Records are fixed-width and described by copybook ACCTREC.', 'Review this code.', COL.teal],
      ['03', 'Input', 'The specific content the instruction applies to.', 'Here is the paragraph: [paste lines 32-48 of INTCALC.cbl]', '(No code provided)', COL.orange],
      ['04', 'Output', 'A signal that shapes the format, length or style of the response.', 'Return a table: Condition | Action | Paragraph.', '(No format specified)', COL.cyan],
    ];
    q.forEach((k, i) => {
      const x = 0.5 + (i % 2) * 6.25, y = 1.7 + Math.floor(i / 2) * 2.6;
      box(s, x, y, 6.08, 2.45, { fill: COL.panel });
      txt(s, k[0] + '  ' + k[1], x + 0.15, y + 0.08, 5.8, 0.4, { size: 15, bold: true, color: k[5] });
      txt(s, k[2], x + 0.15, y + 0.48, 5.8, 0.45, { size: 11.5, color: COL.muted });
      box(s, x + 0.15, y + 0.98, 5.78, 0.9, { fill: COL.code, line: COL.green });
      txt(s, k[3], x + 0.22, y + 0.98, 5.64, 0.9, { size: 11.5, color: COL.green, valign: 'middle' });
      box(s, x + 0.15, y + 1.95, 5.78, 0.4, { fill: COL.code, line: COL.red });
      txt(s, k[4], x + 0.22, y + 1.95, 5.64, 0.4, { size: 11.5, color: COL.red, valign: 'middle' });
    });
  }

  // 36 ---- divider input-based
  section(pres, 'MODULE 02', 'Input-Based Prompt Techniques', 'Zero-shot, few-shot and prompt chaining, with COBOL examples.',
    ['1.1 Zero-shot: no examples, rely on pre-trained knowledge', '1.2 Few-shot: 2 to 5 worked examples before the task', '1.3 Prompt chaining: break a complex task into steps'], COL.orange);

  // 37 ---- zero-shot
  {
    const s = content(pres, '1.1 Zero-Shot Prompting', 'Module 02');
    txt(s, 'You give the model a task with no examples and rely on its pre-trained knowledge. Simplest and fastest, and often enough for well-scoped tasks.', 0.5, 1.2, 12.3, 0.6, { size: 13.5, color: COL.muted });
    [['Task is well-defined', 'The model already knows how to do this type of task well.'], ['Output format is simple', 'Short answer, classification or translation.'],
      ['Low-stakes or exploratory', 'Testing or exploring, not in production.'], ['No examples ready', 'Start here. Add examples only if the output is poor.']].forEach((k, i) => {
      titled(s, 0.5 + (i % 2) * 3.15, 1.95 + Math.floor(i / 2) * 2.1, 3.0, 1.95, k[0], k[1], COL.teal, { size: 12.5, tsize: 14 });
    });
    txt(s, 'COBOL examples', 6.95, 1.9, 5, 0.35, { size: 14, bold: true, color: COL.orange });
    code(s, 'classification', [['Classify this review comment as: \'bug\', \'style\',', COL.green], ['\'performance\' or \'question\'.', COL.green], ['', COL.text], ["Comment: 'This MOVE truncates when WS-AMT", COL.muted], ["exceeds 9999.99.'", COL.muted]], 6.95, 2.3, 5.88, 1.85, 12);
    code(s, 'code explanation', [['Explain what this COBOL statement does in one', COL.green], ['sentence, for a junior developer:', COL.green], ['', COL.text], ['COMPUTE WS-INT ROUNDED = ACCT-BAL * WS-RATE / 12', COL.muted]], 6.95, 4.3, 5.88, 1.85, 12);
    banner(s, 'Limitation: unreliable for complex tasks, domain-specific formats or nuanced instructions. The model defaults to its own style.', COL.orange);
  }

  // 38 ---- few-shot
  {
    const s = content(pres, '1.2 Few-Shot Prompting', 'Module 02');
    txt(s, 'Include 2 to 5 worked examples before the actual task. Examples show the model exactly what input and output look like for your case. More reliable than zero-shot for specific formats.', 0.5, 1.2, 12.3, 0.6, { size: 13.5, color: COL.muted });
    const t = [['Use when zero-shot gives the wrong format', 'The model keeps formatting output differently than you need.'], ['For domain-specific output', 'Custom messages, record layouts, naming conventions.'],
      ['Examples trump description', 'One good example is more precise than a paragraph of instructions.'], ['Order matters', 'Put the best, most representative example last, closest to the task.'],
      ['Diverse examples are stronger', 'Cover edge cases. Similar examples cause over-generalisation.'], ["Don't use incorrect examples", 'Wrong examples actively hurt output. Verify yours.']];
    t.forEach((k, i) => {
      const y = 1.95 + i * 0.76;
      box(s, 0.5, y, 6.2, 0.68, { fill: COL.panel });
      txt(s, k[0], 0.62, y + 0.02, 5.95, 0.3, { size: 13, bold: true, color: i === 5 ? COL.orange : COL.teal });
      txt(s, k[1], 0.62, y + 0.32, 5.95, 0.34, { size: 11.5, color: COL.muted });
    });
    code(s, 'COBOL example: abend and file-status classifier', [
      ['Classify the error type.', COL.green], ['', COL.text],
      ['Error: "S0C7, invalid packed data in INTCALC"', COL.text], ['Type: Data', COL.cyan], ['', COL.text],
      ['Error: "FILE STATUS 35 on OPEN INPUT"', COL.text], ['Type: File', COL.cyan], ['', COL.text],
      ['Error: "S0C4, protection exception"', COL.text], ['Type: Storage', COL.cyan], ['', COL.text],
      ['# Now the real task:', COL.muted], ['Error: "FILE STATUS 39 on OPEN, record length"', COL.text], ['Type: ???', COL.orange],
      ['', COL.text], ['Claude: Type: File  (follows the pattern)', COL.green]], 6.95, 1.95, 5.88, 4.4, 12);
  }

  // 39 ---- chaining
  {
    const s = content(pres, '1.3 Prompt Chaining', 'Module 02');
    txt(s, 'Break a complex task into a sequence of smaller prompts where the output of each step becomes the input of the next. Ideal for multi-step work that exceeds a single prompt’s reliable scope.', 0.5, 1.2, 12.3, 0.6, { size: 13.5, color: COL.muted });
    const c = [['1', 'Read and summarise', 'Read ACCTUPD.cbl. Summarise the posting flow in bullet points.', COL.purple], ['2', 'Identify issues', 'Given this summary, list places where numeric data could be wrong: signs, rounding, truncation.', COL.teal],
      ['3', 'Write a fix plan', 'For each issue listed, write a fix plan before touching any code.', COL.orange], ['4', 'Implement', 'Implement fix #1 from the plan. One paragraph at a time.', COL.red]];
    c.forEach((k, i) => {
      const x = 0.5 + i * 3.1;
      box(s, x, 2.05, 2.95, 2.9, { fill: COL.panel });
      badge(s, k[0], x + 0.15, 2.17, 0.5, k[3]);
      txt(s, k[1], x + 0.8, 2.17, 2.1, 0.5, { size: 15, bold: true, valign: 'middle' });
      txt(s, k[2], x + 0.15, 2.9, 2.65, 1.95, { size: 13, color: COL.muted });
    });
    const b = [['Output of step N feeds step N+1', 'Each step stays within a manageable scope'], ['A human checkpoint between steps is the PACT Approve step', 'Use /compact between long chains to save context']];
    b.forEach((p, i) => txt(s, p.map((t, k) => ({ text: t, options: { bullet: true, breakLine: k < 1 } })), 0.5 + i * 6.4, 5.2, 6.0, 1.2, { size: 13.5, gap: 8 }));
  }

  // 40 ---- divider reasoning
  section(pres, 'MODULE 02', 'Reasoning Techniques', 'Chain of Thought and Tree of Thought: making Claude think before it acts.',
    ['2.1 Chain of Thought: step-by-step reasoning before answering', '2.2 Tree of Thought: explore several paths and compare'], COL.orange);

  // 41 ---- CoT
  {
    const s = content(pres, '2.1 Chain of Thought (CoT) Prompting', 'Module 02');
    txt(s, 'Prompt the model to reason step by step before giving a final answer. This improves results on complex tasks: debugging, planning, architecture, multi-step changes.', 0.5, 1.2, 12.3, 0.6, { size: 13.5, color: COL.muted });
    titled(s, 0.5, 1.95, 6.0, 1.7, 'Why it works', 'Generating intermediate reasoning steers the model through a logical path before it commits to an answer. It cannot skip ahead to a plausible but wrong one.', COL.teal, { size: 13 });
    const u = ['Complex debugging: trace the data flow before naming a root cause', 'Architecture planning: weigh trade-offs before proposing a design', 'Multi-step refactoring: think through dependencies before touching code', 'Ambiguous requirements: reason through what the spec might mean first'];
    txt(s, u.map((t, k) => ({ text: t, options: { bullet: true, breakLine: k < 3 } })), 0.5, 3.85, 6.0, 2.4, { size: 13, gap: 8 });
    txt(s, 'Two ways to trigger CoT', 6.9, 1.95, 5.9, 0.35, { size: 14, bold: true, color: COL.orange });
    code(s, 'zero-shot CoT: trigger phrase', [['Before writing any code, think step by step', COL.green], ['about why INTCALC gives 1.62 instead of 1.63', COL.green], ['for ACCT000017. Then fix the root cause.', COL.green]], 6.9, 2.35, 5.93, 1.55, 12);
    code(s, 'few-shot CoT: show the reasoning', [
      ['Q: Is MOVE ACCT-BAL TO WS-NEW safe if WS-NEW', COL.text], ['   is PIC 9(7)V99?', COL.text], ['Thinking: ACCT-BAL is signed, WS-NEW is not, so', COL.muted], ['   a negative balance loses its sign.', COL.muted],
      ['A: No. Use a signed field, S9(7)V99.', COL.green], ['', COL.text],
      ['Q: Is COMPUTE X = BAL * RATE / 12 safe for cents?', COL.text], ['Thinking: no ROUNDED, so 1.625 becomes 1.62.', COL.muted], ['A: No. Add ROUNDED.', COL.green]], 6.9, 4.05, 5.93, 2.3, 11);
  }

  // 42 ---- ToT
  {
    const s = content(pres, '2.2 Tree of Thought (ToT) Prompting', 'Module 02');
    txt(s, 'Instead of one reasoning path, ask the model to explore several approaches, evaluate each and pick the best. Useful for design decisions and open-ended problems.', 0.5, 1.2, 12.3, 0.6, { size: 13.5, color: COL.muted });
    box(s, 3.5, 1.9, 6.33, 0.6, { fill: COL.panel, line: COL.orange });
    txt(s, 'Problem: detect dormant accounts (no activity in 12 months)', 3.6, 1.9, 6.1, 0.6, { size: 14, bold: true, color: COL.orange, align: 'center', valign: 'middle' });
    [['Path A: compare YYMMDD numerically', 'Pros: simplest.\nCons: wrong across the century. 990615 looks larger than 260101.', COL.red],
      ['Path B: century window', 'Pros: handles 1999 dates, small change.\nCons: the pivot year needs maintaining.', COL.green],
      ['Path C: intrinsic date functions', 'Pros: exact.\nCons: needs a 4-digit year first, and compiler support to check.', COL.cyan]].forEach((k, i) => {
      titled(s, 0.5 + i * 4.18, 2.75, 3.95, 1.65, k[0], k[1], k[2], { size: 12, tsize: 13.5 });
    });
    pill(s, 'Best fit: Path B, the century window', 4.0, 4.55, 5.33, 0.45, COL.green, 14);
    code(s, 'ToT prompt', [['I need a dormant-account rule for LEDGER-ME. The date field is PIC 9(6) YYMMDD.', COL.green], ['Explore 3 approaches: A) numeric YYMMDD compare  B) century window', COL.green],
      ['C) intrinsic date functions. For each: pros, cons, and the risk with two-digit', COL.green], ['years. Then recommend the best one.', COL.green]], 0.5, 5.15, 12.33, 1.55, 12);
  }

  // 43 ---- activity: prompt chaining
  {
    const s = content(pres, 'Module 02 Activity — Prompt Chaining: Add a Rule to LEDGER-ME', 'Module 02');
    box(s, 0.5, 1.2, 6.08, 0.95, { fill: COL.panel });
    txt(s, 'YOUR EXISTING SYSTEM', 0.65, 1.22, 5.8, 0.3, { size: 11, bold: true, color: COL.teal, cs: 2 });
    txt(s, 'LEDGER-ME month-end batch: ACCTUPD, INTCALC, STMTRPT', 0.65, 1.5, 5.8, 0.6, { size: 13, bold: true });
    box(s, 6.75, 1.2, 6.08, 0.95, { fill: COL.panel });
    txt(s, 'NEW FEATURE TO ADD', 6.9, 1.22, 5.8, 0.3, { size: 11, bold: true, color: COL.orange, cs: 2 });
    txt(s, 'Dormant-account rule, DORMANT flag on the statement, parameter file', 6.9, 1.5, 5.8, 0.6, { size: 13, bold: true });
    const c = [
      ['1', 'Understand', 'READ AND SUMMARISE', 'Tell Claude about LEDGER-ME. Ask it to summarise how INTCALC decides which accounts earn interest. Keep it high level.', 'No code in this step.', COL.purple],
      ['2', 'Map the files', 'IDENTIFY CHANGES', 'Pass the Step 1 summary as context. Ask which programs, copybooks and scripts must change, with one line each.', 'No code in this step.', COL.teal],
      ['3', 'Write the plan', 'PLAN, STOP AND APPROVE', 'Pass the file list as context and ask for a step-by-step plan per file. Correct it, then explicitly approve.', 'STOP. Approve before Step 4.', COL.orange],
      ['4', 'Implement', 'ONE PROGRAM AT A TIME', 'Tell Claude the plan is approved and ask for one program first. Compile and run after each one.', 'Repeat until the change is complete.', COL.red],
    ];
    c.forEach((k, i) => {
      const x = 0.5 + i * 3.1;
      box(s, x, 2.35, 2.95, 3.85, { fill: COL.panel });
      badge(s, k[0], x + 0.12, 2.45, 0.45, k[5]);
      txt(s, k[1], x + 0.68, 2.45, 2.2, 0.45, { size: 15, bold: true, valign: 'middle' });
      txt(s, k[2], x + 0.15, 3.0, 2.65, 0.3, { size: 10.5, bold: true, color: k[5], cs: 1 });
      txt(s, k[3], x + 0.15, 3.35, 2.65, 1.9, { size: 12.5, color: COL.muted });
      txt(s, k[4], x + 0.15, 5.4, 2.65, 0.7, { size: 12, bold: true, color: k[5] });
    });
    txt(s, 'Output of each step is the input of the next · always stop and approve at Step 3 · time box: 15 min', 0.5, 6.4, 12.3, 0.4, { size: 12.5, color: COL.muted });
  }

  // 44 ---- best practices
  {
    const s = content(pres, 'Best Practices — Crafting Effective Prompts', 'Module 02');
    const r = [
      ['1  Write for your stack', 'Write fixed-format COBOL for GnuCOBOL 3.2. Columns 8-72. No intrinsic functions.', 'Write good code'],
      ['2  Be specific and descriptive', 'Explain what 2100-SAV-RATE in INTCALC.cbl sets when ACCT-BAL is exactly 1,000.00. One sentence.', 'Explain this'],
      ['3  Use positives, avoid negatives', 'Write a test script for ACCTUPD. Cover: deposit, withdrawal, NSF reject, closed account.', 'Write a test'],
      ['4  Request structured output', 'Return a table: Paragraph | Reads | Writes | Fields changed.', 'Make it better'],
      ['5  Iterate: prompts are code', 'Refactor 3000-CHECK-ACCT for readability. Keep the same behaviour. No new copybooks.', 'Fix it'],
    ];
    txt(s, 'Do this', 4.3, 1.2, 5.5, 0.3, { size: 12, bold: true, color: COL.green });
    txt(s, 'Not this', 10.3, 1.2, 2.5, 0.3, { size: 12, bold: true, color: COL.red });
    r.forEach((k, i) => {
      const y = 1.55 + i * 1.04;
      box(s, 0.5, y, 12.33, 0.95, { fill: COL.panel });
      txt(s, k[0], 0.65, y, 3.5, 0.95, { size: 14, bold: true, valign: 'middle' });
      box(s, 4.3, y + 0.1, 5.8, 0.75, { fill: COL.code, line: COL.green });
      txt(s, k[1], 4.4, y + 0.1, 5.6, 0.75, { size: 11.5, color: COL.green, valign: 'middle' });
      box(s, 10.3, y + 0.1, 2.4, 0.75, { fill: COL.code, line: COL.red });
      txt(s, k[2], 10.4, y + 0.1, 2.2, 0.75, { size: 12, color: COL.red, valign: 'middle', align: 'center' });
    });
  }

  // 45 ---- divider templates
  section(pres, 'MODULE 02', 'Prompt Templates', 'Techniques decide how Claude thinks. Templates decide how you structure the ask.',
    ['RTF, RTFC, RTCIF', 'CO-STAR', 'AUTOMAT', 'BRAIN', 'Goal, Input, Output (GIO)'], COL.orange);

  // 46 ---- RTF family
  {
    const s = content(pres, 'Prompt Template 1 — RTF, RTFC, RTCIF', 'Module 02');
    txt(s, 'Templates evolve as your needs become more complex. Each level adds structure and control over Claude’s output.', 0.5, 1.2, 12.3, 0.4, { size: 13.5, color: COL.muted });
    const c = [
      ['RTF', 'Role · Task · Format', ['Role: You are a senior COBOL developer.', 'Task: Review this paragraph for numeric-handling defects.', 'Format: Bullet list, one issue per line.'], 'A good starting point for most tasks.', COL.purple],
      ['RTFC', 'Role · Task · Format · Constraints', ['Role: You are a senior COBOL developer.', 'Task: Review this paragraph for numeric-handling defects.', 'Format: Bullet list, one issue per line.', 'Constraints: Signs, rounding and truncation only. Max 5 issues.'], 'Adds constraints to control scope and length.', COL.teal],
      ['RTCIF', 'Full template', ['Role: Senior COBOL developer.', 'Task: Review the paragraph below for numeric defects.', 'Context: Batch program, fixed-width records, copybook ACCTREC.', 'Input: [paste INTCALC.cbl lines 32-48]', 'Format: Table: Issue | Severity | Fix', 'Constraints: Signs and rounding only.'], 'Production-grade. Use for critical tasks.', COL.orange],
    ];
    c.forEach((k, i) => {
      const x = 0.5 + i * 4.18;
      box(s, x, 1.75, 3.95, 4.55, { fill: COL.panel });
      txt(s, k[0], x + 0.15, 1.82, 3.6, 0.5, { size: 22, bold: true, color: k[4] });
      txt(s, k[1], x + 0.15, 2.32, 3.6, 0.35, { size: 12, color: COL.muted });
      txt(s, k[2].map((t, n) => ({ text: t, options: { breakLine: n < k[2].length - 1 } })), x + 0.15, 2.8, 3.65, 2.7, { size: 12, color: COL.cyan, gap: 5 });
      txt(s, k[3], x + 0.15, 5.6, 3.65, 0.6, { size: 12, bold: true, color: k[4] });
    });
  }

  // 47 ---- divider other templates
  section(pres, 'MODULE 02', 'Other Templates', 'CO-STAR, AUTOMAT, BRAIN and Goal-Input-Output.', null, COL.orange);

  // 48 ---- CO-STAR
  {
    const s = content(pres, 'CO-STAR Framework', 'Module 02');
    txt(s, 'A complete context-setting structure, originally from the Singapore Government Tech Agency. Excellent when context heavily shapes the output.', 0.5, 1.2, 12.3, 0.6, { size: 13.5, color: COL.muted });
    const q = [['C', 'Context', 'Background on the situation', 'You are reviewing a nightly batch program on z/OS that updates a master file.', COL.purple], ['O', 'Objective', 'What you want Claude to do', 'Identify paragraphs that could produce wrong balances.', COL.teal],
      ['S', 'Style', 'Communication style', 'Write like a senior mainframe developer reviewing a change.', COL.orange], ['T', 'Tone', 'Attitude and emotion', 'Direct and concise. No filler. Flag critical issues clearly.', COL.cyan],
      ['A', 'Audience', 'Who will read the response', 'A developer who knows Java but is new to COBOL.', COL.green], ['R', 'Response', 'Desired format and length', 'Markdown list: Paragraph | Problem | Fix.', COL.red]];
    q.forEach((k, i) => {
      const x = 0.5 + (i % 2) * 6.25, y = 1.95 + Math.floor(i / 2) * 1.5;
      box(s, x, y, 6.08, 1.38, { fill: COL.panel });
      badge(s, k[0], x + 0.15, y + 0.15, 0.6, k[4]);
      txt(s, k[1] + ': ' + k[2], x + 0.9, y + 0.1, 5.05, 0.35, { size: 13, bold: true });
      txt(s, k[3], x + 0.9, y + 0.5, 5.05, 0.8, { size: 12.5, color: COL.cyan });
    });
  }

  // 49 ---- AUTOMAT
  {
    const s = content(pres, 'AUTOMAT Framework', 'Module 02');
    txt(s, 'Designed for automation and pipeline prompts: when Claude performs an autonomous or semi-autonomous task in a workflow, not just answering a question.', 0.5, 1.2, 12.3, 0.55, { size: 13.5, color: COL.muted });
    const r = [['A', 'Act as', 'Act as a COBOL code reviewer specialised in batch posting programs.'], ['U', 'User context', 'A mid-level developer maintaining a 20-year-old batch system.'], ['T', 'Task', 'Review INTCALC.cbl for numeric-handling defects.'],
      ['O', 'Output format', 'JSON: [{paragraph, issue, severity: low/med/high, fix}]'], ['M', 'Mode / style', 'Be direct. Skip praise. Only flag real issues.'], ['A', 'Audience', 'A developer who will apply the fixes immediately. No explanation needed.'],
      ['T', 'Temperature cue', 'Be consistent and deterministic. This feeds a review script.']];
    const cs = [COL.purple, COL.teal, COL.orange, COL.cyan, COL.green, COL.red, COL.purple];
    r.forEach((k, i) => {
      const y = 1.85 + i * 0.7;
      box(s, 0.5, y, 12.33, 0.62, { fill: COL.panel });
      badge(s, k[0], 0.62, y + 0.06, 0.5, cs[i]);
      txt(s, k[1], 1.3, y, 2.4, 0.62, { size: 13.5, bold: true, valign: 'middle' });
      txt(s, k[2], 3.8, y, 8.9, 0.62, { size: 13, color: COL.cyan, valign: 'middle' });
    });
  }

  // 50 ---- BRAIN
  {
    const s = content(pres, 'BRAIN Framework (Enterprise Research)', 'Module 02');
    txt(s, 'Designed for enterprise research: when you need Claude to analyse a problem in depth, such as architecture decisions and technical investigations.', 0.5, 1.2, 12.3, 0.55, { size: 13.5, color: COL.muted });
    const r = [['B', 'Background', 'Set the full context upfront', 'LEDGER-ME runs month-end on 200 test accounts; production has millions. Dates are two-digit years (YYMMDD).'],
      ['R', 'Request', 'What you need Claude to do', 'Research and compare three ways to detect dormant accounts for our case.'],
      ['A', 'Action steps', 'How Claude should approach it', 'For each option: 1) explain how it works, 2) list pros and cons, 3) estimate change effort.'],
      ['I', 'Input data', 'Data Claude should analyse', '[paste ACCTREC.cpy and INTCALC.cbl here]'],
      ['N', 'Notes', 'Guardrails and preferences', 'Record length must stay 60 bytes. Example constraint: no intrinsic functions. Two developers. No change to the job schedule.']];
    const cs = [COL.purple, COL.teal, COL.orange, COL.cyan, COL.green];
    r.forEach((k, i) => {
      const y = 1.9 + i * 0.9;
      box(s, 0.5, y, 12.33, 0.82, { fill: COL.panel });
      badge(s, k[0], 0.62, y + 0.12, 0.58, cs[i]);
      txt(s, k[1], 1.4, y + 0.08, 2.6, 0.35, { size: 14, bold: true });
      txt(s, k[2], 1.4, y + 0.44, 2.6, 0.32, { size: 11, color: COL.muted });
      txt(s, k[3], 4.1, y, 8.6, 0.82, { size: 12.5, color: COL.cyan, valign: 'middle' });
    });
  }

  // 51 ---- GIO
  {
    const s = content(pres, 'Goal – Input – Output (GIO)', 'Module 02');
    txt(s, 'The most practical template for real-world automation, proposals and pipelines. Every component has a job and nothing is left ambiguous.', 0.5, 1.2, 12.3, 0.55, { size: 13.5, color: COL.muted });
    const r = [['GOAL', 'What you want', 'Add a monthly maintenance fee to INTCALC.', COL.purple],
      ['INPUTS', 'Data provided to Claude', 'Copybook ACCTREC (60 bytes). Parameter record read through DD PARMIN: threshold 9(7)V99, fee 9(5)V99.', COL.teal],
      ['CONSTRAINTS', 'Rules Claude must follow', 'Fixed format, columns 8-72. Match the numbered paragraphs. New fields come out of FILLER. No hard-coded values.', COL.orange],
      ['OUTPUT', 'Format and structure', 'Changed ACCTREC.cpy, INTCALC.cbl and the run script, each in a separate code block.', COL.cyan],
      ['VERIFY', 'How to check quality', 'After generating, run sh scripts/run_all.sh and python tests/oracle_check.py --checks=fee. All checks must pass.', COL.green]];
    r.forEach((k, i) => {
      const y = 1.9 + i * 0.9;
      box(s, 0.5, y, 12.33, 0.82, { fill: COL.panel });
      txt(s, k[0], 0.65, y + 0.08, 2.1, 0.35, { size: 14, bold: true, color: k[3] });
      txt(s, k[1], 0.65, y + 0.44, 2.3, 0.32, { size: 11, color: COL.muted });
      txt(s, k[2], 3.1, y, 9.6, 0.82, { size: 12.5, color: COL.cyan, valign: 'middle' });
    });
  }

  // 52 ---- techniques vs templates
  {
    const s = content(pres, 'Techniques vs Templates — Why You Need Both', 'Module 02');
    txt(s, 'They solve different problems. The technique decides HOW Claude thinks. The template decides HOW you structure the ask.', 0.5, 1.2, 12.3, 0.6, { size: 13.5, color: COL.muted });
    table(s, [['Technique (how Claude thinks)', 'What it does', 'Template (how you ask)', 'What it does'],
      ['Zero-Shot', 'No examples, rely on training knowledge', 'RTF / RTFC / RTCIF', 'Role, task, format: escalating detail'],
      ['Few-Shot', 'Pattern from examples you provide', 'CO-STAR', 'Full context-setting for complex tasks'],
      ['Prompt Chaining', 'Break the work into sequential steps', 'AUTOMAT', 'Automation and pipeline workflows'],
      ['Chain of Thought', 'Force step-by-step reasoning', 'BRAIN', 'Enterprise research and analysis'],
      ['Tree of Thought', 'Explore multiple paths in parallel', 'Goal-Input-Output', 'Proposals, automation, real tasks']],
      0.5, 1.95, [2.6, 3.55, 2.6, 3.58], { size: 12.5, rowH: 0.62, boldCol: 0 });
    banner(s, 'Rule: pick your TECHNIQUE first (how Claude reasons), then wrap it in a TEMPLATE (how you structure the ask).', COL.teal);
  }

  // 53 ---- optimization
  {
    const s = content(pres, 'Prompt Optimization — Why It Matters', 'Module 02');
    txt(s, 'Prompt optimization is the systematic process of refining prompts to maximise output quality, consistency and efficiency. The same task with a different structure gives dramatically different results.', 0.5, 1.2, 12.3, 0.65, { size: 13.5, color: COL.muted });
    [['Consistency', 'The same prompt structure gives predictable, repeatable output across sessions and team members.', COL.purple], ['Efficiency', 'Well-optimised prompts use fewer tokens: less cost, less context bloat, faster responses.', COL.teal],
      ['Scalability', 'Optimised prompts work reliably at scale, in pipelines, automation and production tooling.', COL.orange], ['Collaboration', 'Shared prompt templates align the team: everyone gets the same quality from Claude.', COL.cyan]].forEach((k, i) => {
      titled(s, 0.5 + (i % 2) * 6.25, 2.05 + Math.floor(i / 2) * 2.2, 6.08, 2.05, k[0], k[1], k[2], { size: 14, tsize: 16 });
    });
  }

  // 54 ---- divider specs
  section(pres, 'MODULE 02', 'Writing Specifications', 'Structured specs consistently outperform even perfect prompts for complex, multi-file tasks.',
    ['What makes a good spec', 'Language, pitfalls and pre-flight check', 'A worked COBOL spec: CR-2026-014'], COL.orange);

  // 55 ---- 5 categories
  {
    const s = content(pres, 'What Makes a Good Spec? The 5 Categories', 'Module 02');
    const c = [
      ['1. Task Definition', ['Clear action verb (build, fix, refactor, add, remove)', 'Scope: what is in and what is out', 'WHY: the problem being solved', 'One coherent task, not several bundled'], '"Add a fee to INTCALC. Don\'t touch ACCTUPD."', COL.purple],
      ['2. Technical Context', ['Compiler, platform and versions', 'Files to create or modify', 'Copybooks and programs to use or avoid', 'Patterns to follow from existing code'], '"Use copybook ACCTREC. Follow the DD_name file pattern."', COL.teal],
      ['3. Expected Output', ['Deliverable format (files, paragraphs, reports)', 'Behaviour when it works', 'Record and report layouts', 'Example of a run'], '"ACCT-FEE S9(5)V99 SIGN LEADING SEPARATE in ACCTREC."', COL.orange],
      ['4. Constraints', ['Must-haves (non-negotiable)', 'Must-NOT-haves', 'Limits: record length, run time', 'Compatibility: GnuCOBOL vs Enterprise COBOL'], '"No new files except PARMS.DAT. Record stays 60 bytes."', COL.cyan],
      ['5. Edge Cases & Errors', ['Invalid input: bad data on a record', 'Empty or missing files', 'Failure modes: abend, return code, log', 'Boundaries: exactly on a threshold'], '"RC 12 if PARMIN is missing. Closed accounts pay no fee."', COL.green],
    ];
    c.forEach((k, i) => {
      const x = 0.5 + (i % 3) * 4.18, y = 1.25 + Math.floor(i / 3) * 2.85, w = 3.95;
      box(s, x, y, w, 2.72, { fill: COL.panel });
      txt(s, k[0], x + 0.15, y + 0.06, w - 0.3, 0.35, { size: 14, bold: true, color: k[3] });
      txt(s, k[1].map((t, n) => ({ text: t, options: { bullet: true, breakLine: n < 3 } })), x + 0.15, y + 0.45, w - 0.3, 1.6, { size: 11.5, gap: 2 });
      box(s, x + 0.12, y + 2.02, w - 0.24, 0.62, { fill: COL.code, line: k[3] });
      txt(s, k[2], x + 0.18, y + 2.02, w - 0.36, 0.62, { size: 10.5, italic: true, color: COL.cyan, valign: 'middle' });
    });
  }

  // 56 ---- language, pitfalls, pre-flight
  {
    const s = content(pres, 'Writing Good Specs — Language, Pitfalls & Pre-flight Check', 'Module 02');
    titled(s, 0.5, 1.25, 5.9, 2.45, 'Power words',
      'Good action verbs: Build · Create · Add · Implement · Refactor · Fix · Remove · Replace · Migrate · Extract · Optimise · Update · Convert\nGood constraint phrases: "Don\'t modify..." · "Must not exceed..." · "Keep existing..." · "Follow the pattern in..." · "Return X when..." · "Stop with RC 12 if..."', COL.teal, { size: 12.5, gap: 8 });
    table(s, [['Avoid these', 'Better: be specific'], ['"Make it better"', 'Better how? Which paragraph?'], ['"Handle errors"', 'Which errors? What return code?'], ['"Add a file"', 'Which DD name? What layout?'], ['"Make it fast"', 'A measurable target (elapsed time)'], ['"Clean up code"', 'Which paragraphs? Which pattern?']],
      6.7, 1.25, [2.2, 3.93], { size: 12.5, rowH: 0.41, colColors: [COL.red, COL.green] });
    txt(s, 'PRE-FLIGHT CHECKLIST: ask yourself before submitting the spec', 0.5, 3.95, 12.3, 0.4, { size: 14, bold: true, color: COL.orange });
    ['Would someone else build the SAME thing from this spec?', 'Did I cover the unhappy paths (errors, edge cases)?', "Did I specify what 'DONE' looks like?", 'Did I provide enough context about the existing code?', 'Did I mention what NOT to do?', 'Is this ONE task, or should I split it up?'].forEach((t, i) => {
      const x = 0.5 + (i % 2) * 6.25, y = 4.45 + Math.floor(i / 2) * 0.62;
      box(s, x, y, 6.08, 0.55, { fill: COL.panel });
      txt(s, '✓  ' + t, x + 0.15, y, 5.8, 0.55, { size: 13, valign: 'middle' });
    });
  }
};

// Part 1: cover, learning path, Module 0 (setup) and Module 1 (foundation).
const { COL, content, section, txt, box, badge, pill, banner, code, setCur } = require('./lib');
const { steps, table, titled } = require('./helpers');

module.exports = function part1(pres) {
  // 1 ---- cover
  {
    const s = pres.addSlide({ masterName: 'COVER' });
    setCur('Cover');
    s.addText('Mastering Claude Code', { placeholder: 'title' });
    txt(s, 'for Mainframe COBOL Developers', 0.9, 3.0, 11, 0.7, { size: 32, bold: true, color: COL.teal });
    txt(s, 'From Foundations to Agentic Mastery', 0.9, 3.8, 9, 0.5, { size: 20, color: COL.muted });
    code(s, 'terminal', [
      ['$ cd ledger-me', COL.muted], ['$ claude', COL.muted],
      ['> Read src/ and copybooks/.', COL.green], ['  Explain the batch flow.', COL.green],
    ], 7.6, 4.55, 5.2, 1.9, 14);
    txt(s, '2026 \u00B7 Claude Code v2.1.81 \u00B7 Internal Use Only \u2014 Do Not Share Outside the Organization', 0.9, 6.85, 11.5, 0.35, { size: 11, color: COL.muted });
  }

  // 2 ---- learning path (modules 0 to 2)
  {
    const s = content(pres, 'Learning Path');
    const cols = [
      ['Module 0 \u2014 Setup', COL.teal, ['01 \u2014 Account Registration', '02 \u2014 Claude Code Installation', '03 \u2014 Mainframe Training Environment']],
      ['Module 1 \u2014 Foundation', COL.purple, ['01 \u2014 What is Claude Code?', '02 \u2014 Tokens and Context Window', '03 \u2014 Interacting with Agentic AI (PACT Framework)', '04 \u2014 Claude Code Extensions', '05 \u2014 Module Exercises']],
      ['Module 2 \u2014 Core Skills', COL.orange, ['01 \u2014 Prompt Engineering', '02 \u2014 Writing Specs', '03 \u2014 Module Exercises']],
    ];
    cols.forEach((c, i) => {
      const x = 0.5 + i * 4.18;
      box(s, x, 1.3, 3.95, 4.75, { fill: COL.panel });
      txt(s, c[0], x + 0.2, 1.42, 3.55, 0.45, { size: 18, bold: true, color: c[1] });
      const runs = c[2].map((t, k) => ({ text: t, options: { breakLine: k < c[2].length - 1 } }));
      txt(s, runs, x + 0.2, 2.05, 3.55, 3.8, { size: 15, gap: 10 });
    });
    banner(s, 'Each phase builds on the previous \u2014 mental models first, daily tools second, advanced features last.', COL.teal);
  }

  // 3 ---- learning path (modules 3 and 4)
  {
    const s = content(pres, 'Learning Path (continued)');
    box(s, 0.5, 1.3, 6.0, 4.75, { fill: COL.panel });
    txt(s, 'Module 3 \u2014 Governance', 0.7, 1.42, 5.6, 0.45, { size: 18, bold: true, color: COL.cyan });
    const m3 = ['01 \u2014 AI-Assisted Development Workflow', '02 \u2014 Sample Usage of the AI-Assisted Development Workflow', '03 \u2014 AI Usage Policy'];
    txt(s, m3.map((t, k) => ({ text: t, options: { breakLine: k < 2 } })), 0.7, 2.05, 5.6, 3.8, { size: 15, gap: 10 });
    box(s, 6.83, 1.3, 6.0, 4.75, { fill: COL.panel });
    txt(s, 'Module 4 \u2014 Capstone', 7.03, 1.42, 5.6, 0.45, { size: 18, bold: true, color: COL.red });
    txt(s, '01 \u2014 LEDGER-ME Capstone Project', 7.03, 2.05, 5.6, 0.4, { size: 15 });
    txt(s, 'Everything you have learned, applied end to end on a real COBOL batch system: inherit it, understand it, change it, prove it.', 7.03, 2.6, 5.6, 1.6, { size: 15, color: COL.muted });
    banner(s, 'Each phase builds on the previous \u2014 mental models first, daily tools second, advanced features last.', COL.teal);
  }

  // 4 ---- module 0 divider
  section(pres, 'MODULE 00', 'Installation & First Session',
    'From team invitation to your first Claude Code session, step by step.',
    ['Check your email', 'Set up Claude.ai', 'Install Git CLI', 'Install Claude Code', 'Meet your mainframe training environment'], COL.teal);

  // 5 ---- step 1
  {
    const s = content(pres, 'Step 1 \u2014 Accept Invitation & Set Up Claude.ai', 'Module 00');
    txt(s, 'Check your email invitation', 0.5, 1.25, 5.8, 0.4, { size: 16, bold: true, color: COL.teal });
    box(s, 0.5, 1.7, 5.8, 3.0, { fill: COL.panel });
    txt(s, 'From: noreply@anthropic.com', 0.7, 1.8, 5.4, 0.3, { size: 13, color: COL.muted });
    txt(s, "Subject: You've been invited to a Claude Team plan", 0.7, 2.1, 5.4, 0.3, { size: 13, color: COL.muted });
    txt(s, "Hi [Your Name], you've been invited to join your organisation's Claude Team plan. Click the button below to accept and create your account.", 0.7, 2.5, 5.4, 0.85, { size: 13 });
    pill(s, 'Accept Invitation', 2.0, 3.45, 2.8, 0.5, COL.teal, 14);
    txt(s, 'Link expires in 7 days. Check spam if not received.', 0.7, 4.15, 5.4, 0.3, { size: 12, color: COL.muted });
    const w = ['Check your spam folder if not in your inbox within 5 minutes', 'Use your work email \u2014 it must match the address your manager registered', 'The link is single-use. Ask your admin to resend if it expires'];
    txt(s, w.map((t, k) => ({ text: t, options: { bullet: true, breakLine: k < 2 } })), 0.5, 4.9, 5.8, 1.4, { size: 13, color: COL.orange, gap: 4 });
    txt(s, 'Set up your Claude.ai account', 6.9, 1.25, 5.9, 0.4, { size: 16, bold: true, color: COL.teal });
    steps(s, [
      ['Click the invitation link', "Opens claude.ai. Choose 'Create account' if you're new, or 'Sign in' if you already have a personal account."],
      ['Complete account setup', 'Set your name and password. Verify your email if prompted. Two-factor auth is recommended for team accounts.'],
      ['Confirm you are on the Team plan', "After login, go to Settings > Plan. You should see your organisation's Team plan, not the free tier."],
      ['Try a quick chat first', 'Before installing Claude Code, send one message in Claude.ai to confirm your account works and you are authenticated.'],
    ], 6.9, 1.75, 5.9, { gap: 1.18 });
  }

  // 6 ---- step 2 git
  {
    const s = content(pres, 'Step 2 \u2014 Install Git CLI for Windows', 'Module 00');
    txt(s, 'Why Git CLI is required', 0.5, 1.25, 6, 0.4, { size: 16, bold: true, color: COL.teal });
    const why = [
      ['git diff', 'Claude reads your uncommitted changes before reviewing or modifying code'],
      ['/commit', 'Claude creates git commits. git must be in PATH for this to work'],
      ['/review', 'Needs git to compare staged vs unstaged changes in a PR'],
      ['Safety net', 'Commit before a large agentic run: instant rollback if something goes wrong'],
      ['/diff', 'Built-in command to view all changes Claude made per turn. Needs git'],
    ];
    why.forEach((w, i) => {
      const y = 1.75 + i * 0.9;
      box(s, 0.5, y, 6.0, 0.8, { fill: COL.panel });
      txt(s, w[0], 0.65, y + 0.05, 1.5, 0.7, { size: 13, bold: true, color: COL.cyan, font: 'Courier New', valign: 'middle' });
      txt(s, w[1], 2.2, y + 0.05, 4.2, 0.7, { size: 12.5, valign: 'middle' });
    });
    txt(s, 'Install Git for Windows', 6.9, 1.25, 5.9, 0.4, { size: 16, bold: true, color: COL.teal });
    steps(s, [
      ['Download Git CLI', 'Go to git-scm.com/download/win and download "64-bit Git for Windows Setup".'],
      ['Run the installer', 'Accept all defaults. On the PATH screen select "Git from the command line and also from 3rd-party software".'],
      ['Verify in a new terminal', 'Open Windows Terminal and run the command below.'],
    ], 6.9, 1.75, 5.9, { gap: 1.05 });
    code(s, 'Windows Terminal', [['git --version', COL.green], ['git version 2.47.1.windows.2', COL.muted], ['', COL.text], ['# First-time setup (run once)', COL.muted],
      ['git config --global user.name "Your Name"', COL.green], ['git config --global user.email "you@company.com"', COL.green]], 6.9, 4.95, 5.93, 1.9, 12);
  }

  // 7 ---- step 3 install claude code
  {
    const s = content(pres, 'Step 3 \u2014 Install Claude Code on Windows', 'Module 00');
    steps(s, [
      ['Open an Admin terminal', 'Press Win + X, then select Windows Terminal (Admin) or Command Prompt (Admin). Run as Administrator is required for the global install.'],
      ['Run the install command', 'Copy and paste this single command. It downloads, installs, then deletes the installer.'],
    ], 0.5, 1.3, 6.0, { gap: 1.25 });
    code(s, 'Admin terminal', [['curl -fsSL https://claude.ai/install.cmd -o install.cmd &&', COL.green], ['install.cmd && del install.cmd', COL.green]], 1.0, 3.8, 5.5, 1.4, 12);
    steps(s, [['Authenticate', 'A browser tab opens automatically. Sign in with the Anthropic account you set up in Step 1. The CLI saves your token.']], 0.5, 5.4, 6.0, { gap: 1.2 });
    txt(s, 'What that command does', 6.9, 1.25, 5.9, 0.4, { size: 16, bold: true, color: COL.teal });
    table(s, [['Part', 'What it does'],
      ['curl -fsSL ...', 'Downloads install.cmd from claude.ai'],
      ['-o install.cmd', 'Saves it locally as install.cmd'],
      ['&& install.cmd', 'Runs it (installs Claude Code globally)'],
      ['&& del install.cmd', 'Cleans up: removes the installer after use']], 6.9, 1.75, [2.1, 3.83], { size: 12, rowH: 0.52, mono: [0] });
    txt(s, 'Verify installation', 6.9, 4.5, 5.9, 0.4, { size: 16, bold: true, color: COL.teal });
    code(s, 'New terminal (no admin needed)', [['claude --version', COL.green], ['Claude Code 2.1.81', COL.muted]], 6.9, 4.95, 5.93, 1.3, 13);
  }

  // 8 ---- step 4 path
  {
    const s = content(pres, 'Step 4 \u2014 Add Claude Code to Your User PATH', 'Module 00');
    box(s, 0.5, 1.2, 12.33, 0.75, { fill: COL.panel });
    txt(s, 'Why this is needed: the installer places the Claude Code binary in C:\\Users\\(username)\\.local\\bin. Windows will not find it in a new terminal unless that folder is in your User PATH.', 0.7, 1.22, 11.9, 0.7, { size: 13, valign: 'middle' });
    steps(s, [
      ['Press Win and search "Environment Variables"', 'Select "Edit the system environment variables" from the Start menu results.'],
      ['Click the "Environment Variables..." button', 'Found at the bottom of the System Properties > Advanced tab.'],
      ['Under "User variables" select Path, then Edit', 'Do NOT edit System variables. Only User variables.'],
      ['Click New and add the path', 'C:\\Users\\(username)\\.local\\bin'],
      ['Click OK on all three dialogs', 'Then open a brand new terminal window. The change only applies to new terminals.'],
    ], 0.5, 2.2, 7.0, { gap: 0.95, size: 12.5 });
    code(s, 'Environment Variables', [['User variables for (username)', COL.muted], ['Path   C:\\Users\\(user)\\AppData...', COL.text], ['TEMP   C:\\Users\\(user)\\AppData...', COL.text],
      ['TMP    C:\\Users\\(user)\\AppData...', COL.text], ['', COL.text], ['New entry:', COL.muted], ['C:\\Users\\(username)\\.local\\bin', COL.green]], 7.9, 2.2, 4.93, 3.4, 12);
  }

  // 9 ---- step 5 first session
  {
    const s = content(pres, 'Step 5 \u2014 Launch Your First Claude Code Session', 'Module 00');
    steps(s, [
      ['Navigate to your project', 'cd C:\\Projects\\ledger-me. Always start inside your project folder: Claude reads files relative to where you launch it.'],
      ['Launch Claude Code', 'Type claude. The CLI starts and shows the model name and the project it detected.'],
      ['Check status', '/status confirms model, your Anthropic account and API connectivity. Always do this first.'],
      ['Give your first task', "Skip 'hello'. Go straight to a real task. Prompting is covered in the next module."],
    ], 0.5, 1.3, 6.2, { gap: 1.35 });
    code(s, 'Windows Terminal \u2014 ledger-me', [
      ['C:\\Projects\\ledger-me> claude', COL.green], ['', COL.text], ['Claude Code v2.1.81', COL.muted], ['Model  : claude-sonnet-5-5', COL.muted],
      ['Account: you@company.com', COL.muted], ['Project: ledger-me', COL.muted], ['', COL.text], ['> /status', COL.green], ['API: Connected    Plan: Team', COL.muted], ['', COL.text],
      ['> Read CLAUDE.md if it exists,', COL.green], ['  then summarise what this system does.', COL.green], ['Reading files...', COL.muted]], 7.0, 1.3, 5.83, 4.9, 13);
  }

  // 10 ---- NEW: mainframe training environment
  {
    const s = content(pres, 'Your Mainframe Training Environment', 'Module 00');
    const t = [
      ['VS Code', 'Your editor and terminal. Open the starter folder, read code, run commands.', COL.cyan],
      ['IBM Z Open Editor', 'COBOL language support in VS Code: colouring, structure and copybook awareness.', COL.purple],
      ['GnuCOBOL 3.2', 'cobc compiles and runs the three programs on your VM. Fast feedback, no transfers.', COL.teal],
      ['Git', 'Your safety net. Commit every day. Each training day has a tag to catch up from.', COL.orange],
      ['Python 3', 'Generates the invented test data and runs the independent test checks.', COL.green],
      ['Zowe CLI and Explorer', 'The route to a real z/OS system. Needs a host, user ID and port from your facilitator.', COL.red],
    ];
    t.forEach((c, i) => titled(s, 0.5 + (i % 3) * 4.18, 1.3 + Math.floor(i / 3) * 1.8, 3.95, 1.65, c[0], c[1], c[2], { size: 13 }));
    code(s, 'Day 0 smoke test', [['cobc --version', COL.green], ['sh scripts/run_all.sh', COL.green], ['# expect: ACCTUPD RC=0, INTCALC RC=0, STMTRPT RC=0', COL.muted]], 0.5, 4.95, 6.6, 1.4, 12);
    box(s, 7.35, 4.95, 5.48, 1.4, { fill: COL.panel, line: COL.orange });
    txt(s, 'A local run is a smoke test, not proof. Behaviour on z/OS, DB2 and CICS can differ. You will document those differences on Day 9.', 7.55, 5.0, 5.1, 1.3, { size: 13, color: COL.orange, valign: 'middle' });
  }

  // 11 ---- module 1 divider (what is claude code)
  section(pres, 'MODULE 01', 'What is Claude Code?',
    'An AI coding assistant from Anthropic that works with your files, in your terminal.',
    ['Writes, explains and improves code from natural-language prompts', 'Built for collaboration, not only output', 'Explains code, suggests changes and helps debug while keeping context'], COL.purple);

  // 12 ---- chat vs dev tool vs api
  {
    const s = content(pres, 'Claude \u00B7 Claude Code \u00B7 Anthropic API', 'Module 01');
    const c = [
      ['Chat', 'Claude.ai', 'Web and mobile chat interface. Consumer-focused. Great for exploration and Q&A. No local file system access.', COL.purple],
      ['Dev Tool', 'Claude Code', 'CLI-first agentic coding tool. Reads your files, runs commands, and works autonomously on multi-step tasks.', COL.teal],
      ['Build', 'Anthropic API', 'Programmatic REST and SDK access. Build Claude into your own apps, products and pipelines.', COL.orange],
    ];
    c.forEach((k, i) => {
      const x = 0.5 + i * 4.18;
      box(s, x, 1.3, 3.95, 3.3, { fill: COL.panel });
      pill(s, k[0], x + 0.2, 1.45, 1.3, 0.38, k[3], 12);
      txt(s, k[1], x + 0.2, 2.0, 3.55, 0.5, { size: 22, bold: true });
      txt(s, k[2], x + 0.2, 2.6, 3.55, 1.9, { size: 14, color: COL.muted });
    });
    box(s, 0.5, 4.85, 12.33, 1.35, { fill: COL.panel, line: COL.teal });
    txt(s, 'On the mainframe project', 0.7, 4.92, 5, 0.35, { size: 14, bold: true, color: COL.teal });
    txt(s, 'Claude Code works on the source files on your VM: COBOL programs, copybooks, JCL and scripts. It does not log on to z/OS by itself. Production data stays out of it.', 0.7, 5.3, 11.9, 0.85, { size: 14 });
    banner(s, 'Key insight: Claude is the model. The products are different access surfaces.', COL.purple);
  }

  // 13 ---- tools reference
  {
    const s = content(pres, 'Claude Code \u2014 Tools Reference', 'Module 01');
    const L = [['Tool', 'Category', 'What it does'],
      ['Read', 'File system', 'Reads any file into context: programs, copybooks, JCL'],
      ['Write', 'File system', 'Creates or overwrites a file on disk'],
      ['Edit', 'File system', 'Targeted edit to an existing file, such as one paragraph'],
      ['MultiEdit', 'File system', 'Several edits to one file in one operation'],
      ['Bash', 'Execution', 'Runs any shell command: cobc, scripts, tests'],
      ['Glob', 'File system', 'Finds files matching a pattern (*.cbl, *.cpy)'],
      ['Grep', 'File system', 'Searches file contents, for example every use of ACCT-BAL'],
      ['LS', 'File system', 'Lists directory contents']];
    const R = [['Tool', 'Category', 'What it does'],
      ['WebSearch', 'Web', 'Searches the web for docs or error messages'],
      ['WebFetch', 'Web', 'Fetches and reads a specific URL'],
      ['Task', 'Agentic', 'Spawns a sub-agent for a discrete task'],
      ['TodoRead', 'Agentic', 'Reads the current session task list'],
      ['TodoWrite', 'Agentic', 'Updates the session task list'],
      ['NotebookRead', 'File system', 'Reads a Jupyter .ipynb notebook'],
      ['NotebookEdit', 'Edit', 'Adds or edits cells in a notebook'],
      ['MCP tools', 'MCP', 'Any tool from a connected MCP server (Jira, GitHub...)']];
    table(s, L, 0.5, 1.3, [1.2, 1.35, 3.55], { size: 12, rowH: 0.56, mono: [0], boldCol: 0 });
    table(s, R, 6.73, 1.3, [1.35, 1.2, 3.55], { size: 12, rowH: 0.56, mono: [0], boldCol: 0 });
    txt(s, 'Source: Claude Code CLI v2.1.81 \u00B7 code.claude.com/docs', 0.5, 6.5, 8, 0.3, { size: 11, color: COL.muted });
  }

  // 14 ---- models divider
  section(pres, 'MODULE 01', 'The Claude Model Family',
    'Opus, Sonnet, Haiku: three tiers, each making a different speed, cost and quality trade-off.', null, COL.purple);

  // 15 ---- three tiers
  {
    const s = content(pres, 'Three-Tier Model Architecture', 'Module 01');
    const m = [
      ['Opus', 'claude-opus-5-5', '\u25CF\u25CB\u25CB', '$$$$$', 'Cross-program impact analysis, reverse-engineering an undocumented batch system, architecture decisions. Use when quality matters more than time.', COL.purple],
      ['Sonnet', 'claude-sonnet-5-5', '\u25CF\u25CF\u25CB', '$$$', 'Most daily work: COBOL changes, test scripts, documentation, code review. The safe default.', COL.teal],
      ['Haiku', 'claude-haiku-5-5', '\u25CF\u25CF\u25CF', '$', 'High-volume, simple tasks: formatting copybook documentation, bulk checks of job headers, quick lookups. Alias: claude-haiku-4-5.', COL.orange],
    ];
    m.forEach((k, i) => {
      const y = 1.3 + i * 1.65;
      box(s, 0.5, y, 12.33, 1.5, { fill: COL.panel });
      txt(s, k[0], 0.7, y + 0.12, 1.8, 0.5, { size: 24, bold: true, color: k[5] });
      txt(s, k[1], 0.7, y + 0.72, 3.0, 0.35, { size: 12, font: 'Courier New', color: COL.muted });
      txt(s, 'Speed ' + k[2], 3.9, y + 0.12, 2.2, 0.35, { size: 13, color: COL.text });
      txt(s, 'Cost ' + k[3], 3.9, y + 0.55, 2.2, 0.35, { size: 13, color: COL.text });
      txt(s, [{ text: 'Best for: ', options: { bold: true, color: k[5] } }, { text: k[4] }], 6.2, y + 0.1, 6.4, 1.3, { size: 13.5, valign: 'middle' });
    });
    banner(s, 'When unsure, start with Sonnet. Upgrade to Opus for genuinely complex tasks. Drop to Haiku for volume.', COL.purple);
  }

  // 16 ---- tokens divider
  section(pres, 'MODULE 01', 'Tokens & Context Windows',
    'The engine constraints that shape cost, quality, and what is possible in a session.', null, COL.purple);

  // 17 ---- tokens detail
  {
    const s = content(pres, 'Tokens, Context Windows & Compaction', 'Module 01');
    txt(s, 'What is a token?', 0.5, 1.25, 6, 0.4, { size: 16, bold: true, color: COL.teal });
    txt(s, 'A token is a subword fragment: not a character, not a word.', 0.5, 1.7, 6.0, 0.55, { size: 13, color: COL.muted });
    table(s, [['Text', 'Tokens'], ['"Hello"', '1 token'], ['"Hello, world!"', '4 tokens'], ['"Refactoring"', '3 tokens'], ['1,000 words', '~750 tokens'], ['100-line source file', '~700 tokens (varies by language)']],
      0.5, 2.35, [3.0, 3.0], { size: 13, rowH: 0.5 });
    txt(s, 'Output tokens cost more than input tokens.', 0.5, 5.5, 6.0, 0.4, { size: 13, bold: true, color: COL.orange });
    txt(s, 'The context window', 6.9, 1.25, 5.9, 0.4, { size: 16, bold: true, color: COL.teal });
    ['System prompt / CLAUDE.md', 'Conversation history', 'Files loaded into context', 'Tool results and output', "Claude's response"].forEach((t, i) => {
      const cs = [COL.purple, COL.teal, COL.cyan, COL.orange, COL.green];
      box(s, 6.9, 1.75 + i * 0.62, 5.93, 0.52, { fill: COL.panel, line: cs[i] });
      txt(s, t, 7.05, 1.75 + i * 0.62, 5.6, 0.52, { size: 13.5, valign: 'middle', color: cs[i] });
    });
    txt(s, 'A 200K token window is about 150K words. Filling it degrades quality. Run /context to see what is using space. COBOL programs and copybooks can be long: load only the ones you need.', 6.9, 4.95, 5.93, 1.3, { size: 13, color: COL.muted });
    banner(s, 'Auto-compaction runs as the window fills (the exact threshold depends on your version). Manual: /compact [hint]. Fresh start: /clear.', COL.orange);
  }

  // 18 ---- context best practices
  {
    const s = content(pres, 'Context Window Best Practices', 'Module 01');
    const c = [
      ['1  Load only what you need', "Point Claude to specific files. 'Read src/INTCALC.cbl' uses far fewer tokens than 'read everything in src/'."],
      ['2  Put critical context first', 'Earlier tokens carry more weight. Put constraints, CLAUDE.md rules and key facts before the task description.'],
      ['3  Watch your rate limit', 'Run /usage: shows the % of your 5-hour allowance used and the exact reset time. Start every day here.'],
      ['4  Compact at milestones',"Don't wait for poor answers. Compact after finishing a program or change while context is still clean."],
      ['5  One task per session', 'A fresh session for an unrelated task is cheaper than carrying dead context. Use /clear between workstreams.'],
      ['6  Keep CLAUDE.md lean', 'Every line loads on every session. Audit it regularly. Remove outdated rules and merge duplicates.'],
    ];
    c.forEach((k, i) => titled(s, 0.5 + (i % 3) * 4.18, 1.25 + Math.floor(i / 3) * 1.7, 3.95, 1.6, k[0], k[1], [COL.teal, COL.purple, COL.orange][i % 3], { size: 12.5, tsize: 14 }));
    txt(s, 'Symptoms of a bloated context. If you see these, compact immediately:', 0.5, 4.7, 12, 0.35, { size: 14, bold: true, color: COL.orange });
    ['Claude ignores rules from earlier in the session', 'Responses get shorter and less detailed', 'Claude repeats the same caveats', "Earlier file changes are 'forgotten'", 'Output quality drops for no obvious reason'].forEach((t, i) => {
      pill(s, t, 0.5 + i * 2.49, 5.1, 2.35, 1.0, COL.orange, 12);
    });
    banner(s, 'Rule: a 200K window is not an invitation to fill it. Quality degrades well before the limit. Use /usage daily.', COL.teal);
  }

  // 19 ---- PACT intro
  {
    const s = content(pres, 'Interacting with Agentic AI: The PACT Framework', 'Module 01');
    txt(s, 'A native Claude Code workflow for consistent, high-quality results, every session.', 0.5, 1.4, 5.2, 1.0, { size: 18, color: COL.muted });
    txt(s, 'On a mainframe change, skipping Approve is the expensive mistake: a wrong assumption about a copybook or a numeric field is cheap to fix in a plan and costly to find in a batch run.', 0.5, 2.7, 5.2, 2.0, { size: 14 });
    const r = [['P', 'Plan', '/plan mode + provide context', COL.purple], ['A', 'Approve', 'Read, review and approve the plan', COL.teal], ['C', 'Code', 'Generate based on the approved plan', COL.orange], ['T', 'Test', 'Run tests, fix, iterate', COL.red]];
    r.forEach((k, i) => {
      const y = 1.3 + i * 1.3;
      box(s, 6.3, y, 6.53, 1.15, { fill: COL.panel });
      badge(s, k[0], 6.5, y + 0.2, 0.75, k[3]);
      txt(s, k[1], 7.45, y + 0.15, 4.5, 0.45, { size: 20, bold: true });
      txt(s, k[2], 7.45, y + 0.62, 5.2, 0.4, { size: 14, color: COL.muted });
    });
  }

  // 20 ---- PACT step by step
  {
    const s = content(pres, 'The PACT Framework \u2014 Step by Step', 'Module 01');
    const c = [
      ['P', 'Plan', COL.purple, 'Activate /plan mode and give your full context: compiler, copybooks, DD names, conventions, constraints and the task.', 'Claude thinks through the approach before touching any code.'],
      ['A', 'Approve', COL.teal, 'Read the plan Claude generated. Check for misunderstandings, missing steps and wrong assumptions.', 'Correct it if needed, then explicitly approve before moving forward.'],
      ['C', 'Code', COL.orange, 'Now let Claude generate. Because the plan is approved, the output is targeted and aligned.', 'Go one program or paragraph at a time to keep context quality high.'],
      ['T', 'Test', COL.red, 'Never accept output blindly. Compile, run the job, paste errors back to Claude and let it fix them.', 'This closes the agentic loop: gather, plan, act, iterate.'],
    ];
    c.forEach((k, i) => {
      const x = 0.5 + i * 3.1;
      box(s, x, 1.3, 2.95, 5.0, { fill: COL.panel });
      badge(s, k[0], x + 0.2, 1.45, 0.7, k[2]);
      txt(s, k[1], x + 1.05, 1.5, 1.8, 0.6, { size: 22, bold: true, valign: 'middle' });
      txt(s, k[3], x + 0.2, 2.35, 2.55, 1.9, { size: 13.5 });
      txt(s, k[4], x + 0.2, 4.4, 2.55, 1.7, { size: 13.5, color: COL.muted });
    });
  }

  // 21 ---- PACT in practice
  {
    const s = content(pres, 'PACT in Practice \u2014 Real Example', 'Module 01');
    box(s, 0.5, 1.2, 12.33, 0.48, { fill: COL.panel, line: COL.cyan });
    txt(s, 'Scenario: add a monthly maintenance fee to the LEDGER-ME interest program (INTCALC)', 0.7, 1.2, 11.9, 0.48, { size: 14, bold: true, color: COL.cyan, valign: 'middle' });
    const r = [
      ['P', 'Plan', '/plan mode', COL.purple, '"Go to /plan mode: read INTCALC.cbl and copybooks/ACCTREC.cpy. Add a monthly fee for active accounts under a threshold. Fee amount and threshold come from a parameter file read through DD PARMIN. ACCTREC must stay 60 bytes. Fixed format, match the existing paragraph style. No code yet."'],
      ['A', 'Approve', 'Review output', COL.teal, '"[Read the plan] Looks good. Step 2 must also end the job with return code 12 if PARMIN is missing. Update the plan, then proceed."'],
      ['C', 'Code', 'Generate', COL.orange, '"Plan approved. Implement INTCALC.cbl only, one paragraph at a time. Do not touch ACCTUPD or STMTRPT yet."'],
      ['T', 'Test', 'Run and iterate', COL.red, '"Run sh scripts/run_all.sh. Here is the output: [INTCALC RC=12, PARMIN not found]. Fix it and re-run."'],
    ];
    r.forEach((k, i) => {
      const y = 1.8 + i * 1.12;
      box(s, 0.5, y, 12.33, 1.04, { fill: COL.panel });
      badge(s, k[0], 0.65, y + 0.14, 0.72, k[3]);
      txt(s, k[1], 1.55, y + 0.12, 1.6, 0.36, { size: 15, bold: true });
      pill(s, k[2], 1.55, y + 0.55, 1.6, 0.34, k[3], 11);
      txt(s, k[4], 3.4, y + 0.04, 9.3, 0.96, { size: 12, italic: true, color: COL.cyan, valign: 'middle' });
    });
    banner(s, 'Each step builds on the previous: context informs the plan, the plan drives the code, the test closes the loop.', COL.teal);
  }

  // 22 ---- practice
  {
    const s = content(pres, "Let's Practice \u2014 Your Turn", 'Module 01');
    box(s, 0.5, 1.25, 12.33, 1.25, { fill: COL.panel, line: COL.cyan });
    txt(s, 'Scenario', 0.7, 1.3, 3, 0.35, { size: 14, bold: true, color: COL.cyan });
    txt(s, 'In LEDGER-ME, ACCTUPD rejects withdrawals that would overdraw an account. Add a new reject reason, OVERLMT, for any single withdrawal above 5,000.00.', 0.7, 1.7, 11.9, 0.75, { size: 14 });
    const q = [
      ['P', 'Plan', 'What would you type in /plan mode?', '(task description + context: compiler, copybooks, conventions, constraints)', COL.purple],
      ['A', 'Approve', 'What would you check in the plan?', '(steps, assumptions, anything missing or wrong? what about a withdrawal exactly at the limit?)', COL.teal],
      ['C', 'Code', 'How would you ask for the code?', '(which paragraph first? scope? one change or the full feature?)', COL.orange],
      ['T', 'Test', 'What would you test first?', '(what command to run? what if it fails, what do you do?)', COL.red],
    ];
    q.forEach((k, i) => {
      const x = 0.5 + (i % 2) * 6.25, y = 2.7 + Math.floor(i / 2) * 1.6;
      box(s, x, y, 6.08, 1.45, { fill: COL.panel });
      badge(s, k[0], x + 0.15, y + 0.15, 0.55, k[4]);
      txt(s, k[2], x + 0.85, y + 0.12, 5.1, 0.4, { size: 15, bold: true });
      txt(s, k[3], x + 0.85, y + 0.6, 5.1, 0.8, { size: 12.5, color: COL.muted });
    });
    txt(s, 'Debrief: Did you use /plan mode? Was your context specific? Did you actually approve before coding? What would you test first?', 0.5, 5.95, 12.3, 0.8, { size: 13, color: COL.muted });
  }

  // 23 ---- extensions divider
  section(pres, 'MODULE 01', 'Claude Code Extension', 'CLAUDE.md, skills, commands and agents.',
    ['CLAUDE.md: project memory', 'Skills: reusable task expertise', 'Commands: built-in and custom', 'Agents and MCP'], COL.purple);

  // 24 ---- what belongs in CLAUDE.md
  {
    const s = content(pres, 'What Belongs in CLAUDE.md', 'Module 01');
    const c = [
      ['Stack & Versions', 'GnuCOBOL 3.2, fixed format (columns 8-72). Target: IBM Enterprise COBOL on z/OS. Python 3 for tests.', COL.teal],
      ['Project Structure', 'src/ programs \u00B7 copybooks/ record layouts \u00B7 data/ test files \u00B7 scripts/ run jobs \u00B7 docs/ rules', COL.purple],
      ['Commands', 'sh scripts/run_all.sh \u00B7 python tests/oracle_check.py, so Claude can verify its own work', COL.orange],
      ['Coding Conventions', 'Uppercase, numbered paragraphs (0000, 1000...) \u00B7 files through DD names, never paths \u00B7 match the existing style', COL.cyan],
      ['Anti-Patterns (Do NOT)', 'Never hard-code file names. Never change a copybook without recompiling every program. Never use real customer data.', COL.red],
      ['Key References', 'Record layouts: copybooks/ACCTREC.cpy \u00B7 Business rules: docs/legacy/POLICY-MEMO.txt', COL.green],
    ];
    c.forEach((k, i) => titled(s, 0.5 + (i % 3) * 4.18, 1.3 + Math.floor(i / 3) * 2.5, 3.95, 2.35, k[0], k[1], k[2], { size: 14, tsize: 16 }));
  }

  // 25 ---- CLAUDE.md example
  {
    const s = content(pres, 'CLAUDE.md \u2014 Real Project Example', 'Module 01');
    code(s, 'CLAUDE.md', [
      ['# CLAUDE.md', COL.green], ['## Stack', COL.cyan],
      ['- GnuCOBOL 3.2, fixed format, cols 8-72', COL.text], ['- Target: IBM Enterprise COBOL on z/OS', COL.text], ['- A local run is a smoke test, not proof', COL.text],
      ['## Project Structure', COL.cyan], ['src/       ACCTUPD INTCALC STMTRPT', COL.text], ['copybooks/ ACCTREC (60) TRANREC (40)', COL.text],
      ['## Commands', COL.cyan], ['sh scripts/run_all.sh   # compile, run', COL.text],
      ['## Conventions', COL.cyan], ['- Files by DD_name variables, no paths', COL.text], ['- Numbered paragraphs, uppercase', COL.text], ['- Check copybook offsets first', COL.text],
      ['## Do NOT', COL.red], ['- Never use real customer data', COL.red], ['- Never edit data/*.DAT by hand', COL.red], ['- Never change a copybook without', COL.red], ['  recompiling all three programs', COL.red],
    ], 0.5, 1.25, 6.2, 5.05, 12);
    titled(s, 7.0, 1.25, 5.83, 2.15, 'Why each section matters',
      'Stack: exact versions prevent wrong assumptions.\nCommands: Claude runs the job after every change to verify.\nConventions: team patterns enforced automatically.\nDo NOT: explicit exclusions are respected every time.', COL.teal, { size: 12.5, tsize: 15 });
    titled(s, 7.0, 3.55, 5.83, 1.45, 'Pro tips',
      'Keep it concise: every line costs tokens. Commit CLAUDE.md with the code. Add a rule whenever Claude makes the same wrong assumption twice.', COL.orange, { size: 12.5, tsize: 15 });
    titled(s, 7.0, 5.15, 5.83, 1.15, 'Many applications in one repo',
      'repo/CLAUDE.md = shop-wide rules. batch/CLAUDE.md = batch rules. online/CLAUDE.md = CICS rules.', COL.purple, { size: 12.5, tsize: 15 });
  }

  // 26 ---- skills divider
  section(pres, 'MODULE 01', 'Claude Skills', 'SKILL.md files that encode best practices, so Claude reads them once and applies them every time.', null, COL.purple);

  // 27 ---- skills
  {
    const s = content(pres, 'Skills \u2014 Reusable Task Expertise', 'Module 01');
    txt(s, 'What is a skill?', 0.5, 1.25, 6, 0.4, { size: 16, bold: true, color: COL.teal });
    txt(s, 'A SKILL.md file in .claude/skills/ with curated instructions. Claude reads the relevant skill before starting that kind of task, so you do not re-explain best practice each time.', 0.5, 1.7, 5.9, 1.8, { size: 14, color: COL.muted });
    titled(s, 0.5, 3.6, 5.9, 1.4, 'Course skills you will use',
      'spec-writer \u00B7 spec-scorer \u00B7 pact-workflow \u00B7 prompt-coach \u00B7 claude-md-builder \u00B7 cobol-local-compile-run', COL.teal, { size: 13 });
    [['Public skills', '/mnt/skills/public/  Platform-provided (docx, pptx, pdf...)', COL.purple], ['User skills', '/mnt/skills/user/  Your custom workflows', COL.orange], ['Example skills', '/mnt/skills/examples/  Reference implementations', COL.cyan]].forEach((k, i) => {
      titled(s, 6.9, 1.3 + i * 1.6, 5.93, 1.45, k[0], k[1], k[2], { size: 13 });
    });
    banner(s, 'Skills encode expertise once. Every future task of that type benefits automatically.', COL.purple);
  }

  // 28 ---- commands divider
  section(pres, 'MODULE 01', 'Claude Commands', 'Built-in slash commands, plus custom commands that automate recurring workflows.', null, COL.purple);

  // 29 ---- commands
  {
    const s = content(pres, 'Built-in Commands & Custom Commands', 'Module 01');
    txt(s, 'Built-in slash commands', 0.5, 1.25, 6, 0.4, { size: 16, bold: true, color: COL.teal });
    table(s, [['Command', 'What it does'], ['/clear', 'Clear conversation history, free up context'], ['/compact', 'Clear history, keep a summary. /compact [hint]'], ['/cost', 'Show total cost and duration of the session'],
      ['/doctor', 'Diagnose installation and settings'], ['/memory', 'Edit Claude memory files'], ['/status', 'Show version, model, account, API connectivity'], ['/diff', 'View uncommitted changes and per-turn diffs'],
      ['/commit', 'Create a git commit from staged changes'], ['/review', 'Review a pull request'], ['/security-review', 'Security review of pending branch changes']],
      0.5, 1.7, [1.9, 4.2], { size: 12, rowH: 0.43, mono: [0] });
    txt(s, 'Custom commands', 6.9, 1.25, 6, 0.4, { size: 16, bold: true, color: COL.teal });
    txt(s, 'Create .claude/commands/cobol-review.md, then type /cobol-review to run it.', 6.9, 1.7, 5.93, 0.55, { size: 13, color: COL.muted });
    code(s, '.claude/commands/cobol-review.md', [
      ['# COBOL Review Checklist', COL.green], ['# Usage: /cobol-review <file>', COL.muted], ['', COL.text], ['Review the named program:', COL.text], ['- FILE STATUS tested after every I/O', COL.text],
      ['- No MOVE of a signed field to unsigned', COL.text], ['- COMPUTE has ROUNDED where cents matter', COL.text], ['- Accumulators reset for every record', COL.text],
      ['- Boundary tests use >= or > as the rule says', COL.text], ['- No GO TO leaves its paragraph range', COL.text], ['', COL.text], ['Output PASS/FAIL per item with file+line.', COL.text]], 6.9, 2.3, 5.93, 3.9, 12);
    banner(s, 'Commands are version-controlled. They ship with the repo and improve over time.', COL.purple);
  }

  // 30 ---- agents divider
  section(pres, 'MODULE 01', 'Claude Agents & MCP', 'Autonomous multi-step workflows, and connecting Claude to external tools through MCP.', null, COL.purple);

  // 31 ---- agentic loop and MCP
  {
    const s = content(pres, 'Agentic Loop & Model Context Protocol', 'Module 01');
    txt(s, 'The agentic loop', 0.5, 1.25, 6, 0.4, { size: 16, bold: true, color: COL.teal });
    [['1', 'Goal given', 'Developer gives a high-level task', COL.purple], ['2', 'Agent plans', 'Claude generates an implementation plan', COL.teal], ['3', 'Agent acts', 'Writes code, runs tests, fixes failures', COL.orange], ['4', 'Observe', 'Reads output, checks against criteria', COL.cyan], ['5', 'Done / ask', 'Criteria met, or it needs human input', COL.green]].forEach((k, i) => {
      const y = 1.75 + i * 0.82;
      badge(s, k[0], 0.5, y + 0.05, 0.5, k[3]);
      txt(s, k[1], 1.15, y, 2.2, 0.35, { size: 14, bold: true });
      txt(s, k[2], 1.15, y + 0.35, 5.2, 0.35, { size: 12.5, color: COL.muted });
    });
    box(s, 0.5, 5.85, 6.0, 0.5, { fill: COL.panel });
    txt(s, 'Safe practice: review the plan, keep git as a safety net, set scope limits.', 0.6, 5.85, 5.8, 0.5, { size: 11.5, color: COL.orange, valign: 'middle' });
    txt(s, 'MCP: external tools', 6.9, 1.25, 6, 0.4, { size: 16, bold: true, color: COL.teal });
    txt(s, 'Model Context Protocol connects agents to external services.', 6.9, 1.7, 5.9, 0.5, { size: 13, color: COL.muted });
    [['Atlassian / Jira', 'Read and write tickets'], ['Linear', 'Issues and sprints'], ['GitHub', 'PRs, issues, repos'], ['Figma', 'Design files'], ['Notion', 'Pages and databases'], ['HubSpot', 'CRM records']].forEach((k, i) => {
      const x = 6.9 + (i % 2) * 3.0, y = 2.35 + Math.floor(i / 2) * 1.2;
      titled(s, x, y, 2.9, 1.08, k[0], k[1], COL.cyan, { size: 12.5, tsize: 14 });
    });
    banner(s, 'Before connecting any tool to a mainframe project, check with your security team what data it can reach.', COL.orange);
  }
};

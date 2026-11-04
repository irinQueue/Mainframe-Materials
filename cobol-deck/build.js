// Build: node build.js   (set NODE_PATH to the global npm modules so pptxgenjs resolves)
const path = require('path');
const { newDeck, THEME, warnings } = require('./lib');
// Folder of the pptx skill (the one that contains scripts/apply_theme.js).
// Set PPTX_SKILL_DIR before running; it is machine-specific, so it is not hard-coded.
const SKILL = process.env.PPTX_SKILL_DIR;
if (!SKILL) { console.error('Set PPTX_SKILL_DIR to the pptx skill folder first.'); process.exit(1); }
const { applyTheme } = require(path.join(SKILL, 'scripts', 'apply_theme.js'));

(async () => {
  const pres = newDeck();
  require('./part1')(pres);
  require('./part2')(pres);
  require('./part3')(pres);
  const out = path.resolve(__dirname, '..', 'Claude Code for Mainframe COBOL Developers.pptx');
  await pres.writeFile({ fileName: out });
  await applyTheme(out, THEME);
  console.log('wrote', out);
  console.log('slides:', pres.slides.length);
  console.log('fit warnings:', warnings.length);
  warnings.forEach((w) => console.log(' -', w));
})().catch((e) => { console.error(e); process.exit(1); });

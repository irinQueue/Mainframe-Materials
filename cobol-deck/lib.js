// Shared theme, layouts and helpers for the COBOL edition of "Mastering Claude Code".
// Slide size is 13.333 x 7.5 in (LAYOUT_WIDE). Colours are hex without '#'.
const path = require('path');
const pptxgen = require('pptxgenjs');

const COL = {
  bg: '0F1626', panel: '1A2338', panel2: '222D48', code: '0B1020',
  text: 'E8EDF5', muted: 'A3B0C7', line: '33405F',
  teal: '14B8A6', purple: '8B5CF6', orange: 'F59E0B', red: 'EF4444', cyan: '22D3EE', green: '34D399',
};
const THEME = {
  name: 'Mainframe Dark',
  headFontFace: 'Calibri',
  bodyFontFace: 'Calibri',
  colors: {
    dk1: COL.bg, lt1: 'FFFFFF', dk2: COL.panel, lt2: COL.text,
    accent1: COL.teal, accent2: COL.purple, accent3: COL.orange,
    accent4: COL.red, accent5: COL.cyan, accent6: COL.green,
    hlink: COL.cyan, folHlink: COL.muted,
  },
};
const FOOT = 'Internal Use Only — Do Not Share Outside the Organization';

const warnings = [];

function newDeck() {
  const pres = new pptxgen();
  pres.layout = 'LAYOUT_WIDE';
  pres.title = 'Mastering Claude Code for Mainframe COBOL Developers';
  pres.author = 'Training team';
  pres.theme = { headFontFace: THEME.headFontFace, bodyFontFace: THEME.bodyFontFace };

  const footer = [
    { text: { text: FOOT, options: { x: 0.5, y: 7.08, w: 8.5, h: 0.3, fontSize: 10, color: COL.muted, fontFace: 'Calibri', margin: 0, isTextBox: true } } },
  ];
  const num = { x: 12.2, y: 7.08, w: 0.65, h: 0.3, fontSize: 10, color: COL.muted, align: 'right' };

  pres.defineSlideMaster({
    title: 'CONTENT', background: { color: COL.bg },
    objects: [
      { placeholder: { options: { name: 'title', type: 'title', x: 0.5, y: 0.3, w: 10.6, h: 0.8, fontFace: 'Calibri', fontSize: 30, bold: true, color: COL.text, valign: 'middle', margin: 0 }, text: '' } },
      ...footer,
    ],
    slideNumber: num,
  });
  pres.defineSlideMaster({
    title: 'SECTION', background: { color: COL.bg },
    objects: [
      { placeholder: { options: { name: 'title', type: 'title', x: 0.9, y: 2.55, w: 7.0, h: 1.7, fontFace: 'Calibri', fontSize: 48, bold: true, color: COL.text, valign: 'top', margin: 0 }, text: '' } },
      ...footer,
    ],
    slideNumber: num,
  });
  pres.defineSlideMaster({
    title: 'COVER', background: { color: COL.bg },
    objects: [
      { placeholder: { options: { name: 'title', type: 'title', x: 0.9, y: 1.9, w: 11.5, h: 1.6, fontFace: 'Calibri', fontSize: 60, bold: true, color: COL.text, valign: 'top', margin: 0 }, text: '' } },
    ],
  });
  return pres;
}

// ---- text fit estimate (no renderer is available, so every box is checked here) ----
function est(plain, w, h, size, mono, label, margin) {
  const cw = mono ? 0.62 : 0.52;
  const inner = Math.max(0.2, w - 2 * (margin / 72));
  let lines = 0;
  for (const para of String(plain).split('\n')) {
    const wi = (para.length * cw * size) / 72;
    lines += Math.max(1, Math.ceil(wi / inner));
  }
  const need = (lines * size * 1.22) / 72 + 2 * (margin / 72);
  if (need > h * 1.03) warnings.push(`${label || ''} needs ${need.toFixed(2)}in, box is ${h.toFixed(2)}in: "${String(plain).slice(0, 48)}"`);
}

let CUR = '';
function setCur(s) { CUR = s; }

function txt(s, t, x, y, w, h, o = {}) {
  const size = o.size || 14;
  const mono = o.font === 'Courier New';
  const margin = o.margin === undefined ? 3 : o.margin;
  const plain = Array.isArray(t)
    ? t.map((r) => (typeof r === 'string' ? r : r.text) + (r.options && r.options.breakLine ? '\n' : '')).join('')
    : t;
  est(plain, w, h, size, mono, CUR, margin);
  s.addText(t, {
    x, y, w, h, fontFace: o.font || 'Calibri', fontSize: size, color: o.color || COL.text,
    bold: o.bold, italic: o.italic, align: o.align || 'left', valign: o.valign || 'top',
    margin, isTextBox: true, paraSpaceAfter: o.gap, lineSpacingMultiple: o.ls,
    charSpacing: o.cs,
  });
}

function box(s, x, y, w, h, o = {}) {
  s.addShape(o.round === false ? 'rect' : 'roundRect', {
    x, y, w, h, rectRadius: o.round === false ? undefined : (o.r || 0.08),
    fill: { color: o.fill || COL.panel },
    line: o.line ? { color: o.line, width: o.lw || 1 } : { color: o.fill || COL.panel, width: 0 },
  });
}

function badge(s, letter, x, y, size, color) {
  s.addShape('roundRect', { x, y, w: size, h: size, rectRadius: 0.06, fill: { color }, line: { color, width: 0 } });
  txt(s, letter, x, y, size, size, { size: Math.round(size * 34), bold: true, align: 'center', valign: 'middle', color: 'FFFFFF', margin: 0 });
}

function pill(s, text, x, y, w, h, color, size) {
  s.addShape('roundRect', { x, y, w, h, rectRadius: 0.06, fill: { color: COL.bg }, line: { color, width: 1.25 } });
  txt(s, text, x, y, w, h, { size: size || 12, align: 'center', valign: 'middle', color, margin: 2 });
}

function banner(s, text, color) {
  const c = color || COL.teal;
  s.addShape('roundRect', { x: 0.5, y: 6.38, w: 12.33, h: 0.52, rectRadius: 0.06, fill: { color: COL.bg }, line: { color: c, width: 1.25 } });
  txt(s, text, 0.7, 6.38, 11.93, 0.52, { size: 14, bold: true, color: c, valign: 'middle', margin: 2 });
}

function modTag(s, text) {
  txt(s, text, 11.0, 0.45, 1.83, 0.4, { size: 13, color: COL.muted, align: 'right' });
}

// lines: strings, or [text, colour] pairs
function code(s, name, lines, x, y, w, h, size) {
  const sz = size || 12;
  s.addShape('roundRect', { x, y, w, h, rectRadius: 0.06, fill: { color: COL.code }, line: { color: COL.line, width: 1 } });
  s.addShape('rect', { x: x + 0.01, y: y + 0.01, w: w - 0.02, h: 0.4, fill: { color: COL.panel2 }, line: { color: COL.panel2, width: 0 } });
  txt(s, name, x + 0.15, y + 0.02, w - 0.3, 0.36, { size: 11, color: COL.muted, valign: 'middle', font: 'Courier New' });
  const runs = lines.map((l, i) => {
    const t = Array.isArray(l) ? l[0] : l;
    const c = Array.isArray(l) ? l[1] : COL.text;
    return { text: t, options: { color: c, breakLine: i < lines.length - 1 } };
  });
  txt(s, runs, x + 0.15, y + 0.48, w - 0.3, h - 0.56, { size: sz, font: 'Courier New' });
}

// A new content slide with the title placeholder filled and the module tag on the right.
function content(pres, title, mod) {
  const s = pres.addSlide({ masterName: 'CONTENT' });
  setCur(title);
  s.addText(title, { placeholder: 'title' });
  if (mod) modTag(s, mod);
  return s;
}

function section(pres, mod, title, sub, items, accent) {
  const s = pres.addSlide({ masterName: 'SECTION' });
  setCur(title);
  s.addText(title, { placeholder: 'title' });
  txt(s, mod, 0.9, 2.0, 5, 0.4, { size: 16, bold: true, color: accent || COL.teal, cs: 4 });
  txt(s, sub, 0.9, 4.45, 6.6, 1.2, { size: 18, color: COL.muted });
  if (items && items.length) {
    box(s, 8.4, 1.7, 4.43, 4.5, { fill: COL.panel });
    txt(s, 'In this module', 8.7, 1.85, 3.9, 0.4, { size: 14, bold: true, color: accent || COL.teal });
    const runs = items.map((t, i) => ({ text: t, options: { bullet: true, breakLine: i < items.length - 1 } }));
    txt(s, runs, 8.7, 2.35, 3.95, 3.7, { size: 16, gap: 8 });
  }
  return s;
}

module.exports = { COL, THEME, newDeck, content, section, txt, box, badge, pill, banner, code, modTag, warnings, setCur, FOOT };

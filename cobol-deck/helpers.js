// Layout helpers built on lib.js: numbered steps, tables, titled cards.
const { COL, txt, box, badge, warnings } = require('./lib');

// items: [title, description]. Returns the y after the last step.
function steps(s, items, x, y, w, o = {}) {
  const gap = o.gap || 1.1;
  const color = o.color || COL.teal;
  items.forEach((it, i) => {
    const yy = y + i * gap;
    s.addShape('ellipse', { x, y: yy + 0.02, w: 0.36, h: 0.36, fill: { color }, line: { color, width: 0 } });
    txt(s, String(i + 1), x, yy + 0.02, 0.36, 0.36, { size: 13, bold: true, align: 'center', valign: 'middle', color: 'FFFFFF', margin: 0 });
    txt(s, it[0], x + 0.5, yy, w - 0.5, 0.34, { size: o.tsize || 15, bold: true, valign: 'middle' });
    txt(s, it[1], x + 0.5, yy + 0.36, w - 0.5, gap - 0.42, { size: o.size || 13, color: COL.muted });
  });
}

// rows: array of arrays of strings; first row is the header.
function table(s, rows, x, y, colW, o = {}) {
  const size = o.size || 12;
  const rowH = o.rowH || 0.5;
  const data = rows.map((r, ri) => r.map((c, ci) => ({
    text: c,
    options: {
      fontFace: o.mono && o.mono.includes(ci) ? 'Courier New' : 'Calibri',
      fontSize: ri === 0 ? size : size,
      bold: ri === 0 || (o.boldCol === ci),
      color: ri === 0 ? COL.text : (o.colColors && o.colColors[ci]) || COL.text,
      fill: { color: ri === 0 ? COL.panel2 : (ri % 2 ? COL.panel : COL.bg) },
      valign: 'middle',
      margin: [2, 6, 2, 6],
    },
  })));
  const w = colW.reduce((a, b) => a + b, 0);
  // fit check per cell
  rows.forEach((r, ri) => r.forEach((c, ci) => {
    const cw = (o.mono && o.mono.includes(ci)) ? 0.62 : 0.52;
    const lines = Math.max(1, Math.ceil((String(c).length * cw * size) / 72 / Math.max(0.3, colW[ci] - 0.17)));
    const need = (lines * size * 1.22) / 72 + 0.06;
    if (need > rowH * 1.04) warnings.push(`table cell needs ${need.toFixed(2)}in, row is ${rowH}in: "${String(c).slice(0, 40)}"`);
  }));
  s.addTable(data, { x, y, w, colW, rowH, border: { type: 'solid', color: COL.line, pt: 0.75 }, autoPage: false });
}

// A titled card: heading in colour plus body text.
function titled(s, x, y, w, h, title, body, color, o = {}) {
  box(s, x, y, w, h, { fill: o.fill || COL.panel });
  txt(s, title, x + 0.15, y + 0.1, w - 0.3, 0.36, { size: o.tsize || 15, bold: true, color: color || COL.teal });
  txt(s, body, x + 0.15, y + 0.5, w - 0.3, h - 0.58, { size: o.size || 13, color: o.bcolor || COL.text, gap: o.gap });
}

module.exports = { steps, table, titled };

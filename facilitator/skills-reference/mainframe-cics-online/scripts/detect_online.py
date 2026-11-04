#!/usr/bin/env python3
"""Classify a specification: does it contain CICS-style online work?

Works on any spec - technology-neutral BRDs/FSDs as well as specs that name
CICS, IBM i, IMS or ISPF. Scores every section (Markdown headings, numbered
headings in plain text, or HTML headings) for signals of:

  SCREEN    an interactive terminal screen (layout, fields, keys, cursor)
  SERVICE   a synchronous request/response program with no screen
  BATCH     scheduled / file-driven processing (counter-evidence)
  PLATFORM  the source platform the online part came from (CICS, IBM i, ...)
  STATUS    the screen is only proposed / optional / out of scope

It prints WHERE the evidence is (file, section, line, signal) - never the
spec's text unless --show-lines is given, because specs can carry sample
customer data.

Usage:
  detect_online.py SPEC [SPEC|DIR ...] [--json] [--show-lines] [--top N]

PDF/DOCX: extract to text first (file-ingestion skill), then run this.
Verdicts: ONLINE-SCREEN, ONLINE-SERVICE, MIXED, UNCERTAIN, BATCH-ONLY.
The verdict is evidence for the model's judgement, not a substitute for it.
"""
import argparse
import html
import json
import os
import re
import sys

TEXT_EXT = {'.md', '.markdown', '.txt', '.text', '.html', '.htm', '.rst', '.adoc'}

# (category, signal name, weight, regex). Case-insensitive.
SIGNALS = [
    # --- explicit CICS / 3270 vocabulary -----------------------------------
    ('SCREEN', 'cics', 10, r'\bCICS\b'),
    ('SCREEN', 'bms-map', 10, r'\bBMS\b|\bDFHMSD\b|\bDFHMDI\b|\bDFHMDF\b|\bmapset\b'),
    ('SCREEN', 'exec-cics', 10, r'EXEC\s+CICS'),
    ('SCREEN', 'pseudo-conversational', 8, r'pseudo[- ]?conversational'),
    ('SCREEN', '3270', 6, r'\b3270\b'),
    ('SERVICE', 'commarea', 8, r'\bCOMMAREA\b|communication area'),
    ('SERVICE', 'cics-link-xctl', 6, r'\bEXEC\s+CICS\s+(LINK|XCTL)\b|\bEXCI\b|\bDPL\b'),
    ('SCREEN', 'transaction-id', 5, r'\btrans(action)?[- ]?id\b|\btranid\b'),
    # --- other online platforms (source of a rebuild) ------------------------
    ('PLATFORM', 'ibmi-display-file', 8,
     r'display file|\bDSPF\b|\bEXFMT\b|\bDDS\b|\bsubfile\b|\b5250\b|workstation file|\bDSPATR\b'),
    ('PLATFORM', 'ims-dc', 8, r'\bIMS[ /-]?(DC|TM)\b|\bMFS\b|message processing (program|region)|\bMPP\b'),
    ('PLATFORM', 'ispf-dialog', 6, r'\bISPF\b.{0,20}(panel|dialog)|\bDISPLAY PANEL\b|\bISPEXEC\b'),
    ('PLATFORM', 'green-screen', 5, r'green[- ]screen'),
    ('PLATFORM', 'web-ui', 3, r'\bweb (page|form|ui|screen)\b|\bbrowser\b|\bHTML form\b'),
    # --- technology-neutral screen structure ---------------------------------
    ('SCREEN', 'screen-size-24x80', 8, r'\b24\s*(x|×|by|lines?\s*(x|×|by))\s*80\b'),
    ('SCREEN', 'screen-layout', 6,
     r'\b(screen|terminal|display|panel) (layout|record|map|format|definition|image)s?\b'),
    ('SCREEN', 'function-keys', 5,
     r'\bfunction keys?\b|\bP?F\d{1,2}\s*[=:(]|\bPF\d{1,2}\b|\bPA[123]\b|\bclear key\b|'
     r'\bF\d{1,2}\s+(keys?|exits?|ends?|returns?|refresh(es)?|cancels?|pages?|to|for|=)\b'),
    ('SCREEN', 'enter-key', 3, r'\b(press(es)?|hit|use)s? (the )?enter\b|\benter key\b'),
    ('SCREEN', 'cursor', 4, r'\bcursor\b'),
    ('SCREEN', 'entry-field', 4,
     r'\b(entry|input|enterable|unprotected|protected|key-?in) fields?\b'),
    ('SCREEN', 'field-attributes', 4,
     r'\bhigh intensity\b|\bunderlined?\b|\breverse video\b|\bnon-?display\b|\bbright\b'),
    ('SCREEN', 'message-line', 4, r'\b(message|error|status) line\b'),
    ('SCREEN', 'menu-navigation', 3, r'\bmain menu\b|\bmenu (option|selection)s?\b|\bnavigat(e|ion)\b'),
    ('SCREEN', 'paging', 3, r'\bpage (up|down|forward|backward)\b|\bscroll(ing)?\b|\bnext page\b'),
    ('SCREEN', 'screen-word', 2, r'\bscreens?\b'),
    # --- technology-neutral interaction / online behaviour ------------------
    ('INTERACT', 'operator-entry', 3,
     r'\b(operator|user|clerk|agent|teller|analyst)s? (enters?|types?|keys?|selects?|presses|chooses)\b'),
    ('INTERACT', 'inquiry', 2, r'\binquir(y|ies)\b|\benquir(y|ies)\b|\blook[- ]?(ups?|s up)\b|\bsearch(es)? for\b'),
    ('INTERACT', 'online-realtime', 3,
     r'\bon-?line\b|\breal[- ]time\b|\binteractive(ly)?\b|\bresponse time\b|\bconcurrent users\b'),
    ('INTERACT', 'wait-for-operator', 4,
     r'(while|when) (the )?(screen|operator|user) (waits?|is waiting)|think time'),
    ('SERVICE', 'sync-request', 3,
     r'\brequest[/ -]response\b|\bsynchronous(ly)? call|'
     r'\bcalled (synchronously )?by (the )?(screen|front[- ]end|channel|adapter|caller)|'
     r'\bunit of work (per|for each) (call|request)\b'),
    ('SERVICE', 'parameter-area', 2, r'\bparameter (area|list|block)\b|\bcall interface\b'),
    # --- batch (counter-evidence) --------------------------------------------
    ('BATCH', 'schedule', 3,
     r'\bnightly\b|\bend[- ]of[- ](day|month)\b|\bscheduler\b|\bscheduled (run|job)\b|\bbatch\b'),
    ('BATCH', 'job-steps', 3, r'\bjob (stream|step)s?\b|\bJCL\b|\bstep \d+\b'),
    ('BATCH', 'file-processing', 2,
     r'\binput file\b|\boutput file\b|\bsequential(ly)?\b|\brecord counts?\b|\btrailer record\b'),
    ('BATCH', 'restart', 2, r'\bcheckpoint\b|\brestart\b'),
    ('BATCH', 'report', 1, r'\breports?\b'),
    # --- status of a screen ----------------------------------------------------
    ('STATUS', 'proposed-or-optional', 0,
     r'\b(proposed|optional|future|not delivered|out of scope|not in scope|to be confirmed|nice to have)\b'),
]

# Phrases that look like screen evidence but are not.
FALSE_FRIENDS = [
    r'\bscreen(ed|ing|s)? (out|for|against)\b',
    r'\bscreening\b',
    r'\bprint[- ]?screen\b',
    r'\bscreen ?shots?\b',
    r'\bon-?line (help|documentation|manual|banking statement)\b',
]

COMPILED = [(c, n, w, re.compile(p, re.I)) for c, n, w, p in SIGNALS]
FALSE_RE = re.compile('|'.join(FALSE_FRIENDS), re.I)
RULER_RE = re.compile(r'^\s*1234567890(1234567890){3,}')     # 80-col ruler
LAYOUT_HDR_RE = re.compile(r'^\s*\|.*\b(row|line)\b.*\b(col(umn)?|pos(ition)?)\b.*\b(len(gth)?|size|width)\b', re.I)
MD_HEAD_RE = re.compile(r'^(#{1,6})\s+(.*)$')
NUM_HEAD_RE = re.compile(r'^(?:[A-Z]\.)?\d+(?:\.\d+)*\.?\s+[A-Z][^\n]{2,80}$')
HTML_HEAD_RE = re.compile(r'<h([1-6])[^>]*>(.*?)</h\1>', re.I | re.S)


def read_text(path):
    with open(path, 'rb') as f:
        raw = f.read()
    for enc in ('utf-8', 'cp1252', 'latin-1'):
        try:
            text = raw.decode(enc)
            break
        except UnicodeDecodeError:
            continue
    if path.lower().endswith(('.html', '.htm')):
        text = HTML_HEAD_RE.sub(lambda m: '\n' + '#' * int(m.group(1)) + ' ' +
                                re.sub(r'<[^>]+>', '', m.group(2)) + '\n', text)
        text = re.sub(r'<(script|style)[^>]*>.*?</\1>', ' ', text, flags=re.I | re.S)
        text = re.sub(r'<br\s*/?>|</p>|</tr>|</li>|</div>', '\n', text, flags=re.I)
        text = html.unescape(re.sub(r'<[^>]+>', ' ', text))
    return text.splitlines()


def sections_of(lines):
    """Yield (heading, first_line_no, [(line_no, text)])."""
    heading, start, body = '(start of file)', 1, []
    in_code = False
    for i, line in enumerate(lines, 1):
        if line.strip().startswith('```'):
            in_code = not in_code
        m = None if in_code else (MD_HEAD_RE.match(line) or
                                  (NUM_HEAD_RE.match(line.strip()) and len(line) < 90))
        if m:
            if body:
                yield heading, start, body
            heading = (m.group(2) if hasattr(m, 'group') and m.re is MD_HEAD_RE
                       else line.strip())[:90]
            start, body = i, [(i, heading)]          # the heading is evidence too
        else:
            body.append((i, line))
    if body:
        yield heading, start, body


def scan_section(body):
    hits = []          # (category, signal, weight, line_no)
    for ln, text in body:
        clean = FALSE_RE.sub(' ', text)
        for cat, name, weight, rx in COMPILED:
            if rx.search(clean):
                hits.append((cat, name, weight, ln))
        if RULER_RE.match(text):
            hits.append(('SCREEN', 'character-grid-ruler', 8, ln))
        if LAYOUT_HDR_RE.match(text):
            hits.append(('SCREEN', 'row-column-length-table', 9, ln))
    return hits


def score(hits):
    """Each distinct signal counts once per section at full weight, repeats add a little."""
    by_cat, seen = {}, {}
    for cat, name, weight, _ in hits:
        seen.setdefault((cat, name), [weight, 0])[1] += 1
    for (cat, name), (weight, n) in seen.items():
        by_cat[cat] = by_cat.get(cat, 0) + weight + min(n - 1, 4) * (weight // 4)
    return by_cat, sorted({n for (_, n) in seen})


def verdict(totals, distinct):
    screen = totals.get('SCREEN', 0) + totals.get('PLATFORM', 0)
    service = totals.get('SERVICE', 0)
    interact = totals.get('INTERACT', 0)
    batch = totals.get('BATCH', 0)
    strong = {'cics', 'bms-map', 'exec-cics', 'pseudo-conversational', 'screen-size-24x80',
              'character-grid-ruler', 'row-column-length-table', 'ibmi-display-file',
              'ims-dc', 'ispf-dialog', 'screen-layout'}
    structural = {'function-keys', 'cursor', 'entry-field', 'field-attributes',
                  'message-line', 'enter-key', 'menu-navigation', 'paging'}
    has_strong = bool(strong & distinct)
    n_struct = len(structural & distinct)
    online_screen = has_strong or n_struct >= 3
    online_service = ('commarea' in distinct or 'cics-link-xctl' in distinct
                      or (service >= 5 and (interact >= 3 or 'sync-request' in distinct)))
    has_batch = batch >= 5
    if online_screen:
        return 'MIXED' if has_batch else 'ONLINE-SCREEN'
    if online_service:
        return 'MIXED' if has_batch else 'ONLINE-SERVICE'
    if n_struct >= 1 or interact >= 5 or screen >= 8 or service >= 5:
        return 'UNCERTAIN'
    return 'BATCH-ONLY'


MEANING = {
    'ONLINE-SCREEN': 'interactive screen work - use mainframe-cics-online for it',
    'ONLINE-SERVICE': 'online request/response program(s), no screen - a CICS LINK/COMMAREA service',
    'MIXED': 'batch AND online parts - mainframe-application for batch, mainframe-cics-online for online',
    'UNCERTAIN': 'weak online hints only - read the listed sections and ask the user',
    'BATCH-ONLY': 'no online evidence - mainframe-application alone',
}


def collect(paths):
    files = []
    for p in paths:
        if os.path.isdir(p):
            for root, _, names in os.walk(p):
                files += [os.path.join(root, n) for n in sorted(names)
                          if os.path.splitext(n)[1].lower() in TEXT_EXT]
        elif os.path.isfile(p):
            files.append(p)
        else:
            sys.exit('not found: ' + p)
    return files


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('paths', nargs='+')
    ap.add_argument('--json', action='store_true', help='machine-readable output')
    ap.add_argument('--show-lines', action='store_true',
                    help='print the matched lines (may expose spec content - off by default)')
    ap.add_argument('--top', type=int, default=15, help='sections to list (default 15)')
    a = ap.parse_args()

    files = collect(a.paths)
    if not files:
        sys.exit('no readable text files (.md/.txt/.html); extract PDF/DOCX first')

    sections, totals, distinct = [], {}, set()
    for f in files:
        lines = read_text(f)
        for heading, start, body in sections_of(lines):
            hits = scan_section(body)
            if not hits:
                continue
            cats, names = score(hits)
            for c, v in cats.items():
                totals[c] = totals.get(c, 0) + v
            distinct |= set(names)
            online = cats.get('SCREEN', 0) + cats.get('PLATFORM', 0) + cats.get('SERVICE', 0) \
                + cats.get('INTERACT', 0)
            sections.append({
                'file': f, 'section': heading, 'line': start,
                'online_score': online, 'batch_score': cats.get('BATCH', 0),
                'signals': names,
                'status_flag': 'proposed-or-optional' in names,
                'lines': sorted({ln for c, n, w, ln in hits if c != 'BATCH'})[:12],
                'text': [lines[ln - 1].strip()[:110] for ln in
                         sorted({ln for c, n, w, ln in hits if c != 'BATCH'})[:6]]
                if a.show_lines else [],
            })

    v = verdict(totals, distinct)
    platforms = sorted(n for n in distinct if n in
                       {'cics', 'ibmi-display-file', 'ims-dc', 'ispf-dialog', 'web-ui', 'green-screen'})
    online_secs = sorted((s for s in sections if s['online_score'] > s['batch_score']
                          and s['online_score'] >= 8),
                         key=lambda s: -s['online_score'])
    result = {
        'verdict': v,
        'totals': totals,
        'source_platform_hints': platforms,
        'proposed_or_optional_screens_mentioned': any(s['status_flag'] for s in online_secs),
        'online_sections': online_secs[:a.top],
        'files_scanned': len(files),
    }
    if a.json:
        print(json.dumps(result, indent=2))
        return

    print('Files scanned : %d' % len(files))
    print('Verdict       : %s' % v)
    print('Meaning       : ' + MEANING[v])
    print('Totals        : ' + ', '.join('%s=%d' % kv for kv in sorted(totals.items())))
    print('Platform hints: ' + (', '.join(platforms) or 'none (technology-neutral)'))
    if result['proposed_or_optional_screens_mentioned']:
        print('NOTE          : some online sections say proposed/optional/out of scope - '
              'confirm scope with the user before building them.')
    print('\nSections with online evidence (highest first):')
    if not online_secs:
        print('  none')
    for s in online_secs[:a.top]:
        flag = '  [proposed/optional?]' if s['status_flag'] else ''
        print('  %4d online / %3d batch  %s:%d  %s%s' % (
            s['online_score'], s['batch_score'], os.path.basename(s['file']),
            s['line'], s['section'], flag))
        print('        signals: ' + ', '.join(s['signals']))
        print('        lines  : ' + ', '.join(map(str, s['lines'])))
        for t in s['text']:
            print('          > ' + t)


if __name__ == '__main__':
    main()

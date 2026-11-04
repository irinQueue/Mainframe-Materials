#!/usr/bin/env python3
"""Re-wrap fixed-format COBOL comment paragraphs that run past column 72.

Only comment lines ('*' in column 7) are touched, and only paragraphs that
contain a line longer than 72 characters. A paragraph is a comment line
followed by the comment lines whose text starts in the same column as the
paragraph's own text (the hanging indent of "* LABEL     : text" headers
and of plain "*    text" notes). Separator lines (*====, *----) and blank
comment lines end a paragraph. Words are never split; code lines are never
changed. Line ends are preserved (CR LF stays CR LF).

Usage: reflow_comments.py FILE [FILE ...]      (rewrites in place)
Exit 1 if a code line (not a comment) is still past column 72.
"""
import re
import sys

LABEL = re.compile(r'^( {6}\* [A-Z][A-Z0-9 ]{1,11}: )')


def text_col(line):
    """Column (0-based) where a comment line's text starts."""
    m = LABEL.match(line)
    if m:
        return len(m.group(1))
    body = line[7:]
    return 7 + (len(body) - len(body.lstrip(' ')))


def is_comment(line):
    return len(line) > 6 and line[6] == '*'


def is_break(line):
    body = line[7:].strip()
    return body == '' or set(body) <= set('=-')


def reflow(lines):
    out, i = [], 0
    while i < len(lines):
        ln = lines[i]
        if not is_comment(ln) or is_break(ln):
            out.append(ln)
            i += 1
            continue
        start_col = text_col(ln)
        cont_col = start_col
        j = i + 1
        while j < len(lines) and is_comment(lines[j]) \
                and not is_break(lines[j]) \
                and not LABEL.match(lines[j]) \
                and text_col(lines[j]) == cont_col:
            j += 1
        para = lines[i:j]
        if all(len(p.rstrip()) <= 72 for p in para):
            out.extend(para)
            i = j
            continue
        words = ' '.join(p[start_col:] for p in para).split()
        prefix = ln[:start_col]
        cont = '      *' + ' ' * (cont_col - 7)
        head, cur = prefix, []
        for w in words:
            if cur and len(head + ' '.join(cur + [w])) > 72:
                out.append(head + ' '.join(cur))
                head, cur = cont, [w]
            else:
                cur.append(w)
        out.append(head + ' '.join(cur))
        i = j
    return out


def main():
    bad = 0
    for path in sys.argv[1:]:
        raw = open(path, 'rb').read().decode('latin-1')
        crlf = '\r\n' in raw
        lines = raw.replace('\r', '').split('\n')
        new = reflow(lines)
        for n, l in enumerate(new, 1):
            if len(l) > 72:
                print(f'{path}:{n}: still {len(l)} columns: {l.strip()[:50]}')
                bad = 1
        text = ('\r\n' if crlf else '\n').join(new)
        if text != raw:
            open(path, 'wb').write(text.encode('latin-1'))
    sys.exit(bad)


if __name__ == '__main__':
    main()

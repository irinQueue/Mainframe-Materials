import re, sys

WORD_COMP3 = re.compile(r'\bCOMP-3\b|\bPACKED-DECIMAL\b')
WORD_BIN = re.compile(r'\b(COMP|COMP-4|COMP-5|BINARY)\b')


def size(pic, usage):
    p = pic.upper().rstrip('.')
    n = 0
    for m in re.finditer(r'([X9AV])(\((\d+)\))?', p.replace('S', '')):
        if m.group(1) == 'V':
            continue
        n += int(m.group(3) or 1)
    u = usage.upper().split(' PIC ', 1)[-1]
    if WORD_COMP3.search(u):
        return n // 2 + 1
    if WORD_BIN.search(u):
        return 2 if n <= 4 else 4 if n <= 9 else 8
    return n


def parse(path):
    txt = [l[6:72] for l in open(path, encoding='latin-1').read().splitlines()
           if len(l) > 6 and l[6] != '*']
    items = []
    for s in ' '.join(txt).split('.'):
        t = s.split()
        if not t or not t[0].isdigit() or t[0] == '88':
            continue
        pic = re.search(r'\bPIC\s+(\S+)', s)
        occ = re.search(r'\bOCCURS\s+(\d+)', s)
        red = re.search(r'\bREDEFINES\s+(\S+)', s)
        items.append(dict(l=int(t[0]), n=t[1] if len(t) > 1 else 'FILLER',
                          pic=pic.group(1) if pic else None, u=' ' + s,
                          occ=int(occ.group(1)) if occ else 1,
                          red=red.group(1) if red else None))

    def build(i):
        it = items[i]; j = i + 1; kids = []
        while j < len(items) and items[j]['l'] > it['l']:
            kids.append(j); j = build(j)
        it['kids'] = kids
        return j

    def sz(it):
        if it['pic']:
            s = size(it['pic'], it['u'])
        else:
            parts = [(sz(items[k]), items[k]['red']) for k in it['kids']]
            s = sum(a for a, r in parts if not r)
        it['sz'] = s
        return s * it['occ']

    def place(it, off):
        it['off'] = off; o = off
        for k in it['kids']:
            c = items[k]
            if c['red']:
                base = [items[x] for x in it['kids'] if items[x]['n'] == c['red']][0]
                place(c, base['off'])
            else:
                place(c, o); o += c['sz'] * c['occ']

    i = 0
    while i < len(items):
        i = build(i)
    for it in items:
        if it['l'] == 1:
            sz(it); place(it, 0)
    return items


if __name__ == '__main__':
    for it in parse(sys.argv[1]):
        print('%5d %5d %s%s' % (it['off'] + 1, it['sz'], it['n'],
                                ' OCCURS %d' % it['occ'] if it['occ'] > 1 else ''))

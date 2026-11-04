#!/usr/bin/env python3
"""Classify a COBOL program's output file, decode it, and mask sensitive data.

Usage:
  decode_output.py <file> [--layout COPYBOOK_OR_PROGRAM] [--record 01-NAME]
                   [--lrecl N] [--out DECODED.txt] [--preview N]

Classification (printed first, always):
  PLAIN TEXT   - ASCII/UTF-8 characters, usually CR/LF or LF terminated lines.
  EBCDIC TEXT  - mainframe character set (code page 037), no binary fields;
                 needs code-page conversion before it is readable.
  BINARY       - contains packed-decimal (COMP-3) / binary (COMP) bytes or
                 other non-printable data; the character fields inside it
                 are reported as EBCDIC or ASCII.

Decoding:
  * With --layout (a copybook, or a program source plus --record naming the
    01-level record / FD record), every record is split on the layout's own
    field offsets: PIC X / display numeric as text, COMP-3 unpacked with its
    sign, COMP/BINARY as big-endian integers. Output is one pipe-delimited
    row per record with a header row. FILLER fields are left out.
  * Without a layout, text files are copied line by line and binary files
    are shown as a character view (non-printables as '.'). Field-level
    decoding of a binary file needs --layout.

Masking (always on, cannot be turned off):
  * By field name - any field whose name looks like SSN/TIN/tax id, date of
    birth/death, person name, home address, phone/fax, e-mail, driver
    licence, bank/account number is replaced with '*' of the same width.
  * By value - in every remaining text field (and in all no-layout output),
    SSN-shaped values (###-##-####), standalone 9-digit numbers and e-mail
    addresses are masked too, as a safety net for fields with uninformative
    names.
The unmasked decode is never written or printed.
"""
import argparse, os, re, sys

# ----------------------------------------------------------------- masking
SENSITIVE_NAME = re.compile(
    r"SSN|SOC-?SEC|SOCIAL|(^|-)TIN($|-)|TAX-?ID|TAX-OR-PERS|PERS(ONAL)?-ID|"
    r"DOB|BIRTH|DEATH|FIRST-?NAME|LAST-?NAME|MIDDLE-?NAME|MID-?NAME|MID(DLE)?-?INIT|PERSON-?NAME|"
    r"PROD(UCER)?-?NAME|HOME-?ADD|RES(IDENCE)?-?ADD|HOME-?(CITY|ZIP|ST)|"
    r"PHONE|PH-?NUM|FAX|E-?MAIL|DRIVER|LICEN[SC]E|ACCOUNT-?N|ACCT-?N|BANK|"
    r"ROUTING|PASSPORT|GENDER|SEX-?CD|MARITAL", re.I)
VALUE_PATTERNS = [
    re.compile(r"(?<!\d)\d{3}-\d{2}-\d{4}(?!\d)"),          # SSN formatted
    re.compile(r"(?<![0-9A-Za-z])\d{9}(?![0-9A-Za-z])"),    # bare 9-digit SSN/TIN
    re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"),  # e-mail
]

def mask_value_patterns(text):
    for p in VALUE_PATTERNS:
        text = p.sub(lambda m: "*" * len(m.group(0)), text)
    return text

def mask_whole(text):
    return text if not text.strip(" \x00") else "*" * len(text)

# ---------------------------------------------------------- classification
EBCDIC_PRINTABLE = set([0x40]) | set(range(0x4A, 0x51)) | set(range(0x5A, 0x62)) | \
    set(range(0x6A, 0x70)) | set(range(0x79, 0x80)) | set(range(0x81, 0x8A)) | \
    set(range(0x91, 0x9A)) | set(range(0xA1, 0xAA)) | set(range(0xC0, 0xCA)) | \
    set(range(0xD0, 0xDA)) | set([0xE0]) | set(range(0xE2, 0xEA)) | set(range(0xF0, 0xFA))
ASCII_PRINTABLE = set(range(0x20, 0x7F))
TEXT_CONTROLS = {0x0A, 0x0D, 0x09, 0x0C}

def score(data):
    n = len(data) or 1
    a = sum(b in ASCII_PRINTABLE or b in TEXT_CONTROLS for b in data) / n
    e = sum(b in EBCDIC_PRINTABLE for b in data) / n
    return a, e

def classify(data, char_bytes=None):
    """Return (kind, charset, evidence). char_bytes = bytes of the text fields
    only (when a layout is known), so packed fields don't skew the charset."""
    if not data:
        return "EMPTY", None, "0 bytes"
    a, e = score(data)
    ca, ce = score(char_bytes) if char_bytes else (a, e)
    charset = "EBCDIC (cp037)" if ce > ca else "ASCII"
    has_lines = data.count(b"\n") > 0 and ca >= ce
    if a >= 0.995:
        return "PLAIN TEXT", "ASCII", f"{a:.1%} printable ASCII, {'line-terminated' if has_lines else 'no line terminators'}"
    if e >= 0.995 and e > a:
        return "EBCDIC TEXT", "EBCDIC (cp037)", f"{e:.1%} printable EBCDIC, no binary bytes"
    nonprint = 1 - max(a, e)
    return "BINARY", charset, (f"{nonprint:.1%} bytes non-printable in both ASCII and EBCDIC "
                               f"(packed/binary fields or low-values); text fields look {charset}")

# ------------------------------------------------------------ layout parse
def code_area(line):
    line = line.rstrip("\r\n")
    if len(line) >= 7 and line[6] in "*/":     # comment indicator column 7
        return ""
    return line[7:72] if len(line) > 7 else ""

def statements(text):
    """Split COBOL source (code area only) into period-terminated statements."""
    buf, out, q = [], [], None
    src = " ".join(code_area(l) for l in text.splitlines())
    for i, ch in enumerate(src):
        if q:
            if ch == q: q = None
        elif ch in "'\"":
            q = ch
        elif ch == "." and (i + 1 == len(src) or src[i + 1] == " "):
            out.append("".join(buf).strip()); buf = []; continue
        buf.append(ch)
    if "".join(buf).strip():
        out.append("".join(buf).strip())
    return out

PIC_RE = re.compile(r"\bPIC(?:TURE)?\s+(?:IS\s+)?(\S+)", re.I)

def field_size(pic, usage):
    p = re.sub(r"(.)\((\d+)\)", lambda m: m.group(1) * int(m.group(2)), pic.upper())
    digits = p.count("9")
    scale = len(p.split("V", 1)[1].replace("P", "")) if "V" in p else 0
    if usage == "COMP-3":
        return digits // 2 + 1, digits, scale
    if usage == "COMP":
        return (2 if digits <= 4 else 4 if digits <= 9 else 8), digits, scale
    return len(p.replace("S", "").replace("V", "").replace("P", "")), digits, scale

def parse_layout(path, record=None):
    text = open(path, encoding="latin-1").read()
    stmts = statements(text)
    items, started, base_level = [], record is None, None
    for s in stmts:
        m = re.match(r"^(\d{1,2})\s+([A-Z0-9][A-Z0-9-]*)?\s*(.*)$", s, re.I)
        if not m:
            if started and re.match(r"^(FD|SD|WORKING-STORAGE|LINKAGE|PROCEDURE)\b", s, re.I) and items:
                break
            continue
        lvl, name, rest = int(m.group(1)), (m.group(2) or "FILLER").upper(), m.group(3)
        if not started:
            if lvl == 1 and name == record.upper():
                started, base_level = True, 1
                items.append((lvl, name, rest))
            continue
        if lvl in (66, 77, 88):
            continue
        if lvl == 1 and items:
            if record is not None:
                break
        items.append((lvl, name, rest))
    if not items:
        sys.exit(f"ERROR: no record layout found in {path}" + (f" for 01 {record}" if record else ""))
    # Build flat field list with offsets; skip REDEFINES subtrees; expand OCCURS.
    skip_below, flat = None, []
    for lvl, name, rest in items:
        if skip_below is not None:
            if lvl > skip_below: continue
            skip_below = None
        if re.search(r"\bREDEFINES\b", rest, re.I):
            skip_below = lvl; continue
        occ = re.search(r"\bOCCURS\s+(\d+)", rest, re.I)
        pic = PIC_RE.search(rest)
        u = rest.upper()
        usage = "COMP-3" if ("COMP-3" in u or "PACKED-DECIMAL" in u) else \
                "COMP" if re.search(r"\b(COMP|COMP-4|COMP-5|BINARY)\b", u) else "DISPLAY"
        flat.append(dict(level=lvl, name=name, pic=pic.group(1).rstrip(".") if pic else None,
                         usage=usage, occurs=int(occ.group(1)) if occ else 1))
    # Recursive layout with OCCURS on groups and elementary items.
    def build(i, parent_level):
        out = []
        while i < len(flat) and flat[i]["level"] > parent_level:
            f = flat[i]
            if f["pic"]:
                size, digits, scale = field_size(f["pic"], f["usage"])
                el = dict(f, size=size, digits=digits, scale=scale)
                out.extend([dict(el, name=f"{f['name']}({k+1})" if f["occurs"] > 1 else f["name"])
                            for k in range(f["occurs"])])
                i += 1
            else:
                children, i = build(i + 1, f["level"])
                for k in range(f["occurs"]):
                    for c in children:
                        out.append(dict(c, name=c["name"] + (f"({k+1})" if f["occurs"] > 1 else ""),
                                        group=f["name"]))
        return out, i
    top = flat[0]
    elems, _ = build(1, top["level"]) if not top["pic"] else build(0, 0)
    off = 0
    for e in elems:
        e["offset"] = off; off += e["size"]
    return top["name"], elems, off

# ----------------------------------------------------------------- decode
def unpack(b, scale):
    h = b.hex()
    digits, sign = h[:-1], h[-1]
    if not digits.isdigit():
        return f"x'{h}'(invalid packed)"
    v = int(digits)
    s = "-" if sign in "bBdD" else ""
    txt = str(v) if scale == 0 else f"{v / 10**scale:.{scale}f}"
    return s + txt

def decode_record(rec, elems, codec):
    row = []
    for e in elems:
        raw = rec[e["offset"]: e["offset"] + e["size"]]
        if e["name"] == "FILLER":
            continue
        if e["usage"] == "COMP-3":
            val = unpack(raw, e["scale"]) if len(raw) == e["size"] else ""
        elif e["usage"] == "COMP":
            val = str(int.from_bytes(raw, "big", signed=e["pic"].upper().startswith("S"))) if raw else ""
        else:
            val = raw.decode(codec, errors="replace").replace("\x00", ".")
        sensitive = bool(SENSITIVE_NAME.search(e["name"]))
        val = mask_whole(val) if sensitive else mask_value_patterns(val)
        row.append(val.rstrip())
    return row

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("file"); ap.add_argument("--layout"); ap.add_argument("--record")
    ap.add_argument("--lrecl", type=int); ap.add_argument("--out")
    ap.add_argument("--preview", type=int, default=5)
    a = ap.parse_args()
    data = open(a.file, "rb").read()

    elems, lrecl, recname = None, a.lrecl, None
    if a.layout:
        recname, elems, size = parse_layout(a.layout, a.record)
        lrecl = lrecl or size
    char_bytes = None
    if elems and lrecl and len(data) >= lrecl:
        char_bytes = b"".join(data[i + e["offset"]: i + e["offset"] + e["size"]]
                              for i in range(0, min(len(data), lrecl * 200), lrecl)
                              for e in elems if e["usage"] == "DISPLAY" and e["name"] != "FILLER")
    kind, charset, evidence = classify(data, char_bytes)
    print(f"FILE     : {a.file}  ({len(data)} bytes)")
    print(f"TYPE     : {kind}" + (f"  - characters are {charset}" if charset else ""))
    print(f"EVIDENCE : {evidence}")
    if kind == "EMPTY":
        print("SCENARIO : A - actual run produced a BLANK file (0 records). Blank on both sides of a")
        print("           comparison proves nothing about layout or content - also compare a")
        print("           scenario B sample WITH data (see SKILL.md 'Blank output files').")
        if elems:
            out = a.out or (a.file + ".SYNTHETIC-layout-sample-masked.txt")
            row = []
            for e in elems:
                if e["name"] == "FILLER": continue
                if SENSITIVE_NAME.search(e["name"]): v = "*" * e["size"]
                elif e["usage"] != "DISPLAY" or (e["pic"] and set(e["pic"].upper()) <= set("S9V()0123456789")):
                    v = "1"
                else: v = "SAMPLE"[: e["size"]]
                row.append(v)
            with open(out, "w", encoding="utf-8") as f:
                f.write("# SYNTHETIC placeholder record built from the layout only - NOT program output.\n")
                f.write("# Use it to check field order/widths; trace real values through the program for scenario B.\n")
                f.write("|".join(e["name"] for e in elems if e["name"] != "FILLER") + "\n" + "|".join(row) + "\n")
            print(f"WRITTEN  : {out}  (SYNTHETIC layout placeholder, labelled as such)")
        return
    codec = "cp037" if charset and charset.startswith("EBCDIC") else "latin-1"

    # Split into records
    if kind == "PLAIN TEXT" and b"\n" in data:
        recs = [l.rstrip(b"\r") for l in data.split(b"\n")]
        if recs and recs[-1] == b"": recs.pop()
        how = "line-terminated"
    elif lrecl:
        if len(data) % lrecl:
            print(f"WARNING  : {len(data)} bytes is not a multiple of LRECL {lrecl} - layout may not match this file")
        recs = [data[i:i + lrecl] for i in range(0, len(data), lrecl)]
        how = f"fixed-length LRECL {lrecl}"
    elif kind == "EBCDIC TEXT" and (b"\x25" in data or b"\x15" in data):
        recs = re.split(b"\x15|\x25", data); how = "EBCDIC NL/LF-terminated"
    else:
        recs = [data[i:i + 100] for i in range(0, len(data), 100)]
        how = "no LRECL known - shown in 100-byte slices; pass --layout or --lrecl"
    lens = sorted({len(r) for r in recs})
    print(f"RECORDS  : {len(recs)} ({how}; record lengths {lens[:5]}{'...' if len(lens) > 5 else ''})")

    lines = []
    if elems:
        print(f"LAYOUT   : {recname} from {a.layout} - {len(elems)} fields, {sum(e['size'] for e in elems)} bytes")
        if lrecl and sum(e["size"] for e in elems) != lrecl:
            print(f"WARNING  : layout length {sum(e['size'] for e in elems)} != LRECL {lrecl}")
        masked = [e["name"] for e in elems if e["name"] != "FILLER" and SENSITIVE_NAME.search(e["name"])]
        print(f"MASKED   : by field name -> {', '.join(masked) or 'none'}; value patterns (SSN/9-digit/e-mail) in all other text fields")
        packed = [e["name"] for e in elems if e["usage"] != "DISPLAY"]
        if packed: print(f"NUMERIC  : binary/packed fields decoded -> {', '.join(packed)}")
        lines.append("|".join(e["name"] for e in elems if e["name"] != "FILLER"))
        for r in recs:
            lines.append("|".join(decode_record(r.ljust(lrecl or len(r), b" " if codec != "cp037" else b"\x40"), elems, codec)))
    else:
        print("MASKED   : value patterns (SSN/9-digit/e-mail) - no layout given, so name-based masking was not possible")
        for r in recs:
            t = r.decode(codec, errors="replace")
            t = "".join(ch if ch.isprintable() else "." for ch in t)
            lines.append(mask_value_patterns(t))
        if kind == "BINARY":
            print("NOTE     : binary file without --layout - packed/binary fields show as '.'; pass the FD copybook to decode them")

    out = a.out or (a.file + ".decoded-masked.txt")
    with open(out, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print(f"WRITTEN  : {out}")
    print("PREVIEW  :")
    for l in lines[: a.preview + (1 if elems else 0)]:
        print("  " + l[:200])

if __name__ == "__main__":
    main()

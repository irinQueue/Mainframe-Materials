"""Independent oracle for Firm-Producer Sync.

Written only from REQUIREMENTS-BRIEF.md (not from the COBOL reference solution).
It builds the scenario inputs and the expected outputs under ../starter/verify/.
Run:  python -I oracle.py
"""
import os, shutil

HERE = os.path.dirname(os.path.abspath(__file__))
START = os.path.normpath(os.path.join(HERE, "..", "starter"))
VERIFY = os.path.join(START, "verify")
SAMPLE = os.path.join(START, "data")


def rec(t, i="", parent="", name="", tin="", status=""):
    assert len(i) <= 8 and len(parent) <= 8 and len(name) <= 20 and len(tin) <= 9 and len(status) <= 1, (i, name, tin)
    return f"{t}{i:<8}{parent:<8}{name:<20}{tin:<9}{status}".ljust(60)


def parse(line):
    line = line.ljust(60)
    return dict(t=line[0], id=line[1:9], parent=line[9:17], name=line[17:37], tin=line[37:46], status=line[46])


def key(r):
    return r["t"] + r["id"]


# ---------------- INTAKE ----------------
def intake(lines):
    """returns (rc, valid_lines, reject_lines, report_lines)"""
    title = "INTAKE CONTROL REPORT"
    recs = [parse(l) for l in lines]

    def rejected(reason):
        return 8, [], [(" " * 60) + " " + reason.ljust(8)], [title, "", "FILE REJECTED".ljust(24) + reason]

    if not recs or recs[0]["t"] != "H":
        return rejected("NO-HDR")
    if recs[-1]["t"] != "T":
        return rejected("NO-TRL")
    details = [r for r in recs if r["t"] in "FP"]
    cnt = recs[-1]["id"]
    if not cnt.isdigit() or int(cnt) != len(details):
        return rejected("BAD-CNT")
    valid_firms = {r["id"] for r in details if r["t"] == "F" and r["id"].strip() != ""}
    valid, reject = [], []
    nf = npd = 0
    for r in details:
        raw = rec(r["t"], r["id"], r["parent"], r["name"], r["tin"], r["status"])
        reason = None
        if r["t"] == "F":
            if r["id"].strip() == "":
                reason = "BLANK-ID"
        else:
            tin = r["tin"]
            if not (len(tin) == 9 and all(c in "0123456789" for c in tin)):
                reason = "BAD-TIN"
            elif r["parent"].strip() == "" or r["parent"] not in valid_firms:
                reason = "NO-FIRM"
        if reason:
            reject.append(raw + " " + reason.ljust(8))
        else:
            valid.append(raw)
            if r["t"] == "F":
                nf += 1
            else:
                npd += 1
    c = lambda label, n: label.ljust(24) + f"{n:>4}"
    rpt = [title, "", "FILE DATE".ljust(24) + recs[0]["id"],
           c("RECORDS READ", len(details)), c("RECORDS VALID", len(valid)), c("RECORDS REJECTED", len(reject)),
           c("FIRMS VALID", nf), c("PRODUCERS VALID", npd)]
    return 0, valid, reject, rpt


# ---------------- UPDATE ----------------
def update(valid_lines, master_lines):
    new = {key(parse(l)): parse(l) for l in valid_lines}
    old = {key(parse(l)): parse(l) for l in master_lines}
    out, act = {}, []
    for k, r in old.items():
        out[k] = r
    for k, r in new.items():
        if k not in old:
            out[k] = r
            act.append((k, "A", r))
        else:
            o = old[k]
            changed = any(o[f] != r[f] for f in ("name", "parent", "tin", "status"))
            out[k] = r
            if changed:
                act.append((k, "C", r))
    fmt = lambda r: rec(r["t"], r["id"], r["parent"], r["name"], r["tin"], r["status"])
    newmaster = [fmt(out[k]) for k in sorted(out)]
    activity = [code + fmt(r) for k, code, r in sorted(act, key=lambda x: x[0])]
    return newmaster, activity


# ---------------- REPORTS ----------------
def reports(master_lines, newmaster_lines):
    old = {key(parse(l)): parse(l) for l in master_lines}
    new = [parse(l) for l in newmaster_lines]
    firms = sorted([r for r in new if r["t"] == "F"], key=lambda r: r["id"])
    prods = sorted([r for r in new if r["t"] == "P"], key=lambda r: r["id"])
    fp = ["FIRM AND PRODUCER REPORT", ""]
    for f in firms:
        fp.append(f"FIRM {f['id']} {f['name']} {f['status']}")
        for p in prods:
            if p["parent"] == f["id"]:
                fp.append(f"  PROD {p['id']} {p['name']} {p['tin']} {p['status']}")
    fp += ["", "TOTAL FIRMS".ljust(24) + f"{len(firms):>4}", "TOTAL PRODUCERS".ljust(24) + f"{len(prods):>4}"]
    tc = ["TIN CHANGE REPORT", ""]
    n = 0
    for p in prods:
        k = key(p)
        if k in old and old[k]["tin"] != p["tin"]:
            tc.append(f"PROD {p['id']} OLD {old[k]['tin']} NEW {p['tin']}")
            n += 1
    tc += ["", "TOTAL CHANGED".ljust(24) + f"{n:>4}"]
    return fp, tc


# ---------------- data ----------------
MASTER = [
    rec("F", "FIRM0001", "", "NORTHWIND FIRM 01", "", "A"),
    rec("F", "FIRM0002", "", "NORTHWIND FIRM 02", "", "A"),
    rec("F", "FIRM0003", "", "NORTHWIND FIRM 03", "", "A"),
    rec("F", "FIRM0004", "", "NORTHWIND FIRM 04", "", "A"),
    rec("P", "PROD0001", "FIRM0001", "PRODUCER ONE", "990000001", "A"),
    rec("P", "PROD0002", "FIRM0001", "PRODUCER TWO", "990000002", "A"),
    rec("P", "PROD0003", "FIRM0002", "PRODUCER THREE", "990000003", "A"),
    rec("P", "PROD0004", "FIRM0003", "PRODUCER FOUR", "990000004", "A"),
    rec("P", "PROD0005", "FIRM0004", "PRODUCER FIVE", "990000005", "A"),
]
DETAIL = [
    rec("F", "", "", "UNNAMED TEST FIRM", "", "A"),                       # R1 BLANK-ID
    rec("F", "FIRM0001", "", "NORTHWIND FIRM 01", "", "A"),                # unchanged
    rec("F", "FIRM0002", "", "NORTHWIND FIRM 02", "", "I"),                # status change
    rec("F", "FIRM0004", "", "NORTHWIND FIRM 4 NEW", "", "A"),           # name change
    rec("F", "FIRM0005", "", "NORTHWIND FIRM 05", "", "A"),                # new
    rec("P", "PROD0001", "FIRM0001", "PRODUCER ONE", "990000001", "A"),    # unchanged
    rec("P", "PROD0002", "FIRM0001", "PRODUCER TWO", "990000099", "A"),    # TIN change
    rec("P", "PROD0003", "FIRM0005", "PRODUCER THREE", "990000003", "A"),  # parent change
    rec("P", "PROD0006", "FIRM0005", "PRODUCER SIX", "990000006", "A"),    # new
    rec("P", "PROD0007", "FIRM0001", "PRODUCER SEVEN", "99000007X", "A"),  # BAD-TIN (letter)
    rec("P", "PROD0008", "FIRM0002", "PRODUCER EIGHT", "99000008", "A"),   # BAD-TIN (8 digits)
    rec("P", "PROD0009", "FIRM0003", "PRODUCER NINE", "990000009", "A"),   # NO-FIRM (firm only on master)
    rec("P", "PROD0010", "", "PRODUCER TEN", "990000010", "A"),            # NO-FIRM (blank parent)
    rec("P", "PROD0011", "FIRM0009", "PRODUCER ELEVEN", "99000ABCD", "A"), # BAD-TIN and NO-FIRM: BAD-TIN wins
]


def lna(detail, header=True, trailer=True, count=None):
    out = []
    if header:
        out.append(rec("H", "20261103"))
    out += detail
    if trailer:
        n = len(detail) if count is None else count
        out.append(rec("T", f"{n:08d}" if isinstance(n, int) else n))
    return out


SCENARIOS = {
    "s1-normal": (lna(DETAIL), MASTER),
    "s2-bad-count": (lna(DETAIL, count=13), MASTER),
    "s3-no-header": (lna(DETAIL, header=False), MASTER),
    "s4-no-trailer": (lna(DETAIL, trailer=False), MASTER),
    "s5-empty-day": (lna([]), MASTER),
    "s6-empty-file": ([], MASTER),
    "s7-count-not-numeric": (lna(DETAIL, count="ABCDEFGH"), MASTER),
    "s8-no-header-no-trailer": (lna(DETAIL, header=False, trailer=False), MASTER),
}


def write(path, lines):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="\n") as f:
        for l in lines:
            f.write(l.rstrip() + "\n")


def write_input(path, lines):  # inputs keep the full 60 characters
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="\n") as f:
        for l in lines:
            f.write(l + "\n")


def main():
    # clear only what this script generates; verify/check.sh must survive
    for sub in ("scenarios", "expected"):
        d = os.path.join(VERIFY, sub)
        if os.path.isdir(d):
            shutil.rmtree(d)
    summary = []
    for name, (lna_lines, master) in SCENARIOS.items():
        sd = os.path.join(VERIFY, "scenarios", name)
        ed = os.path.join(VERIFY, "expected", name)
        write_input(os.path.join(sd, "LNA.DAT"), lna_lines)
        write_input(os.path.join(sd, "MASTER.DAT"), master)
        rc, valid, reject, rpt = intake(lna_lines)
        write(os.path.join(ed, "intake_rc.txt"), [str(rc)])
        write(os.path.join(ed, "VALID.DAT"), valid)
        write(os.path.join(ed, "REJECT.DAT"), reject)
        write(os.path.join(ed, "INTAKE.RPT"), rpt)
        line = f"{name}: INTAKE rc={rc} valid={len(valid)} reject={len(reject)}"
        if rc == 0:
            newmaster, activity = update(valid, master)
            fp, tc = reports(master, newmaster)
            write(os.path.join(ed, "NEWMASTER.DAT"), newmaster)
            write(os.path.join(ed, "ACTIVITY.DAT"), activity)
            write(os.path.join(ed, "FIRMPROD.RPT"), fp)
            write(os.path.join(ed, "TINCHG.RPT"), tc)
            line += f" newmaster={len(newmaster)} activity={len(activity)}"
        summary.append(line)
    # the sample day trainees see in data/ is scenario 1
    s1 = os.path.join(VERIFY, "scenarios", "s1-normal")
    os.makedirs(SAMPLE, exist_ok=True)
    for f in ("LNA.DAT", "MASTER.DAT"):
        shutil.copy(os.path.join(s1, f), os.path.join(SAMPLE, f))
    print("\n".join(summary))


if __name__ == "__main__":
    main()

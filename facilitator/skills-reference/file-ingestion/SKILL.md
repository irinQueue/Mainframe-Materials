---
name: file-ingestion
description: "Extract and consolidate content from one or more files (PDF, DOCX, plain text, or markdown) into a single readable context block. Called by other skills that require file content as input, triggered explicitly by the user, or used when the user asks to extract or read the contents of a file. Supports multiple files in a single call, merging all extracted content with clear source labels. Trigger when the user says 'extract this file', 'read this document', 'ingest this file', 'load this spec', or any variation."
---

# File Ingestion Skill

## Purpose

Extract readable content from one or more files and make it available as a consolidated context block for the calling skill or the current session. Supports PDF, DOCX, plain text, and markdown. Handles all extraction tool detection and fallback logic internally — the caller receives clean, labeled content ready for use.

---

## Workflow

### Step 1: Receive File Paths

If called by a skill, accept the file path(s) passed by the calling skill and proceed to Step 2.

If triggered directly by the user and no file paths were provided, ask:

```
✦ File Ingestion
──────────────────────────────────────────────
Enter the path(s) of the file(s) to extract.
For multiple files, separate paths with a comma.

File path(s):
```

Wait for input before proceeding.

---

### Step 2: Detect File Type Per File

For each file path received, detect the file type:

- Extension is `.txt` or `.md` → plain text — read directly
- Extension is `.pdf` → PDF extraction required
- Extension is `.docx` or `.doc` → DOCX extraction required
- Extension is anything else → flag as unsupported, inform the user, and skip that file

```
✦ Detected file types:
  - [filename] → [type]
  - [filename] → [type]
```

---

### Step 3: Extract Content Per File

Process each supported file using the following fallback chain:

#### Plain Text / Markdown
Read the file content directly. No conversion needed.

#### PDF — Fallback Chain
1. Check if `pdftotext` is available:
```
pdftotext --version
```
If available → extract:
```
pdftotext [filepath] -
```

2. If `pdftotext` is not available, check if `pdfplumber` is installed:
```
python -c "import pdfplumber"
```
If available → extract using pdfplumber via Python one-liner.

3. If neither is available → go to Step 4.

#### DOCX — Fallback Chain
1. Check if `pandoc` is available:
```
pandoc --version
```
If available → extract:
```
pandoc [filepath] -t plain
```

2. If `pandoc` is not available, check if `python-docx` is installed:
```
python -c "import docx"
```
If available → extract using python-docx via Python one-liner.

3. If neither is available → go to Step 4.

---

### Step 4: Handle Missing Tools

If a required extraction tool is not available for any file, inform the user:

```
✦ Missing extraction tools for: [filename]
──────────────────────────────────────────────
  Required tool not found. Options to resolve:

  For PDF:
  - Install pdftotext: sudo apt install poppler-utils
                       brew install poppler
  - Install pdfplumber: pip install pdfplumber

  For DOCX:
  - Install pandoc: sudo apt install pandoc
                    brew install pandoc
  - Install python-docx: pip install python-docx

  Would you like me to attempt installation? (yes / no)
──────────────────────────────────────────────
```

If the user says yes → attempt installation, then re-run extraction for that file.
If the user says no → skip that file and proceed with remaining files.
If all files are skipped → inform the user and stop.

---

### Step 5: Label and Consolidate Content

Once all supported files are extracted, label each file's content clearly and merge into a single consolidated context block:

```
✦ Extraction complete. Content now available in context:

══════════════════════════════════════════════
SOURCE: [filename-1]
──────────────────────────────────────────────
[extracted content of file 1]

══════════════════════════════════════════════
SOURCE: [filename-2]
──────────────────────────────────────────────
[extracted content of file 2]

══════════════════════════════════════════════
```

Each file's content must be clearly separated and labeled with its source filename so any calling skill or the user can distinguish which content came from which file.

---

### Step 6: Confirm Availability

Confirm to the user or calling skill that extraction is complete and content is available:

```
──────────────────────────────────────────────
✦ File ingestion complete.
  Files extracted: [n]
  Files skipped:   [n] (if any)
  Content is available in the current session context.
──────────────────────────────────────────────
```

If called by a skill, hand control back to the calling skill automatically after this confirmation.

---

## Rules

1. Never proceed without at least one successfully extracted file — if all files fail, stop and inform the user clearly.
2. Never silently skip a file — always inform the user when a file is skipped and why.
3. Always label extracted content with its source filename — never merge content without clear separation.
4. Never modify, summarize, or interpret extracted content — pass it through exactly as extracted.
5. Always attempt the full fallback chain before declaring a tool missing.
6. Always offer installation assistance when a required tool is missing.
7. When called by another skill, return control to the calling skill immediately after Step 6.
8. Content is available for the current session only — it does not persist across sessions.

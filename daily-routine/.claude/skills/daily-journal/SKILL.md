---
name: daily-journal
description: Writes a formatted daily journal entry at the end of the day, around 10 PM. Use this whenever the user says "journal", "daily journal", "log my day", "end of day", "10pm check-in", or "how was my day", or shares a recap of their day, even if they don't say "journal".
---

# Daily Journal

Turn the user's day into a short, consistent entry. The same structure every day makes entries easy to look back on.

## Steps
1. Use whatever the user shared about the day. If they only said "journal", ask for the missing parts in one short message: morning movement, work wins, family time, mood (1-5).
2. Fill the template using only what they told you. Write "Not logged" for anything missing, since an invented detail makes the journal untrustworthy.
3. End with tomorrow's plan, defaulting to the routine: 6 AM movement, 9-5 work, evening family time.

## Output format
ALWAYS use this template:

# Daily Journal - [Weekday, Date]

## Morning Movement (6:00 AM)
- Activity / details: ...

## Work (9:00 AM - 5:00 PM)
- Main tasks: ...
- Wins: ...
- Carried over: ...

## Family Time (Evening)
- What we did: ...
- Highlight: ...

## 10 PM Reflection
- Mood / energy (1-5): ...
- Grateful for: ...
- Do differently: ...

## Tomorrow
- 6:00 AM: [movement plan]
- Top 3 priorities: 1. ... 2. ... 3. ...

## Guidelines
- Keep it under one page so writing it stays a two-minute habit.
- Use a warm, plain tone. This is a personal record, not a report.
- Don't include customer names or personal details in work notes. Describe tasks generically.
- A skill can't fire by itself at 10 PM. The user triggers it by saying "journal", or sets up a scheduled reminder separately.

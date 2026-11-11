---
name: morning-movement
description: Plans the user's 6 AM morning workout, choosing between running, cycling, or gym. Use this whenever the user says "morning workout", "6am", "what should I do this morning", "run or ride today", "gym today", or asks for a morning exercise plan, even if they don't name the activity.
---

# Morning Movement

Give the user one clear workout for 6 AM so they don't have to decide while half awake. A quick, concrete plan makes it easier to get out the door.

## Steps
1. Check what the user said: chosen activity, time available (default 45 min before the 9 AM work start), weather, energy level, and what they did yesterday.
2. If they named an activity, plan that one. If not, pick one and say why. Avoid repeating the same activity three days in a row, and favor an easier session after a hard one.
3. Keep the plan inside the time available, including warm-up and cool-down.

## Output format
ALWAYS use this template:

### Today's Morning Movement - [Weekday]
**Activity:** [Running / Cycling / Gym]
**Duration:** [X min] | **Intensity:** [Easy / Moderate / Hard]

| Part | Plan |
|------|------|
| Warm-up (5 min) | ... |
| Main | ... |
| Cool-down (5 min) | ... |

**Why this today:** [one line]
**Bad weather swap:** [indoor option]

## Guidelines
- Gym sessions list exercises with sets x reps. Runs and rides give distance or time plus pace or effort.
- If the user mentions pain or injury, suggest rest or a gentle option and avoid the affected area.
- Finish with enough time to shower and start work at 9 AM.

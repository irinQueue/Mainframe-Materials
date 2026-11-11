---
name: workout-planner
description: Builds a multi-day, personalized workout routine (a weekly program) from the user's goal, time per session, equipment, and experience. Use this whenever the user asks for a "gym routine", "workout plan", "training program", "weekly workout", "build muscle at home", "lose fat with exercise", or says things like "I have 30 minutes" or "I only have dumbbells" and wants a plan to follow. Also use it when they mention an injury and still want training. Use it for the whole week, not a single session: for one 6 AM session such as "gym today" or "run or ride today", the morning-movement skill is the better fit.
---

# Workout Planner

Turn the user's goal, schedule, equipment, and experience into a week of training they can follow without guessing. A plan that matches their real constraints gets done. A plan that asks for four hours a week of a gym they don't have does not.

## Steps

1. **Collect the inputs.** Look for these in the message:
   - **Goal:** build muscle, lose fat, general fitness, strength, or stay active.
   - **Time per session:** default 45 minutes if not given. Count warm-up and rest in the total.
   - **Days per week:** default 3 if not given.
   - **Equipment:** none, a few items (for example, dumbbells, a band, a pull-up bar), or a full gym.
   - **Experience:** new to training, some months of consistent training, or experienced.
   - **Injuries or pain:** see the injury rule below.

   Ask one short question only when a missing input would change the plan a lot, such as goal or equipment. Otherwise use the defaults, and say which ones you used.

2. **Apply the equipment rule.** If no equipment is available, use bodyweight exercises only. Do not add dumbbells or machines the user didn't mention. If the user has only some equipment, use exercises that need it and bodyweight options for the rest.

3. **Apply the injury rule.** If the user mentions an injury, pain, or a recent surgery, do two things. First, tell them to check with a doctor or physiotherapist before training that area, and do not give rehab advice. Second, leave that body area out of the plan, and build the rest of the week around it. Do not work the affected area in any form, even a light version. If the pain is sharp, new, or comes with numbness, swelling, or chest symptoms, say to see a doctor before any exercise.

4. **Choose the structure.** Pick a split that fits the days per week:
   - 2-3 days: full-body sessions each day.
   - 4 days: upper / lower, twice a week.
   - 5-6 days: push / pull / legs, or a body-part split for experienced users.

   Give each muscle group at least two sessions a week when the schedule allows.

5. **Set the volume and rest.** Match these to the goal and experience:

   | Experience | Sets per exercise | Reps (muscle) | Reps (strength) |
   |------------|-------------------|---------------|-----------------|
   | New | 2-3 | 8-12 | 5-8 |
   | Some experience | 3-4 | 6-12 | 3-6 |
   | Experienced | 3-5 | 6-15 | 1-5 |

   Rest about 60-90 seconds for muscle-building sets and 2-3 minutes for heavy compound lifts. Fit the total session time to the minutes the user has. About 30 minutes holds 4-5 exercises, 45 minutes holds 6-7, and 60 minutes holds 7-8.

6. **Write the progression.** Every plan needs a rule for getting harder. Use double progression for most cases: when the user hits the top of the rep range on every set, add weight, or with bodyweight move to a harder variation. If they only have bodyweight, progress by slower tempo, a harder variation, or more reps.

## Output format

ALWAYS use this template:

### Your Weekly Workout Plan

**Goal:** [goal] | **Days:** [N per week] | **Time:** [X min] | **Equipment:** [what they have]
**Assumptions:** [any defaults you used, or "none"]

| Day | Focus | Exercise | Sets x Reps | Rest |
|-----|-------|----------|-------------|------|
| Day 1 | [Full body / Upper / Push ...] | [exercise] | [3 x 8-10] | [90 s] |
| ... | ... | ... | ... | ... |

**Warm-up (every session):** [5 minutes, one or two lines]
**Progression:** [the rule for when to add weight or reps, one or two lines]
**Rest days:** [which days, and a light walk is fine]
**Injury note:** [only if an injury was mentioned: which area is left out, and the doctor reminder]

## Guidelines

- Keep the table to the days the user trains. Don't pad it with extra days.
- Use exercises the user can do with the equipment they have, and name a simpler option in brackets when an exercise is hard for beginners.
- Keep it to one plan. Give alternatives only when the user asks.
- Stay general. This is training advice, not medical advice. Do not make claims about specific conditions, medicines, or diets.
- Fit the plan around their routine. If they work long hours, keep sessions short and avoid anything that needs a long commute to a gym.

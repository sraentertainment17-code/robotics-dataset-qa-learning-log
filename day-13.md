# Day 13: Script review and cleanup ✅ (Oct 9, 2026)

## Goal
Scattered checks are hard to reuse. One clean script is easier. Combine the 4 separate check scripts from Days 8–12 into **one file** with **one function per check** and a **one-page summary**: `audit_checks_v1.py`. This file is the product engine; everything after is packaging.

## Analogies
- **4 loose tools in a drawer → a Swiss army knife.** Same tools, but now they're in one thing you can pick up and use anywhere.
- **A function = a recipe card.** You write the recipe once, give it a name (like `check_timing`), and after that you just "call" it by name instead of rewriting every step.

## What's inside audit_checks_v1.py (251 lines)
| Part | What it does |
|---|---|
| Top comment | Explains what the script is, which 4 scripts it combines, and how to run it |
| **Thresholds block** | All the pass/fail rules in one place, so they're easy to change |
| `load(repo_id)` | Downloads info.json, the episodes list and all the frames |
| `joint_names(info)` | Reads the joint names from info.json |
| `check_episodes(eps)` | Checklist #1 and #2 (Day 8) |
| `check_timing(df, fps)` | Checklist #4 (Day 9) |
| `check_actions(df)` | Checklist #7, dead or clipped joints (Day 10) |
| `check_empty(df)` | Checklist #7, empty or junk tries (Day 12) |
| `main()` | Runs everything and prints the one-page summary |

### The thresholds block (the rules)
| Rule | Value | Meaning |
|---|---|---|
| `SKIP_FACTOR` | 2.0 | A time step over 2× the normal beat = a skipped frame |
| `LIMIT` | 99.9 | A joint at or past ±99.9 = at the limit |
| `CLIP_MAX_PCT` | 1.0 | More than 1% of frames at the limit = clipped joint |
| `DEAD_STD` | 0.5 | A joint whose spread in a try is under 0.5 = dead |
| `EMPTY_RATIO` | 0.25 | A try moving under 25% of the typical try = empty |

### The load step
- Reads **info.json** (the label on the box) for fps, try count, frame count, robot type and joint names.
- Reads **every** parquet file in `meta/episodes/` and `data/` and glues them together, so bigger datasets split across several files still load completely.
- Takes the dataset name from the command line: `python audit_checks_v1.py some-user/some-dataset`. With no name, it uses `lerobot/svla_so101_pickplace`.

### No hardcoding
Nothing about our dataset is typed in by hand: no "50 tries", no "30 fps", no joint names. Everything comes from the dataset's own info.json. That's why the same script can run on a different dataset tomorrow (Day 14).

### The 4 functions (recipe cards)
Each one takes data in and hands back **two things**: `passed` (True/False) and a short **message** explaining why.
1. **check_episodes:** are all tries there (0 to N−1, no gaps), none empty, and do the frames add up to what info.json says?
2. **check_timing:** is the step between frames steady at 1/fps, with no skipped frames?
3. **check_actions:** is any joint dead in any try, or clipped in more than 1% of frames?
4. **check_empty:** does any try move less than 25% of a typical try?

If one check crashes (for example, a dataset is missing a column), it's recorded as **FAIL with the error** and the others still run.

### Testing that it can actually catch problems
A check that always says PASS is useless. The coach broke copies of the data on purpose, in memory only (the real data wasn't touched), and each check caught its problem:

| Broken on purpose | What the check said |
|---|---|
| Removed try 3 | FAIL: missing tries [3]; frames add up to 11756, info.json says 11939 |
| Cut frames out of try 5 | FAIL: 1 skipped frames in tries [5] (biggest step 0.400 s) |
| Froze elbow_flex in try 7 | FAIL: elbow_flex dead in 1 tries [7] |
| Froze the whole arm in try 9 | FAIL: 1 empty tries [9] (under 25% of median 860) |

## Running it on my laptop
The coach copied the file to my laptop at `~/audit_checks_v1.py`.
1. `exit()` to leave Python (the `>>>` prompt) and get back to Terminal.
2. In the `lerobot` environment, from my home folder (`~`):
```bash
python audit_checks_v1.py
```
My output matched the coach's run exactly:
```
Loading lerobot/svla_so101_pickplace ...

========================================================================
ROBOT DATASET AUDIT: automated checks (audit_checks_v1)
========================================================================
Dataset:    lerobot/svla_so101_pickplace
Robot type: so100_follower
Episodes:   50   Frames: 11939   FPS: 30
Joints:     shoulder_pan, shoulder_lift, elbow_flex, wrist_flex, wrist_roll, gripper
------------------------------------------------------------------------
PASS  #1-2 Episodes     all 50 tries present (0-49), none empty, shortest 183 frames
PASS  #4   Timing       steady at 30 fps (avg step 0.03333 s, biggest 0.03333 s), 0 skipped frames
PASS  #7   Actions      no dead joints in any try; clipping under 1% (highest: elbow_flex 0.7%)
PASS  #7   Empty tries  0 empty tries; least-moving try 24 = 77% of typical (median 860)
------------------------------------------------------------------------
OVERALL: PASS (4/4 automated checks passed)
Not automated yet: #3 odd lengths, #5 video vs data, #6 action vs state,
#8 camera clear, #9 task finished, #10 label correct (manual review).
========================================================================
```

## How to read the report
1. **Header (top block):** which dataset, which robot, how many tries, frames and fps, and the joint names, all read from info.json. It's the "what we audited" line.
2. **One line per check:** `PASS` or `FAIL`, then the checklist number, then the check name, then the **evidence** (the numbers behind the verdict). For example, Timing: avg step 0.03333 s = exactly 1/30 s, 0 skipped frames.
3. **OVERALL:** PASS only if **every** automated check passed (here 4 of 4). One FAIL makes the overall FAIL.
4. **Not automated yet:** an honest list of what this script does **not** check. Those need the video work (Days 15–17) or a human eye (Day 11 style). This is the Day 6 rule: only claim what you actually checked.

## In my words (checked)
> "because it will not messy .if you do 4 separate scripts it will be overwarming"

Feedback: right ✅. Two more reasons: **one command gives one report** you can hand to a team, and it **runs on any dataset in seconds**.

## Key ideas
- Function = recipe card: write once, call by name, get back (passed, message).
- Keep the rules (thresholds) in one place at the top.
- Read everything from info.json; never hardcode, so it works on any dataset.
- Test your checks by breaking data on purpose; a check that can't fail can't be trusted.
- The report lists what it did **not** check, so it's honest.

## Checklist progress
- #1 Episode count, #2 Frame count: ✅ automated, now inside `audit_checks_v1.py`
- #4 Timing: ✅ automated, now inside `audit_checks_v1.py`
- #7 Robot moves (dead/clipped joints + empty tries): ✅ automated, now inside `audit_checks_v1.py`
- #3, #5, #6: not in the script yet (done by hand on Days 2–4)
- #8, #9, #10: manual review (Day 11)

Script: [audit_checks_v1.py](audit_checks_v1.py). Run it with `python audit_checks_v1.py [dataset_name]`.

## Next: Day 14
Week 2 review: run `audit_checks_v1.py` on a second public SO-101 dataset, fix anything that breaks (camera names, fps, columns), and note each fix.

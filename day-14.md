# Day 14: Week 2 review: run it on a second dataset ✅ (Oct 9, 2026)

## Goal
A script that works on one dataset is a demo. One that works on two is a **tool**. Run `audit_checks_v1.py` on a second public SO-101 dataset, fix anything that breaks, and note each fix. Team datasets all look slightly different, so this shows whether the tool is general enough.

## The second dataset
The coach searched the Hugging Face Hub for "so101", then checked each candidate's info.json (needs format v3.0, SO-100/SO-101 robot, small, 20+ tries).

| | First dataset | Second dataset |
|---|---|---|
| Name | lerobot/svla_so101_pickplace | **MaxT90/so101-pick-place** |
| Robot type (info.json) | so100_follower | so_follower |
| fps | 30 | 30 |
| Tries | 50 | 50 |
| Frames | 11,939 | 22,771 |
| Size | ≈ 86 MB downloaded | 288 MB total (the audit only downloads the small tables, not the videos) |

## Run 1: the old tool → FAIL
On my laptop:
```bash
python audit_checks_v1.py MaxT90/so101-pick-place
```
```
FAIL  #7   Actions      shoulder_lift clipped in 37.5% of frames; wrist_roll clipped in 1.8% of frames
OVERALL: FAIL (3/4 automated checks passed)
```
The other 3 checks passed.

## What was wrong: the tool, not the data
The old rule said: "a joint value at 99.9 or more (plus or minus) = stuck at the limit = clipped." That assumes every robot uses a **±100 scale**. But in this dataset some joints go **past** 100 (-104.3, 113.8). A joint that can reach 104 is **not stuck at 100**, so calling it "clipped" was wrong. **Tool bug, not bad data.**

## The fix (smallest change)
**Before:**
```python
LIMIT = 99.9          # joint value at or beyond +/-99.9 = "at the limit"
...
    clip_pct = (act.abs() >= LIMIT).sum() / len(act) * 100
...
    return True, f"no dead joints in any try; clipping under {CLIP_MAX_PCT:g}% (highest: {top} {clip_pct.max():.1f}%)"
```
**After:**
```python
SCALE_MAX = 100.0     # the +/-100 scale that LeRobot calibration usually uses
LIMIT_TOL = 0.1       # within 0.1 of +/-100 (99.9 to 100.1) = "at the limit"
...
    # Clipping: what % of frames sit right AT the +/-100 limit, per joint.
    # (Day 14 fix: some datasets go past 100, e.g. 104 or 123. A value that
    # can go past 100 is not stuck at 100, so only 99.9 to 100.1 counts.)
    clip_pct = ((act.abs() - SCALE_MAX).abs() <= LIMIT_TOL).sum() / len(act) * 100
    past_scale = [j for j in names if act[j].abs().max() > SCALE_MAX + LIMIT_TOL]
...
    note = f"; note: {', '.join(past_scale)} go past +/-100 (scale not capped at 100)" if past_scale else ""
    return True, f"no dead joints in any try; clipping under {CLIP_MAX_PCT:g}% (highest: {top} {clip_pct.max():.1f}%){note}"
```
In plain words:
1. Only values **right at** 100 (between 99.9 and 100.1) count as "at the limit". A value of 104 is no longer counted.
2. If a joint goes past 100, the report adds a **note** saying so, so nothing is hidden.

Checked that the fix didn't break anything:
- svla_so101_pickplace: exactly the same output as before, still PASS 4/4 (its biggest value is exactly 100.0).
- A fake test with elbow_flex pinned at 100 in about 5% of frames still gives FAIL ("elbow_flex clipped in 5.7% of frames"), so real clipping is still caught.

The script is now 256 lines.

## Run 2: the fixed tool → PASS
The coach copied the fixed file to my laptop, and I re-ran the same command:
```
Loading MaxT90/so101-pick-place ...

========================================================================
ROBOT DATASET AUDIT: automated checks (audit_checks_v1)
========================================================================
Dataset:    MaxT90/so101-pick-place
Robot type: so_follower
Episodes:   50   Frames: 22771   FPS: 30
Joints:     shoulder_pan, shoulder_lift, elbow_flex, wrist_flex, wrist_roll, gripper
------------------------------------------------------------------------
PASS  #1-2 Episodes     all 50 tries present (0-49), none empty, shortest 346 frames
PASS  #4   Timing       steady at 30 fps (avg step 0.03333 s, biggest 0.03333 s), 0 skipped frames
PASS  #7   Actions      no dead joints in any try; clipping under 1% (highest: wrist_flex 0.2%); note: shoulder_lift, wrist_flex, wrist_roll go past +/-100 (scale not capped at 100)
PASS  #7   Empty tries  0 empty tries; least-moving try 24 = 88% of typical (median 1084)
------------------------------------------------------------------------
OVERALL: PASS (4/4 automated checks passed)
Not automated yet: #3 odd lengths, #5 video vs data, #6 action vs state,
#8 camera clear, #9 task finished, #10 label correct (manual review).
========================================================================
```

## My questions and how they got answered
1. **"Explain like a baby."** A **height chart**. One school's chart goes up to 100 cm, another's goes to 120 cm. A kid who measures 104 on the 120 chart is perfectly normal. The old rule said "anything near the top of a 100 chart is stuck", so it flagged the 104 kid. **The rule was wrong, not the kid.**
2. **"How do you know the first data was bad?"** Neither dataset was bad. The **tool** was wrong. Lesson: **check the tool before blaming the data.**
3. **"How do you know their robot arm is longer?"** It isn't. It's the **same SO-101 arm**. What differs is the **calibration number scale**, like two volume knobs on the same speaker: one labelled 0–100, the other 0–120. Same sound, different numbers. We knew because the data's own max values showed it.
4. **"Show me, I didn't see 114/104."** I checked it myself:
```python
import pandas as pd
df = pd.read_parquet("hf://datasets/MaxT90/so101-pick-place/data/")
names = ["shoulder_pan","shoulder_lift","elbow_flex","wrist_flex","wrist_roll","gripper"]
act = pd.DataFrame(df["action"].tolist(), columns=names)
print(act.describe().round(1))
```
(Pointing at the `data/` folder reads every file inside it.)

| | shoulder_pan | shoulder_lift | elbow_flex | wrist_flex | wrist_roll | gripper |
|---|---|---|---|---|---|---|
| count | 22771 | 22771 | 22771 | 22771 | 22771 | 22771 |
| mean | 5.8 | -39.8 | 34.8 | 77.5 | 82.7 | 5.4 |
| std | 21.5 | 57.1 | 54.4 | 13.7 | 8.9 | 8.9 |
| min | -23.6 | **-104.3** | -64.1 | -9.2 | 50.0 | 0.0 |
| 25% | -9.9 | **-102.8** | -16.4 | 75.4 | 78.5 | 0.0 |
| 50% | -6.7 | -29.4 | 23.6 | 78.1 | 83.4 | 0.1 |
| 75% | 34.3 | 15.9 | 96.5 | 84.2 | 88.0 | 7.9 |
| max | 49.3 | 56.0 | 97.0 | **100.3** | **113.8** | 38.3 |

There they are: shoulder_lift reaches **-104.3**, wrist_roll **113.8**, wrist_flex **100.3**. All past 100. ✅
5. **"How do you know shoulder_lift 25%?"** Percentiles = **lining kids up by height**. Line up all 22,771 shoulder_lift values from lowest to highest. The value a quarter of the way along is the 25% (here -102.8). So **a quarter of all frames are at -102.8 or lower**, past -100. That's why the old rule flagged so many frames (37.5%): the arm spends lots of time in its rest pose down there.
6. **"Where? I don't see it."** Read the table like map coordinates: find the **row** (`25%`) on the left, the **column** (`shoulder_lift`) on top, and where they cross is the value (-102.8).

## Lesson
**Don't trust a claim, even the coach's, until you see the number.** I asked to see 104 and 114, ran the code, and found them myself. That's what an auditor does.

## In my words (checked)
> "if i see the first fail , i will try do go look at dataset, what is going on with joints , does the data collector set the joints to other limit .So, i can look at it , typically should be 100 , so i will confrimed it and labaled it ,it is not bad data"

Feedback: **exactly the auditor's process** ✅. See a FAIL → look at the data → find the cause (a different scale) → confirm with numbers → label it correctly (tool issue, not bad data).

## Third test: lerobot/svla_so100_pickplace
The coach also ran the fixed tool on a well-known lerobot dataset (SO-100, 50 tries, 19,631 frames). **PASS 4/4.** It looks different in two ways, and the tool handled both without changes:
- Joint names have a `main_` prefix (`main_shoulder_pan`, …) and no `.pos` ending. The tool reads them from info.json.
- Cameras are called `top` and `wrist` (svla_so101 uses `side` and `up`).

Its Actions line also carries the note: main_wrist_roll goes past ±100 (up to 123.6).

## Generality fixes: what differed between datasets
| Difference | Datasets | What happened |
|---|---|---|
| Camera names | side/up vs top/wrist | Nothing broke (no check uses cameras yet; Days 15–16 will) |
| Joint naming | `.pos` endings vs `main_` prefix | Nothing broke: names read from info.json, `.pos` dropped |
| Number scale | capped at ±100 vs going past 100 | **Broke check #7 → fixed** (clipping = only 99.9–100.1, plus a note) |

## Key ideas
- One dataset = demo; two or three = tool.
- When a check FAILs, first ask: **is it the data, or is it my tool?**
- Read limits from the data instead of assuming them.
- Show the number. Never just trust a claim.

## 🎉 Week 2 complete
In Week 2 I wrote real audit checks (episodes, timing, actions, empty tries), did my first human label review, combined everything into one tool, and proved it works on 3 different datasets.

## Next: Day 15
Camera-robot sync: compare each video's duration to its data time span and flag any mismatch over 0.5 s (`check_sync()`).

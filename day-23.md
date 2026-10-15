# Day 23: Sample audit, part 1: run it ✅ (Oct 10, 2026)

## Goal
"Proof helps: one well-checked public dataset shows how the checks work." Today: pick a showcase dataset, run the full audit tool on it end to end (videos included), save the raw output, and give every flag a verdict.

Plan text:
- **WHY:** Proof helps: one well-checked public dataset shows how the checks work.
- **LEARN:** Choose a showcase dataset (a public SO-101 set, with real defects if found).
- **DO:** Run the audit tool on it end to end. Save the raw output.
- **DONE WHEN:** Raw audit output saved for the showcase dataset.

## Analogy: a photographer's showcase
A photographer shows sample photos instead of just saying "I take good photos." In the same way, I show one public dataset checked end to end so anyone can see how the checks work.

## Step 1: Choose the showcase dataset
I chose **MaxT90/so101-pick-place** because it has **real findings**: the 16-second dead start in try 0 (Day 20), no calibration file (Day 18), and the try 45 gripper flag. A clean dataset doesn't show off the skills; one with real findings does.

## Step 2: Run the full audit and save the raw output
In Terminal (in `Downloads`, `(lerobot)` showing), with the newest tool (9 checks, including #1c Duplicates):

```
python audit_checks_v1.py MaxT90/so101-pick-place --videos | tee maxt90_audit_raw.txt
```

- `--videos` runs every check, including decoding every MP4 (#5b), so it takes a few minutes.
- `| tee maxt90_audit_raw.txt` is like a **receipt printer**: it shows the results on screen and saves them to a file at the same time. That file is the raw output, the proof the audit was done.

Raw output saved: [raw/maxt90_audit_raw.txt](raw/maxt90_audit_raw.txt)

```
========================================================================
ROBOT DATASET AUDIT: automated checks (audit_checks_v1)
========================================================================
Dataset:    MaxT90/so101-pick-place
Robot type: so_follower
Episodes:   50   Frames: 22771   FPS: 30
Joints:     shoulder_pan, shoulder_lift, elbow_flex, wrist_flex, wrist_roll, gripper
------------------------------------------------------------------------
PASS   #1-2 Episodes       all 50 tries present (0-49), none empty, shortest 346 frames
PASS   #1c  Duplicates     no copy-paste tries (50 unique fingerprints)
FAIL   #3   Lengths        1 too long [0]; normal 438 frames (14.6 s), range 346-948, limits 219-876
PASS   #4   Timing         steady at 30 fps (avg step 0.03333 s, biggest 0.03333 s), 0 skipped frames
PASS   #5   Sync           2 cameras in sync (wrist max gap 0.000 s, overhead max gap 0.000 s), 0 tries over 0.5 s
PASS   #5b  Videos         2 cameras fully readable (wrist 22771/22771, overhead 22771/22771 frames)
PASS   #6   Action/state   robot follows orders; mean gap 0.9-3.1, gaps >20 in at most 0.6% of rows (shoulder_lift)
PASS   #7   Actions        no dead joints in any try; clipping under 1% (highest: wrist_flex 0.2%); note: shoulder_lift, wrist_flex, wrist_roll go past +/-100 (scale not capped at 100)
PASS   #7   Empty tries    0 empty tries; least-moving try 24 = 88% of typical (median 1084)
REVIEW #9   Endings (hint) watch 1 try, unusual end pose: try 45: gripper 14.5 (usual 0.8)
------------------------------------------------------------------------
OVERALL: FAIL (9/10 automated checks did not fail: 8 PASS, 1 REVIEW)
*** HUMAN REVIEW NEEDED: watch the tries listed on the REVIEW line before signing off
Not automated yet: #8 camera clear, #10 label correct (manual review);
#9 is a hint only.
========================================================================
```

## Step 3: Read the result
**OVERALL: FAIL (9/10 automated checks did not fail: 8 PASS, 1 REVIEW).**
- **8 PASS:** nothing missing, no copies, steady timing, cameras in sync, videos good, robot follows orders, no dead joints, no empty tries.
- **FAIL #3 Lengths:** try 0 is too long, **948 frames vs normal 438** (limits 219–876). This is the known **16 s dead start** proven on Day 20.
- **PASS #5b Videos:** **22,771 / 22,771** frames readable on both the **wrist** and **overhead** cameras.
- **REVIEW #9 Endings:** try 45 gripper ends at **14.5 vs usual 0.8**.
- **Note:** shoulder_lift, wrist_flex and wrist_roll go past **±100** (scale not capped at 100; no calibration file to confirm it, Day 18).

## Step 4: Review try 45
**What I saw (my words):**
> "look like gripper was open when the robot go back to rest,"

> "yes it end up in the try 45, task finished"

**Double check on the numbers** (gripper per second, 0 = closed, higher = more open):
- **state:** 0.8 at 0–2 s (closed, waiting) → opens to **27.6** at 3–5 s (reaching) → **1.5** at 6–7 s (closed on the brick, holding it) → opens to **14.5** at 8–9 s (release into the box) → stays at **14.5** until the end while the arm returns to rest.
- **action:** also about **14.8** at the end, so the operator never commanded the gripper closed, and the robot obeyed. **Not broken.**
- It's the **only try** that ends that open; the next highest is **try 2 at 6.2**.
- **Duration:** last timestamp **13.0 s** (about 13.1 s in the viewer), within the length limits (219–876 frames ≈ 7–29 s). A quick try, not a short one.

**Verdict: minor, not bad data.** Task finished; gripper left slightly open at rest.

## My questions
**(a) "but video was only 13.1 seconds right?"**
Yes, it matches the data: the last picture is stamped 13.0 s; add the length of that last frame and it's about 13.0–13.1 s. The tiny difference is rounding in the viewer.

**(b) "so why it said 14.5"**
14.5 is **how open the gripper is** on the 0–100 scale (0 closed, 100 fully open), **not seconds**. Don't confuse it with **14.6 s**, the normal try length from #3. Door analogy: 14.5 is how far the door is open; 13.1 s is how long you were in the room.

**(c) "how do you that open 14.5 , when i look at video was only 13.1"**
The number comes from the **data** (`observation.state`, 6 joint numbers per picture; the 6th is the gripper), not the video. The video is just pictures. Check it yourself:

```
import pandas as pd
df = pd.read_parquet("hf://datasets/MaxT90/so101-pick-place/data/chunk-000/file-000.parquet")
e = df[df['episode_index']==45]; print(e['timestamp'].iloc[-1], e['observation.state'].iloc[-1])
```

That prints the last timestamp (about 13.0 s) and the 6 joint numbers at that moment; the last one is the gripper, 14.5.

**(d) "what is usual 0.8 mean"**
It's the **median end-gripper value across all 50 tries**: almost closed. Analogy: 50 people leave a room, almost everyone shuts the door (0.8), one leaves it ajar (14.5). Nothing broke; that one is just different. That's why it's a **REVIEW, not a FAIL**.

## All flags now have verdicts
| Flag | Verdict | Level | Fix |
|---|---|---|---|
| Try 0, #3 too long (948 vs 438 frames) | 16 s dead start, then a normal task | Major | Trim the first 16 s (or remove the try) |
| Try 45, #9 gripper 14.5 vs 0.8 | Task finished, gripper left slightly open at rest | Minor | None needed; note it |
| No calibration file (values past ±100) | Can't verify the scale | Minor | Include the calibration file |

**49 of 50 usable (98%), passes the 85/15 rule.**

## Key ideas
- **Show your work.** One well-checked public dataset makes a good example.
- **Pick a dataset with real findings.** A clean dataset shows nothing; real defects show the skill.
- **Save the raw output (`tee`).** Screen + file at once; the file is the evidence behind the report.
- **Every flag gets a verdict.** Code flags, a human watches, the numbers confirm, then write the verdict.
- **Know your units.** 14.5 (gripper opening) ≠ 14.6 s (normal length) ≠ 13.1 s (try 45's length).
- **REVIEW ≠ FAIL.** "Different from the rest" isn't "broken."

## Checklist progress
- Full audit run on MaxT90/so101-pick-place with all 9 automated checks + #9 hint, videos included
- New deliverable: [Sample audit raw output: MaxT90](raw/maxt90_audit_raw.txt)
- Closed: try 45 open item from Days 20–22 (minor, not bad data)
- Still open: MaxT90 coverage not scored yet

## Next: Day 24
Sample audit, part 2: write it up. Fill the Day 22 template with these Day 23 results, written the way a team reads it (what, where, why it matters), and export a 2-page PDF sample report.

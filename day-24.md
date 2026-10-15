# Day 24: Sample audit, part 2: write it up ✅ (Oct 11, 2026)

## Goal
"Raw output isn't a report. The write-up is the skill." Today: fill the Day 22 template with the Day 23 MaxT90 results, write every finding the way a team reads it (**what, where, why it matters**), and export a 2-page PDF sample report.

Plan text:
- **WHY:** Raw output isn't a report. The write-up is the skill.
- **LEARN:** Re-read the template from Day 22.
- **DO:** Fill the template with the Day 23 results. Write findings as a team would read them: what, where, why it matters. Export PDF.
- **DONE WHEN:** A finished 2-page sample audit report PDF exists.

## Analogy: lab results vs. the doctor explaining them

## Step 1: The finding formula (what, where, why it matters)
Every finding answers 3 questions, then gives a fix. Worked example from my coach, for the try 0 finding:

> **Major: dead start in try 0**
> - **What:** the robot sits completely still for the first 16 seconds, then does the task normally.
> - **Where:** try 0, seconds 0 to 16 (948 frames vs a normal 438).
> - **Why it matters:** a robot (policy) trained on this may learn to freeze for no reason before starting.
> - **Fix:** trim the first 16 seconds, or remove the try.

## Step 2: I wrote the other two findings
**My words (exact):**
> "Minor ; No calribration file is included so we do actually tell you , the joint go past 100 or -100 and no one can check what the numbers mean"

> "2. Minor; when we check the try 45 , we noticed that gripper left open in try 45. We saw the task was finished in try 45 ."

**Review note:** I nailed the **What** in both. Each one was missing the **Where** and the **Why it matters**. Completed versions:

> **Minor: no calibration file**
> - **What:** no calibration file is included, so we can't tell what the joint numbers mean, and some joints go past 100 or -100.
> - **Where:** all tries, mostly shoulder_lift, wrist_flex and wrist_roll.
> - **Why it matters:** nobody can verify the numbers are right, and another team can't safely reuse the data.
> - **Fix:** upload the calibration file.

> **Minor: gripper left open in try 45**
> - **What:** the gripper stays a little open (**14.5 vs a normal 0.8**) when the arm goes back to rest. The task still finished.
> - **Where:** try 45, the last 4 seconds.
> - **Why it matters:** it's small, but the robot might learn not to fully close the gripper at the end.
> - **Fix:** keep it, or have the operator close the gripper before stopping.

## Step 3: The PDF
Deliverable: a 2-page sample report (`sample_audit_report_maxt90.pdf`, not included in this log)

- **2 pages, US Letter.**
- **Verdict box** at the top: **"PASS after one fix: 49 of 50 tries usable (98%)."** No critical issues; one major (try 0, fixable by trimming, no re-recording needed); two minor.
- **"What this audit can't catch" box:** wrong labels and frozen-but-decodable camera pictures. Only sampled human video review covers them (2 of 50 tries watched in this sample: tries 0 and 45).
- **The 6 template sections:** 1) dataset overview, 2) checks run (9 automated + human review), 3) findings (Critical / Major / Minor table with evidence), 4) unusable episodes (try 0; 49/50 = 98%, passes 85/15), 5) recommendations, 6) coverage score.
- **What / Where / Why / Fix blocks** for all 3 findings.

| Level | Finding | Tries |
|---|---|---|
| Critical | None | — |
| Major | Dead start: still for 0–16 s, then normal | 0 |
| Minor | No calibration file; joint scale can't be verified | All |
| Minor | Gripper left open at the end (task finished) | 45 |

## My questions
**(a) "can you explain me Human review part"**
Human review = the parts **a person** checks, because code can't watch video. In this report:
- **Try 0** was watched: the robot froze for 16 s, then did the task. Confirmed.
- **Try 45** was watched: the gripper was left open, but the task finished. Confirmed.
- **Calibration** was checked by hand with the Day 18 checklist: no file, **1/5**.
- **#8 camera clear** and **#10 label correct** are marked **"not fully reviewed"**, because only 2 of 50 tries were watched. A fuller audit would watch a sample of **about 10 tries**.

**(b) "what is not coverage score , what is it look like"**
Coverage score = the **Day 19 variety grade**: brick position, objects and lighting, each scored 1–3, total out of 9 (svla_so101_pickplace scored **4/9**: position 2, objects 1, lighting 1). MaxT90 hasn't been scored yet, so the report says **"Not scored in this sample"** instead of inventing a number. Filled in, it would look like this:

| Category | Score | Note |
|---|---|---|
| Brick position | ?/3 | how many spots |
| Objects | ?/3 | how many items |
| Lighting | ?/3 | how many light setups |
| **Total** | **?/9** | |

## Key ideas
- **Raw output isn't a report.** Lab results vs. the doctor explaining them; the explanation is the useful part.
- **What, where, why it matters, then fix.** The "what" alone is a note; all four make it a finding.
- **Lead with the verdict.** One line a busy team reads first: "PASS after one fix: 49 of 50 usable (98%)."
- **Say what you can't catch.** Wrong labels and frozen pictures need a human; be honest about how much was watched.
- **Never invent a number.** "Not scored in this sample" beats a made-up coverage score.

## Checklist progress
- New deliverable: Sample Audit Report: MaxT90 (PDF, not included in this log), 2 pages, US Letter
- All 3 MaxT90 findings written as What / Where / Why / Fix
- Still open: MaxT90 coverage not scored; #8 and #10 only sampled on 2 of 50 tries

## Next: Day 25
Business day (not published).

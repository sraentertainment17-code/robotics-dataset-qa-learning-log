# Day 22: The audit report format ✅ (Oct 10, 2026)

## Goal
"The report is the deliverable." Today: learn the **6 parts of a team audit report**, explain each one in my own words, and turn them into a fill-in template, `audit_report_template.md`, that stays about **2 pages** when filled.

Plan text:
- **WHY:** The report is the deliverable.
- **LEARN:** Outline: 1) dataset overview, 2) checks run, 3) findings table (critical/major/minor), 4) unusable-episode list, 5) recommendations, 6) coverage score.
- **DO:** Write the template as markdown with placeholders. Keep it to 2 pages when filled.
- **DONE WHEN:** `audit_report_template.md` exists.

## Analogy: a car inspection sheet
When you get your car inspected, you never see the mechanic's tools. You get **the sheet**: what's good, what's wrong, what to fix. My audit tool is the mechanic's toolbox; **the report is the sheet the team reads.** Teams read the report, not my script.

## Step 1: A filled example first (MaxT90)
I was shown the 6 parts filled in with what I found on MaxT90/so101-pick-place (Days 14–21):

1. **Dataset overview:** MaxT90/so101-pick-place: 50 tries, 22,771 frames, 30 fps, robot so_follower, task "pick and place."
2. **Checks run:** 9 automatic checks (episodes, duplicates, lengths, timing, sync, videos, action/state, actions, empty tries), plus a human review of endings, camera and labels.
3. **Findings table:**

| Level | Finding | Tries |
|---|---|---|
| Critical | none | none |
| Major | 16-second dead start (robot frozen, then normal) | 0 |
| Minor | joint values go past ±100, with no calibration file | all |
| Minor | unusual gripper end pose (still to review) | 45 |

4. **Unusable tries:** try 0, until it's trimmed. 49 of 50 usable (98%), passes the 85/15 rule.
5. **Recommendations:** trim the first 16 seconds of try 0, include the calibration file, add more brick positions and lighting.
6. **Coverage score:** still to be done for MaxT90 (svla scored 4/9 on Day 19).

The three levels:
- **Critical:** the robot could learn something dangerous or wrong.
- **Major:** that try needs fixing.
- **Minor:** good to fix, but it won't break training.

## Step 2: "can you give me example"
Before writing my own, I asked "can you give me example", so I got a one-line purpose for each part:
1. **Dataset overview:** which dataset I checked and its basic facts (tries, frames, robot). The name tag on the report.
2. **Checks run:** every test I did, so the team knows exactly what was covered and what wasn't.
3. **Findings table:** every problem I found, sorted by how serious it is (critical, major, minor), with the try numbers.
4. **Unusable tries:** the tries they shouldn't train on until fixed, plus how many good ones are left.
5. **Recommendations:** what the team should do next to fix the problems or collect better data.
6. **Coverage score:** how much variety the dataset has (brick spots, objects, lighting), so they know if the robot will only work in one setup.

## Step 3: My version (my words)
> "1.dataset overview;  so101 robot , pick and place ;50 tries , 22771 frames, 30 fps"

> "2. automatic checks ( ep,duplicates,odd lengths, timing , syns, videos, actio/state , pluse human review of endings, camera , and labels"

> "finding table / critical none / major 16 seconds dead start ( robot frozen or video start recording first) / minor no calibration file , unusaul gripper end pose"

> "4. try 0 until , trim or rework it"

> "5. trim try 0 the first 16 second ,inlucding the calibration file, add more brick postition and switch light"

> "6." (left blank)

## Step 4: Review fixes
- **#1 and #2 are right ✅.** In #2, add the last two automatic checks, **actions** and **empty tries**, so the list has all 9.
- **#3 findings table is right ✅**, and **I added *why* the dead start happened** (robot frozen, or the video started recording first). That's exactly what a team wants: not just "what" but "why."
- **#4:** say how many are left: "try 0 until trimmed; **49 of 50 usable (98%), passes the 85/15 rule**." Teams always want that number.
- **#6:** MaxT90 coverage **isn't scored yet**, so write "Coverage: brick position ?/3, objects ?/3, lighting ?/3, to be scored by looking at first frames," the way I scored svla on Day 19 (**4/9**).

## Step 5: The template: `audit_report_template.md`
A shareable markdown file with `{{placeholders}}`, about 2 pages when filled:
- **Header:** dataset, team, auditor, date audited.
- **One-line overall verdict** near the top: `{{PASS / PASS after fixes / FAIL}}: {{one line}}`.
- **"What this audit can't catch"** line: wrong labels and frozen camera pictures are covered only by **sampled human review** (the honest limit from Day 21).
- **1. Dataset overview:** name, robot, task, tries, frames, fps, cameras, joints, date audited.
- **2. Checks run:** the 9 automated checks (#1-2 Episodes, #1c Duplicates, #3 Lengths, #4 Timing, #5 Sync, #5b Videos, #6 Action/state, #7 Actions, #7 Empty tries), each with "what it asks" and a result; plus human review of #9 endings, #8 camera clear, #10 label correct, calibration (Day 18 checklist, /5) and coverage (Day 19 rubric, /9).
- **3. Findings:** Level | Finding | Tries | Evidence, with the one-line Critical / Major / Minor definitions.
- **4. Unusable episodes:** Try | Reason | Fix, then "**X of N usable (Y%), passes/fails the 85/15 rule**."
- **5. Recommendations:** Major fixes first, then Minor, then next recordings.
- **6. Coverage score:** position / objects / lighting, each 1–3, total /9 (narrow / moderate / broad).
- **Example (filled): MaxT90/so101-pick-place** after the blank template, so I can see what "done" looks like.

The filled example's findings:

| Level | Finding | Tries | Evidence |
|---|---|---|---|
| Critical | none | — | — |
| Major | 16 s dead start: frozen 0–15 s, then a normal ~15 s task | 0 | #3 FAIL (948 vs 438 frames); verified by video and per-second movement (Day 20) |
| Minor | No calibration file, so values past ±100 can't be verified | all | #7 note + Day 18 checklist |
| Minor | Gripper end pose 14.5 vs usual 0.8, still to review | 45 | #9 hint |

Verdict line: **PASS after one fix: 49 of 50 usable (98%), passes 85/15.** Coverage: still to be scored.

## Key ideas
- **The report is the product.** The script is the mechanic's toolbox; the team reads the inspection sheet.
- **Six parts, always the same order:** overview, checks run, findings, unusable list, recommendations, coverage.
- **Severity levels tell the team what to do first:** Critical = dangerous or wrong learning, Major = fix that try, Minor = nice to fix.
- **Always give the number:** "49 of 50 usable (98%), passes 85/15" is what a team looks for first.
- **Finding + evidence + cause + fix.** Saying *why* (dead start because recording began early) turns a scary FAIL into a simple job.
- **State the limits up front.** "What this audit can't catch" builds trust (Day 21).

## Checklist progress
- 9 automated checks in [audit_checks_v1.py](audit_checks_v1.py): #1-2, #1c, #3, #4, #5, #5b (with `--videos`), #6, #7 actions, #7 empty tries
- Human review: #8 camera clear, #9 endings (hint), #10 label correct, calibration (/5), coverage (/9)
- New deliverable: Audit Report Template v1 (`audit_report_template.md`, not included in this log) with a filled MaxT90 example
- Open: MaxT90 try 45 (gripper 14.5 vs 0.8) not watched yet; MaxT90 coverage not scored yet

## Next: Day 23

# Day 21: Week 3 review: break it on purpose ✅ (Oct 10, 2026)

## Goal
"If you know how it fails, you can promise what it catches." Today: think of **3 ways a dataset could fool my audit tool**, then actually try one: **duplicate an episode** (copy try 5 over try 6) and see if the tool notices. Document the result as an **adversarial test**, so when a team asks "what can't it catch?", there's an honest answer.

Plan text:
- **WHY:** If you know how it fails, you can promise what it catches.
- **LEARN:** Think of 3 ways a dataset could fool your script.
- **DO:** Try one: duplicate an episode's parquet rows; see if the script notices (it should flag identical episodes). Document the result.
- **DONE WHEN:** You have one documented "adversarial test" with outcome.

## Analogy: testing a smoke alarm with a candle
You don't wait for a real fire to find out if the smoke alarm works. You hold a candle under it on purpose. Today I fed my own tool **bad data on purpose** to see if it beeps. If it doesn't, better to find out now than in front of a team.

## Step 1: Three ways a dataset could fool the tool
I was given an example list:
1. **Copy-paste try.** The same try is saved twice under two numbers, so it looks like 50 tries but only 49 are real.
2. **Wrong label.** Every try says "pick the pink brick", but in some tries the robot picks something else. Code reads the **label**, not the **video**.
3. **Frozen camera.** The video decodes fine (passes #5b) but shows the same picture the whole time. It still counts as 11,939 good frames.

Today's test: **#1, the copy-paste try.**

## Step 2: Make a fake dataset (try 6 = a copy of try 5)
In Terminal: `cd ~/Downloads`, typed `python`, then pasted one at a time:
```python
import pandas as pd
import audit_checks_v1 as a
info, eps, df = a.load("lerobot/svla_so101_pickplace")
names = a.joint_names(info, "action")
fake = df[df["episode_index"] == 5].copy()
fake["episode_index"] = 6
df2 = pd.concat([df[df["episode_index"] != 6], fake], ignore_index=True)
print(a.check_actions(df2, names))
print(a.check_empty(df2, names))
print(a.check_action_state(df2, names))
```
What each line does:
1. `import pandas as pd`: load the table tool.
2. `import audit_checks_v1 as a`: load **my own audit tool** as a toolbox (nickname `a`), so I can call each check by hand.
3. `info, eps, df = a.load(...)`: the tool's own loader gives back the label (info.json), the tries list and all 11,939 rows.
4. `names = a.joint_names(info, "action")`: the 6 joint names.
5. `fake = df[df["episode_index"] == 5].copy()`: copy every row of **try 5**.
6. `fake["episode_index"] = 6`: relabel the copy as **try 6**.
7. `df2 = pd.concat([...])`: the real data with the **real try 6 thrown out** and the **fake one put in its place**.
8. The three `print` lines: run three of my checks on the fake data.

My output:
```text
(True, 'no dead joints in any try; clipping under 1% (highest: elbow_flex 0.7%)')
(True, '0 empty tries; least-moving try 24 = 77% of typical (median 860)')
(True, 'robot follows orders; mean gap 1.7-4.1, gaps >20 in at most 2.9% of rows (shoulder_lift)')
```

## Step 3: The surprise: all three said PASS
**All three returned True (PASS), even though try 6 is a fake copy.** The tool didn't notice. The smoke alarm stayed silent.

Why? It's not a bug in the checks. **None of them was built to compare tries with each other.** Each one asks its own question about each try ("does it move?", "is it stuck?", "does it follow orders?"), and a copied try is a **perfectly normal-looking try**, so it passes every one.

**Analogy: grading two identical essays separately.** Each essay is well written and gets an A. Nobody put them side by side to see that one was copied.

**Why a team cares:**
- They think they have **50 real tries but only got 49**.
- Worse, the robot sees that try **twice**, so it **over-learns** it (learns it extra hard), which skews training.

## Step 4: The fix: a fingerprint for every try
Compare tries **to each other**: give each try a "fingerprint" made from all its numbers and flag any two that match.
```python
sig = df2.groupby("episode_index")["observation.state"].apply(lambda s: hash(str(list(map(list, s)))))
print(sig[sig.duplicated(keep=False)])
```
What each line does:
1. `df2.groupby("episode_index")["observation.state"]`: take each try's joint positions separately. `.apply(lambda s: hash(str(...)))` turns **all** of a try's numbers into text and squeezes it into one big number: the **fingerprint**.
2. `sig.duplicated(keep=False)`: mark every fingerprint that appears more than once (`keep=False` = show **both** copies, not just the second). `print(...)` shows those tries.

My output:
```text
episode_index
5   -5488951331346229659
6   -5488951331346229659
Name: observation.state, dtype: int64
```
**Caught it ✅** Tries **5 and 6 have the same fingerprint**, so the copy is exposed.

**The number itself means nothing.** It's like a **barcode**: you don't read a barcode, you just check whether two items have the same one. Same barcode = same try.

## Step 5: Write-up (my words)
Example given:
> "Test: I copied try 5 over try 6. Result: my original checks all passed, so they missed it. Fix: I added a fingerprint check, and it flagged tries 5 and 6 as identical. Now the tool catches copy-paste tries. It still can't catch wrong labels or a frozen camera picture; those need a human."

My version:
> "I copied try 5 over try 6 , originally checks all passed and i added a fingerprint check , i saw that the try 5 and try 6 were the same identical"

That's right ✅. **Review addition:** add one line saying what it **still can't catch**: "It can't catch wrong labels or a frozen camera picture; those need a human." That's the honest answer when a team asks "what can't it catch?"

## Step 6: Added to the tool as check #1c
New function `check_duplicates(df)` in `audit_checks_v1.py` (512 → 549 lines), shown right after #1-2 in the summary:
- Fingerprints each try's `observation.state` numbers (all rows stacked into one grid, then hashed with SHA-1; falls back to `action` if there's no state column).
- **FAIL** if two or more tries share a fingerprint, listing the groups, e.g. `2 identical tries: [5, 6]`.
- **PASS** message: `no copy-paste tries (50 unique fingerprints)`.
- All existing checks unchanged.

Tests:
```text
Real svla data:      (True, 'no copy-paste tries (50 unique fingerprints)')
Doctored df2:        (False, '2 identical tries: [5, 6]')
```
Full run on svla_so101_pickplace:
```text
PASS   #1-2 Episodes       all 50 tries present (0-49), none empty, shortest 183 frames
PASS   #1c  Duplicates     no copy-paste tries (50 unique fingerprints)
PASS   #3   Lengths        no odd tries; normal 230.5 frames (7.7 s), range 183-306, limits 115-461
...
OVERALL: PASS (9/9 automated checks did not fail: 8 PASS, 1 REVIEW)
```
Full run on MaxT90/so101-pick-place: `#1c PASS (50 unique fingerprints)`; still FAIL on #3 (try 0 dead start, explained on Day 20): **OVERALL: FAIL (8/9 automated checks did not fail: 7 PASS, 1 REVIEW).**

## Limit of the fix (possible future test)
The exact fingerprint only catches **exact** copies. A **near-copy** (try 5 with tiny noise added to every number) gets a completely different fingerprint and slips through. Catching that would need a "how similar are these two tries?" check. A good next adversarial test.

## What the tool still can't catch (honest answer for teams)
| Way to fool it | Caught? |
|---|---|
| Copy-paste try (exact) | ✅ Now caught by #1c |
| Near-copy (copy + tiny noise) | ❌ Not yet (future test) |
| Wrong label | ❌ Needs a human watching (#10) |
| Frozen camera picture | ❌ Needs a human watching (#8); #5b only checks frames decode |

## Key ideas
- **Break it on purpose.** Test the smoke alarm with a candle before a real fire.
- **Checks that look at one try at a time can't see copies.** A copy is a perfectly normal try. Comparing tries **to each other** needed a new check.
- **Fingerprint = barcode.** The number means nothing; only matches matter.
- **Exact fingerprints catch exact copies only.** Noise defeats them.
- **Honest limits build trust.** "Here's what it catches, here's what needs a human" builds more trust than "it catches everything."

## Checklist progress
- #1, #2 Episodes; **#1c Duplicates (new today)**; #3 Lengths; #4 Timing; #5 Sync; #5b Videos (with `--videos`); #6 Action/state; #7 Robot moves: ✅ automated (**9 automated checks**)
- #9 Task finished: 🟡 partly automated (REVIEW hint) + watching
- #8 Camera clear, #10 Label correct: manual review
- Tool: [audit_checks_v1.py](audit_checks_v1.py) (549 lines). svla_so101_pickplace = PASS 9/9; MaxT90/so101-pick-place = FAIL on #3 (try 0 dead start, explained) + REVIEW try 45 (still open from Day 20)

🎉 **Week 3 complete (Days 15–21):** sync, video decoding, truncation hint, calibration checklist, coverage rubric, the full 9-check audit tool, and the first adversarial test.

## Next: Day 22
The audit report format. Outline: dataset overview, checks run, findings table (critical/major/minor), unusable-episode list, recommendations, coverage score. Write `audit_report_template.md` with placeholders, 2 pages when filled.

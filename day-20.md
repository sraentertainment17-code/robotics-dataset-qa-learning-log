# Day 20: Assemble the full audit script ✅ (Oct 10, 2026)

## Goal
"Ten checks in one run is a product. Ten separate scripts is a hobby." Today: run the **one** audit tool on a whole dataset with **every** automatic check switched on (including the video check), read the summary line by line, and close the last two gaps on the "Not automated yet" list by building **#3 odd lengths** and **#6 action vs state** by hand first, then adding them to the tool. Then test it end to end on two datasets.

The plan called this file `audit.py` with a single `run(dataset)` entry point. Ours is `audit_checks_v1.py`: one command, one dataset name, one summary page.

## Analogy: the full car inspection
Days 8–19 were like checking the tires one day, the brakes the next, the lights the day after. Today is the **full inspection in one pass**: you drive the car in, and one report comes out with every part graded. Each line in the summary is one part of the car, and the word on the left (PASS / FAIL / REVIEW / SKIP) is the grade.

## Step 1: Run the whole tool, every check on
Saved the newest `audit_checks_v1.py` (it got new checks on Days 15–17) to **Downloads**, opened a new Terminal and ran, one at a time:
```bash
conda activate lerobot
cd ~/Downloads
python audit_checks_v1.py lerobot/svla_so101_pickplace --videos
```
- `conda activate lerobot`: switch on the LeRobot Python setup (where pandas, PyAV and LeRobot are installed).
- `cd ~/Downloads`: go to the folder where the tool was saved.
- `python audit_checks_v1.py <dataset> --videos`: run every check on that dataset. `--videos` also downloads and plays **both camera videos** frame by frame (#5b), so it takes a few minutes.

Result: **OVERALL: PASS (7/7 automated checks did not fail: 6 PASS, 1 REVIEW).**

## Step 2: What every line means (and which day built it)
**The top part** is the car's ID card: dataset name, robot (`so100_follower`), 50 tries, 11,939 pictures, 30 pictures per second, the 6 joint names.

| Line | Grade | What it says | Built on |
|---|---|---|---|
| #1–2 Episodes | PASS | All 50 tries are there (0–49), none empty, shortest 183 frames | Day 8 |
| #4 Timing | PASS | Every gap between pictures is 0.03333 s (= 1 ÷ 30), 0 skipped. A steady heartbeat. | Day 9 |
| #5 Sync | PASS | Both cameras line up with the robot's numbers, gap 0.000 s. Video and robot dance to the same beat. | Day 15 |
| #5b Videos | PASS | Both video files play every frame, 11,939 / 11,939, no freezing | Day 16 |
| #7 Actions | PASS | No dead (stuck) joint; almost nothing hits the limit, worst is elbow_flex 0.7% | Day 10 |
| #7 Empty tries | PASS | Every try has real movement; laziest try 24 = 77% of a normal try | Day 12 |
| #9 Endings | REVIEW | Try 49 ends in an unusual pose: shoulder_lift -79.0 (usual -98.6), wrist_flex 61.3 (usual 73.8) | Day 17 |

**The bottom part:**
- **OVERALL: PASS**: none of the 7 checks failed (6 PASS + 1 REVIEW).
- **HUMAN REVIEW NEEDED**: watch try 49 before signing off. Already done on Day 17: brick in the box, arm just resting a little to the right, so "not cut off" ✅.
- **Not automated yet**: #3 odd lengths, #6 action vs state, #8 camera clear, #10 label correct.

**REVIEW is not FAIL.** It's the code saying "a human should look here." The code points at the risky spots; you make the final call.

In short: the code did the boring counting in a few minutes and pointed at the one try worth watching.

## Step 3: Why weren't #3 and #6 automated?
My question: "first explain me 3# odd length and 6 action vs state are not automaed yet"

Answer: they **can** be done by code. We just hadn't built them into the tool yet. I already did both by hand at the very start:
- **#3 Odd lengths (Day 2):** I looked at the try lengths myself and saw they vary (shortest 183 frames). The tool counted tries but never flagged a try for being too long or too short.
- **#6 Action vs state (Day 3):** I checked only the **first row** (biggest gap 2.93 on wrist_roll). The tool didn't check every row.

So the plan for the rest of Day 20: build each one by hand, then add it to the tool. #3 first (the easier one).

## Step 4: Build #3 (odd lengths) by hand
**Plan:** find the typical try length (the **median** = the middle one), then flag any try that's **less than half** of it or **more than double** it.

**Analogy: a height chart.** If most kids are about 4 feet tall, a 1-foot or 9-foot "kid" is worth a second look.

In Terminal, typed `python`, then pasted one at a time:
```python
import pandas as pd
eps = pd.read_parquet("hf://datasets/lerobot/svla_so101_pickplace/meta/episodes/chunk-000/file-000.parquet")
med = eps["length"].median()
print(med, eps["length"].min(), eps["length"].max())
odd = eps[(eps["length"] < med * 0.5) | (eps["length"] > med * 2)]
print(len(odd), odd["episode_index"].tolist())
```
What each line does:
1. `import pandas as pd`: load the table tool.
2. `eps = pd.read_parquet(...)`: open the **episodes list** (one row per try, with its `length` in frames) straight from Hugging Face.
3. `med = eps["length"].median()`: the middle length = our "normal" try.
4. `print(med, min, max)`: show the normal, shortest and longest.
5. `odd = eps[(... < med * 0.5) | (... > med * 2)]`: keep only tries under half **or** (`|`) over double the normal.
6. `print(len(odd), ...tolist())`: how many odd tries, and which try numbers.

My output:
```text
230.5 183 306
0 []
```
How to read it:
- **230.5** frames = the typical try ≈ **7.7 s** (230.5 ÷ 30)
- **183** = the shortest ≈ **6.1 s**
- **306** = the longest ≈ **10.2 s**
- The "odd" zone: under **115** frames (half of 230.5) or over **461** (double). Every try is between 183 and 306, nowhere near either edge.
- `0 []` = 0 odd tries, and the empty list means no try number to go watch.

**Check #3: PASS.**

### Explained again, slower (I asked "explain more about this")
- Every try is a little movie of the robot picking up the brick. **Length** = how many pictures (frames) that movie has. 30 pictures per second, so 230 frames ≈ 7.7 s, 183 ≈ 6.1 s, 306 ≈ 10.2 s.
- **Why look for odd lengths?** The robot does the same job every time, so every try should take about the same time, give or take a few seconds. **Much shorter** = maybe the recording stopped early and the task never finished. **Much longer** = maybe the robot got stuck, dropped the brick and tried again, or the person forgot to press stop.
- **Why the median, not the average?** Line all 50 tries up from shortest to longest and take the middle one. **One weird try can't drag the median up or down** the way it can drag an average.
- **Analogy: pizza delivery.** The shop says "about 30 minutes." 20 or 40 minutes is normal. 5 minutes (did they even cook it?) or 90 minutes (did they get lost?) means something went wrong. All 50 of our "deliveries" took 6 to 10 seconds: all normal.

### Saying it back
I asked "what you want to say", so I got an example restatement first:
> "Check #3 looks for odd lengths. Every try should take about the same time. The normal try was 230 frames, about 7.7 seconds. I flag any try under half (115) or over double (461). All 50 tries were between 183 and 306, so 0 were odd. PASS."

My version:
> "i checked 3# for odd lengths and every try look same time and normal try was 230 frames , about  7.7 seconds .I did flag any try under half 115 or over double 461  , all 50 tries were between 183 and 306 so 0 was odd pass"

Good team explanation ✅. **Fix:** say "**I set the limits at** 115 and 461", not "I did flag", because nothing actually got flagged.

## Step 5: Timestamp vs timing vs odd length (my confusion)
My question: "btw what is difference between odd lenght ,timing and timestamp"

| Word | What it is | Question it answers |
|---|---|---|
| **Timestamp** | The clock time stamped on each picture: frame 0 = 0.000 s, frame 1 = 0.033 s, frame 2 = 0.067 s… Like the time printed on every photo in an album. | It's the **raw data**, not a check. |
| **Timing (#4)** | The **gap between two pictures in a row**. Every gap should be 0.033 s (1 ÷ 30). | Is the heartbeat steady, with no skipped pictures **inside** a try? |
| **Odd length (#3)** | The **whole try at once**: how many pictures it has in total. | Is this try way too short or too long **compared with the others**? |

**Analogy: a running race.** The **timestamp** is the stopwatch reading at each step. **Timing** checks that the runner's steps are evenly spaced and nobody teleported. **Odd length** checks that the runner's total race time is close to everyone else's.

A try can pass one and fail the other: a **40-second try with perfectly steady steps passes timing but fails odd length.**

## Step 6: Build #6 (action vs state) by hand
Reminder: **action** = the order ("go to 30"), **state** = where the joint actually is ("I'm at 29"). Measure the gap on **every row for every joint**. Like checking whether a dog actually sits when you say "sit."

Still in Python, one at a time:
```python
import numpy as np
df = pd.read_parquet("hf://datasets/lerobot/svla_so101_pickplace/data/chunk-000/file-000.parquet")
names = ["shoulder_pan", "shoulder_lift", "elbow_flex", "wrist_flex", "wrist_roll", "gripper"]
gap = pd.DataFrame(np.abs(np.stack(df["action"]) - np.stack(df["observation.state"])), columns=names)
print(gap.describe().round(1))
```
What each line does:
1. `import numpy as np`: the number-crunching tool.
2. `df = pd.read_parquet(...)`: load **all 11,939 rows** of robot data.
3. `names = [...]`: the 6 joint names, to label the columns.
4. `np.stack(df["action"]) - np.stack(df["observation.state"])`: turn each column of lists into a grid (rows × 6 joints) and subtract **reality from the order** on every row. `np.abs(...)` turns minus signs into plain distances.
5. `gap.describe().round(1)`: the summary table per joint (Day 10 skill).

My output:
```text
       shoulder_pan  shoulder_lift  elbow_flex  wrist_flex  wrist_roll  gripper
count       11939.0        11939.0     11939.0     11939.0     11939.0  11939.0
mean            4.1            3.8         3.6         2.2         1.7      2.3
std             5.7            5.7         4.2         3.5         2.5      3.5
min             0.0            0.0         0.0         0.0         0.0      0.0
25%             0.2            0.5         0.6         0.2         0.1      0.2
50%             0.8            0.9         2.4         0.5         0.3      0.3
75%             7.0            5.1         4.4         2.7         2.3      5.4
max            28.5           35.8        27.7        22.7        14.4     29.8
```
How to read it (gaps on the -100 to 100 scale; small = the robot listened well):
- **count 11939**: every row was checked.
- **mean** 1.7 to 4.1: small. Like saying "go to 30" and the joint lands around 26–28.
- **50%** (middle gap) under 2.5 for every joint: half of all moments are almost a perfect match.
- **75%**: three out of four moments are within 7 or less.
- **max**: the single worst moment per joint, up to **35.8 on shoulder_lift**.

**Why are the max values bigger?** The robot needs a moment to catch up. When you tell it to move fast, the order jumps ahead first and the arm follows a split second later.

**Analogy: a dog chasing a thrown ball.** Right after the throw, the dog is far behind. Then it catches up. A big gap **for a moment** is normal; a big gap **all the time** is not. A broken motor would show a huge **mean** (like 30+), because the joint would never reach where it was told.

### Proving it's only a quick catch-up
```python
print((gap > 20).sum())
```
Counts the rows where each joint is more than 20 behind its order. My output:
```text
shoulder_pan     202
shoulder_lift    341
elbow_flex       117
wrist_flex         7
wrist_roll         0
gripper           38
```
As a share of 11,939 rows (check it with `print(((gap > 20).mean() * 100).round(1))`):

| Joint | Rows with gap > 20 | Share |
|---|---|---|
| shoulder_lift | 341 | ≈ 2.9% |
| shoulder_pan | 202 | ≈ 1.7% |
| elbow_flex | 117 | ≈ 1.0% |
| gripper | 38 | ≈ 0.3% |
| wrist_flex | 7 | ≈ 0.06% (almost never) |
| wrist_roll | 0 | 0% (never) |

So **97% or more of the time, every joint stays close to its order**. The big gaps come in quick bursts. It makes sense that **shoulder_lift** has the most: it's the big joint lifting the whole arm, so it's the slowest to catch up (the dog chasing the ball). A broken motor would show big gaps most of the time, not 3%.

**Check #6: PASS.**

### Saying it back
I asked for both explanations first ("FIRST CAN YOU DO IT , WHAT WE DID 6 AND 3"). The examples:
> **Check #3, odd lengths: PASS.** Every try should take about the same time. The normal try was 230 frames, about 7.7 seconds. I set the limits at half (115 frames) and double (461 frames). All 50 tries were between 183 and 306 frames, so 0 tries were odd.

> **Check #6, action vs state: PASS.** I compared what the robot was told to do (action) with what it actually did (state) on all 11,939 rows. The average gap was small, between 1.7 and 4.1 for every joint. Big gaps over 20 happened less than 3% of the time, and only during fast moves while the arm was catching up. That's normal. A broken motor would show big gaps most of the time.

My version of #6:
> "I checked what robot was told to do action with what actually did the state, on all 11939 rows , average gap was small and between 1.7 and 4.1 for every joint , big gaps over 20 happened less than 3% of the time when robot catching up the object"

Right ✅. **Fix:** the arm is catching up to its **order**, not to the object (the dog runs to where the ball was thrown). Add "PASS" at the end and it's shareable.

## Step 7: Add both checks to the tool
Two new functions in `audit_checks_v1.py` (432 → 512 lines), with their limits in the thresholds block at the top:
```python
LEN_MIN_X = 0.5       # a try under 0.5x the normal (median) length = too short
LEN_MAX_X = 2.0       # a try over 2x the normal (median) length = too long
AS_BIG_GAP = 20.0     # an order-vs-reality gap over 20 points = a "big gap" row
AS_MAX_MEAN = 15.0    # a joint whose AVERAGE gap is over 15 = not following orders
AS_MAX_SHARE = 0.10   # a joint with big gaps in over 10% of rows = not following orders
```
- `check_lengths(eps, fps)`: #3. Median length, limits at 0.5× and 2×, lists any too-short / too-long try numbers. FAIL if any.
- `check_action_state(df, names)`: #6. Gap per joint on every row. FAIL if a joint's mean gap is over 15 **or** it has gaps over 20 in more than 10% of rows. If a dataset has no action/state to compare, it shows **SKIP** and isn't counted.

Typed `exit()` to leave Python, then ran it on both datasets:
```bash
python audit_checks_v1.py lerobot/svla_so101_pickplace
python audit_checks_v1.py MaxT90/so101-pick-place
```

### Result 1: lerobot/svla_so101_pickplace
```text
PASS   #1-2 Episodes       all 50 tries present (0-49), none empty, shortest 183 frames
PASS   #3   Lengths        no odd tries; normal 230.5 frames (7.7 s), range 183-306, limits 115-461
PASS   #4   Timing         steady at 30 fps (avg step 0.03333 s, biggest 0.03333 s), 0 skipped frames
PASS   #5   Sync           2 cameras in sync (side max gap 0.000 s, up max gap 0.000 s), 0 tries over 0.5 s
SKIP   #5b  Videos         skipped (run with --videos)
PASS   #6   Action/state   robot follows orders; mean gap 1.7-4.1, gaps >20 in at most 2.9% of rows (shoulder_lift)
PASS   #7   Actions        no dead joints in any try; clipping under 1% (highest: elbow_flex 0.7%)
PASS   #7   Empty tries    0 empty tries; least-moving try 24 = 77% of typical (median 860)
REVIEW #9   Endings (hint) watch 1 try, unusual end pose: try 49: shoulder_lift -79.0 (usual -98.6), wrist_flex 61.3 (usual 73.8)
OVERALL: PASS (8/8 automated checks did not fail: 7 PASS, 1 REVIEW)
Not automated yet: #8 camera clear, #10 label correct (manual review);
```
The new #3 and #6 lines match my by-hand numbers exactly. **8 automated checks, no fails.** The only manual items left are **#8 camera clear** and **#10 label correct**.

### Result 2: MaxT90/so101-pick-place (the surprise)
```text
PASS   #1-2 Episodes       all 50 tries present (0-49), none empty, shortest 346 frames
FAIL   #3   Lengths        1 too long [0]; normal 438 frames (14.6 s), range 346-948, limits 219-876
PASS   #4   Timing         steady at 30 fps (avg step 0.03333 s, biggest 0.03333 s), 0 skipped frames
PASS   #5   Sync           2 cameras in sync (wrist max gap 0.000 s, overhead max gap 0.000 s), 0 tries over 0.5 s
SKIP   #5b  Videos         skipped (run with --videos)
PASS   #6   Action/state   robot follows orders; mean gap 0.9-3.1, gaps >20 in at most 0.6% of rows (shoulder_lift)
PASS   #7   Actions        no dead joints in any try; clipping under 1% (highest: wrist_flex 0.2%); note: shoulder_lift, wrist_flex, wrist_roll go past +/-100 (scale not capped at 100)
PASS   #7   Empty tries    0 empty tries; least-moving try 24 = 88% of typical (median 1084)
REVIEW #9   Endings (hint) watch 1 try, unusual end pose: try 45: gripper 14.5 (usual 0.8)
OVERALL: FAIL (7/8 automated checks did not fail: 6 PASS, 1 REVIEW)
```
The new #3 check caught something we **missed on Day 14**: a normal MaxT90 try is 438 frames (≈ 14.6 s), but **try 0 is 948 frames (≈ 31.6 s)**, more than double, past the 876 limit. Like a pizza that should take 15 minutes showing up after 32.

The code can't say **why** it's long. It only points at it. Maybe the robot dropped the brick and retried, got stuck, or the person was slow to press stop on the first try of the day. That's where the human comes in.

## Step 8: Investigate MaxT90 try 0, two ways
### Way 1: watch the video
Opened [MaxT90 episode 0](https://huggingface.co/spaces/lerobot/visualize_dataset?path=%2FMaxT90%2Fso101-pick-place%2Fepisode_0) in the viewer. What I saw:
> "the robot was stuck until 16.3 second and then trying to grapped the object , it took 31 second ."

### Way 2: prove it with the data
Per-second movement of the arm in try 0. Back in Python (`import pandas as pd` and `import numpy as np` first):
```python
df = pd.read_parquet("hf://datasets/MaxT90/so101-pick-place/data/chunk-000/file-000.parquet")
e = df[df["episode_index"] == 0]
mv = np.abs(np.diff(np.stack(e["observation.state"]), axis=0)).sum(axis=1)
print(pd.Series(mv).groupby(e["timestamp"].values[1:].astype(int)).sum().round(0))
```
What each line does:
1. `df = pd.read_parquet(...)`: load the MaxT90 robot data (may take a minute).
2. `e = df[df["episode_index"] == 0]`: keep only try 0.
3. `np.diff(...)`: how much each joint moved between each pair of pictures; `np.abs` makes it a distance; `.sum(axis=1)` adds up all 6 joints. (Day 12's "step counter", picture by picture.)
4. `.groupby(timestamp.astype(int)).sum()`: add those up **per second** (`astype(int)` chops 16.7 s down to second 16). `values[1:]` because `diff` gives one fewer value than there are pictures.

My output (left = second, right = how much the arm moved in that second; 0 = frozen):
```text
0       0.0
1       0.0
2       0.0
3       0.0
4       0.0
5       0.0
6       0.0
7       0.0
8       0.0
9       0.0
10      0.0
11      0.0
12      0.0
13      0.0
14      0.0
15      0.0
16      7.0
17     53.0
18    108.0
19    118.0
20     71.0
21     44.0
22     48.0
23     93.0
24     80.0
25     18.0
26     19.0
27    123.0
28    198.0
29     62.0
30     11.0
31      0.0
```
- **0 to 15 s:** 0.0. The arm doesn't move at all.
- **16 s:** it starts (7).
- **19 to 22 s:** the gripper opens and closes = **the grab**.
- **26 to 27 s:** it opens again = **the release** into the box.
- **31 s:** 0 again. Task done.

The actual task took about **15 s**, which is normal for this dataset (typical 14.6 s). The extra length is **16 seconds of the robot sitting still at the start**, probably because the recording started before the operator began.

**Verdict: not broken, a dead start.** Proved two ways: my eyes (video) and the numbers (data) agree.

### My coverage note
Example given:
> "Try 0 FAILED the length check (31.6 s vs a normal 14.6 s). I watched it: the robot sits still for 16 seconds, then does the task normally. Not broken, just a dead start. Fix: trim the first 16 seconds or remove the try."

My version:
> "i went back to check try 0 why it failed , i watched the video , it stopped until 16.3 second and then do the task normally not broken ,just a dead start and fix : trim the first 16 seconds or remove the try,"

Solid coverage note ✅. Why the fix matters: a robot trained on this try might learn to "**wait for nothing**" for 16 seconds. No need to re-record; trim or drop it.

## Step 9: What will a team think of a FAIL?
My question: "i have question if i send this failed csv what team will think"

- A good team **won't be upset**. They'll be glad you found it **before** they spent time training on it.
- **Don't** send a bare "FAIL". It sounds scary and gives them nothing to do.
- **Do** send **the finding, the proof and the fix together**: "1 of 50 tries has a 16-second dead start. Not broken. Trim it or remove it. The other 49 pass."
- **49 / 50 = 98% clean**, well above the **85/15 rule** (Day 6), so the dataset is usable after one small fix.

## Open item
- **MaxT90 #9 REVIEW, try 45:** ends with gripper 14.5 (usual 0.8), so the gripper is a bit open at the end. **Not watched yet.** Watch it before signing off on MaxT90.

## Key ideas
- **One command, one report.** The whole checklist in one run is a product; separate scripts are a hobby.
- **Build by hand first, then automate.** The tool's #3 and #6 lines matched my by-hand numbers exactly.
- **Median, not average**, for "normal": one weird try can't drag it.
- **Timestamp ≠ timing ≠ length**: raw clock / gap between pictures / total size of a try.
- **Action vs state:** small average gaps + rare big gaps = the arm catching up to its order (dog and ball). A broken motor = big gaps most of the time.
- **A FAIL from the code means "go look."** It's not the final verdict. Prove it two ways (video + data), then decide.
- **Report finding + proof + fix**, never a bare FAIL.

## Checklist progress
- #1, #2 Episodes; **#3 Lengths (new today)**; #4 Timing; #5 Sync; #5b Videos (with `--videos`); **#6 Action/state (new today)**; #7 Robot moves: ✅ automated (**8 automated checks**)
- #9 Task finished: 🟡 partly automated (REVIEW hint) + watching
- #8 Camera clear, #10 Label correct: manual review
- Tool: [audit_checks_v1.py](audit_checks_v1.py) (512 lines). svla_so101_pickplace = PASS 8/8; MaxT90/so101-pick-place = FAIL on #3 (try 0 dead start, explained) + REVIEW try 45 (open)

## Next: Day 21
Week 3 review: break it on purpose. Think of 3 ways a dataset could fool the script, then try one: duplicate an episode's parquet rows and see if the tool notices (it should flag identical episodes). Document the result as an "adversarial test", so when a team asks "what can't it catch?", there's an honest answer.

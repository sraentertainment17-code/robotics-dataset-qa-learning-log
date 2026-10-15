# Day 6: What "usable" means: the 85/15 rule ✅ (Oct 8, 2026)

## Goal
An audit needs a pass/fail bar. Today: learn what "usable" means (the 85/15 rule) and write QA Checklist v1, 8–10 checks, one sentence each. No code today: this is thinking and writing.

## The 85/15 rule
- **Pass:** more than **85%** of the tries are usable.
- **Fail (re-record):** **15% or more** of the tries are bad.

**Analogy: a teacher grading 100 homework sheets.** 90 good and 10 bad = the class passes. 20 bad = too many need redoing, so the batch goes back.

**For our dataset (50 tries):** 15% of 50 = 7.5, so:

| Bad tries | Bad % | Verdict |
|---|---|---|
| 0–7 | 0–14% | ✅ Pass |
| 8 or more | 16%+ | ❌ Fail: re-record |

## What makes a try unusable (from the plan)
1. **Robot never moves:** the arm just sits there, so there's nothing to learn.
2. **Wrong object:** it grabs something other than what the task says.
3. **Camera blocked:** a hand, arm or object covers the view.
4. **Cut off mid-task:** the recording stops before the job is done.
5. **Wrong label:** the task text doesn't match what really happens.

## Where is the checklist?
I asked: "Where can I find the checklist?" Answer: **you write it yourself.** That's the product: your own list of rules. The coach gave me a fill-in starter to begin from.

## My first attempt (and what I learned)
What I wrote:
> "Episode is 50 tries which means 50 videos, robot type is so100, 30 fps, frames 11939. It is 8 seconds per try. The gap is very narrow, 0.1, because the video and data show the actual same matches. Action starts from 0 to observation_state which robot joints are moving, and cameras are also clear during the task. Task was finished smoothly and labeled correctly. The time is also on point."

Coaching points:
1. **That's a report, not a checklist.** A **checklist** = the rules you'd use on **any** dataset. A **report** = the results for **one** dataset.
   - Analogy: **car inspection.** The checklist says "check brakes, check lights, check tires." The report says "this car: brakes OK, left light broken." You write the checklist once and use it on every car.
2. **Only claim what you actually checked.** I said the cameras were clear, the task was finished and the label was correct, but I haven't checked those yet (they come in Weeks 2–3). A team trusts the report only if every claim was tested.
3. **Correction: action doesn't "start from 0."** `action` = the **order** (where the joints are told to go). `observation.state` = where the joints **actually** were. (Day 3.)

## QA Checklist v1 (final, approved)
1. **Episode count:** the number of tries on disk matches the count in info.json.
2. **Frame count:** total frames match info.json, and no try has 0 frames.
3. **Odd lengths:** flag any try that's much shorter or longer than the others.
4. **Timing:** timestamps step evenly at 1 ÷ fps, with no jumps.
5. **Video vs. data:** each try's video length matches its data length within 0.1 seconds.
6. **Action vs. state:** the order and the actual joint positions stay close, with no big gaps.
7. **Robot moves:** every joint changes during the try, so none are stuck or frozen.
8. **Camera clear:** both cameras show the robot and the object, with nothing blocking them.
9. **Task finished:** each try ends with the task done, not cut off halfway.
10. **Label correct:** the task text matches what really happens in the video.

**Pass rule:** more than 85% of tries pass every check (for 50 tries, at most 7 bad).

My reaction: "It is very clean for me." ✅
Shareable version: [qa_checklist_v1.md](qa_checklist_v1.md)

## What I've already checked by hand on svla_so101_pickplace
| Check | Status | Where |
|---|---|---|
| #1 Episode count | ✅ Done | Day 2 |
| #2 Frame count | ✅ Done | Day 2 |
| #3 Odd lengths | ✅ Done | Day 2 |
| #4 Timing | ✅ Done | Day 3 |
| #5 Video vs. data | ✅ Done (all 50, both cameras) | Day 4 |
| #6 Action vs. state | 🟡 Partly (row 0 only) | Day 3 |
| #7 Robot moves | ⏳ Not yet | Weeks 2–3 |
| #8 Camera clear | ⏳ Not yet | Weeks 2–3 |
| #9 Task finished | ⏳ Not yet | Weeks 2–3 |
| #10 Label correct | ⏳ Not yet | Weeks 2–3 |

## Key ideas
- The 85/15 rule turns "is this data good?" into a clear yes/no a team can act on.
- A checklist is written once and reused on every dataset; that's what makes it a product.
- Only report what you tested. "Not checked yet" is an honest answer; a guess is not.

## Day 6 in one sentence
A checklist is the rules I use on any dataset; a report is what I found in one dataset. A dataset passes if more than 85% of the tries pass every check.

## Next: Day 7
Week 1 review: narrate a dataset. Record a 2-minute voice note explaining svla_so101_pickplace: what it is, how it's stored, and 3 things I'd check first.

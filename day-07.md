# Day 7: Week 1 review: narrate a dataset ✅ (Oct 9, 2026)

## Goal
Week 1 review. Explain the svla_so101_pickplace dataset out loud in about 2 minutes, like talking to a stranger: **what it is, how it's stored, and 3 things I'd check first.** If I can say it simply, I understand it.

## The cheat sheet (3 parts)
**1. What it is**
- Robot: SO-101 arm (the files call it `so100_follower`)
- Task: pink lego brick into the transparent box
- 50 tries, 11,939 frames, 30 fps, about 8 seconds per try

**2. How it's stored**
- `meta/` = the **label on the box** (robot type, fps, number of tries, the task)
- `data/` = the **diary** (action, observation.state, time for every frame)
- `videos/` = the **side** and **up** cameras, one MP4 per camera

**3. Three checks**
1. Does the try count match what meta says?
2. Does each video's length match its data length?
3. Are any tries way shorter or longer than the others?

End with the 85% rule: the dataset passes if more than 85% of tries pass.

## Take 1 (word for word)
> "Yes, we use uh- the robot uh type is like S- 100 and the task we're doing is The robot Picking uh picking up the ball and put it in the baggage. We try 50 episodes and we use uh 30 FPS and we store it in data is data is like a diary. We record everything and meta is like uh- how the robot joins Movement during the during the time so and then videos, we have two main cameras on our robot one is above the uh- robot and above the robot arms and uh- one is above the above the grabber. Treatings you check. First, I check there's a- a lot of checklist first of all, I check how many episode uh that we're doing and uh another one is how many how many FPS we using and the camera quality like 6040 or 70- uh 20s like we check it that one and then we we check the frames, how many frames do we do and timestamp when we during our training, how many time-step we are doing Thank you"

### Feedback on take 1
1. **Task:** it's a **pink lego brick** into a **transparent box**, not a ball into a bag.
2. **meta and data were swapped:** joint movement over time is **data** (the diary). **meta** is the label on the box.
3. **Cameras:** they're **side** and **up**, and each picture is **640 × 480**.
4. **Facts vs checks:** episodes, fps and frames are **facts you read**. A **check** asks "**does it match?**" (e.g. does the try count on disk match what meta says?).

## Take 2 (word for word)
> "Okay, let me try it again What is uh what is it that we use the S1- S100 robot arms, and the task we're doing it. Pink logo bricks and going into the transparent box. Data is like we uh, it's like a diary and the tasks we do uh- the meta is like label on the box, uh robot type and FPS and the task we're doing and how many try we're doing, everything is and uh everything is... store in the meta Camera we're using, and one is side. Looking from the- looking from the side and one is up uh... above from the robotic arms. That's uh the picture we're using is 6040 by 4080. The checklist we're doing is how many how many uh does uh number of tries on this much meta or the other one is does each video match its data's length uh in this december, all fifty did, are any tries way shorter and longer than others We had to check the timestamp, you know uh if the If the The trains is way shorter and longer, it's gonna be big gap. So we had to check it again Thank you"

### Feedback on take 2
Much better ✅ I got the task, meta = label, data = diary, both cameras, and 3 real "does it match?" checks.

Small fixes:
- Say the picture size as **640 × 480** ("six-forty by four-eighty"), not "6040 by 4080".
- The robot is the **SO-101** (the files say `so100`).

## Improvement: take 1 vs take 2
| Part | Take 1 | Take 2 |
|---|---|---|
| Robot | "S- 100" | "S100 robot arms" (still say SO-101) |
| Task | ❌ ball into the bag | ✅ pink lego brick into the transparent box |
| data/ | 🟡 diary (but mixed with meta) | ✅ like a diary |
| meta/ | ❌ "how the robot joints move over time" (that's data) | ✅ label on the box: robot type, fps, task, number of tries |
| Cameras | 🟡 two cameras, but "above the arm" and "above the grabber" | ✅ side and up |
| Picture size | ❌ "6040 or 70- 20s" | 🟡 "6040 by 4080" (should be 640 × 480) |
| Checks | ❌ listed facts (how many episodes, fps, frames) | ✅ 3 real match checks: try count vs meta, video vs data length (all 50 matched), odd-length tries |

## Key ideas
- **Facts vs checks:** a fact is something you read ("50 tries"). A check compares two things ("does disk say 50 like meta does?").
- **meta = label on the box, data = diary, videos = the cameras.** Getting these straight is the base for everything in Week 2.
- Saying it out loud shows the gaps fast: take 1 found 4 mix-ups that reading alone didn't.

## 🎉 Week 1 complete
In 7 days I installed LeRobot, learned the meta/, data/ and videos/ folders, loaded the dataset in Python, ran my first full-dataset check (video vs data, all 50 pass), wrote [QA Checklist v1](qa_checklist_v1.md), and explained it all out loud.

## Next: Day 8
Episode counts and integrity. Write a Python script that checks the try numbers run 0 to 49 with no gaps and that every try has more than 0 frames.

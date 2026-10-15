# Day 27: The 5-minute dataset scan

## Goal
Learn a fast, repeatable first look at any public LeRobot dataset, so you can spot the most likely problem in about five minutes before running the full audit tool.

## Analogy: a doctor's quick checkup
A doctor checks the same few things in the same order every time. If something looks wrong, they stop and look closer. If everything looks fine, they move on to the big tests.

## The scan, in order
1. **Dataset name.** The name hints at the task you should expect (for example "stacking" or "pick and place").
2. **`meta/info.json`.** Do the math:
   - frames ÷ episodes ÷ fps = seconds per try (does it look reasonable?)
   - number of videos ÷ episodes = number of cameras
   - read `total_tasks`
3. **`meta/tasks.jsonl`.** Do the task names match the dataset name? Does the number of tasks match `total_tasks`?
4. **`meta/episodes.jsonl`.** Find the shortest and longest `length`. A try under half of the typical length, or over double, is a red flag (see Day 20).
5. **File list.** Names like "merged" or "cont" can mean copies of the same recording (possible duplicates).

Stop at the first real red flag and look at it closely. If everything is clean, run `audit_checks_v1.py`.

## Why each check?
Look where a problem is likely, like a mechanic listening to the engine where it makes noise:
- Counting task names finds labels that disagree with `info.json`. Wrong task labels can make a model mix jobs up.
- Checking lengths is the fastest way to find cut-off or copied tries.
- Reading the task lines shows when a second task is hiding inside a dataset.

## Key ideas
- Only report a problem you have seen with your own eyes (open the file, watch the video).
- A clean result is still a result.
- Doing the scan in the same order every time saves time.

## Next: Day 28
Business day (not published).

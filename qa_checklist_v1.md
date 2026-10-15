# Robot Dataset QA Checklist v1

A pass/fail checklist for robot demonstration datasets (LeRobot format). Each check is run on every try (episode).

| # | Check | What passes |
|---|---|---|
| 1 | Episode count | The number of tries on disk matches the count in info.json. |
| 2 | Frame count | Total frames match info.json, and no try has 0 frames. |
| 3 | Odd lengths | No try is much shorter or longer than the others (outliers are flagged). |
| 4 | Timing | Timestamps step evenly at 1 ÷ fps, with no jumps. |
| 5 | Video vs. data | Each try's video length matches its data length within 0.1 seconds. |
| 6 | Action vs. state | The commanded and actual joint positions stay close, with no big gaps. |
| 7 | Robot moves | Every joint changes during the try, so none are stuck or frozen. |
| 8 | Camera clear | Every camera shows the robot and the object, with nothing blocking the view. |
| 9 | Task finished | Each try ends with the task done, not cut off halfway. |
| 10 | Label correct | The task text matches what really happens in the video. |

## Pass rule (85/15)
- **Pass:** more than 85% of tries pass every check.
- **Re-record:** 15% or more of tries fail any check.
- Example: for 50 tries, at most 7 bad tries is a pass; 8 or more is a fail.

## What counts as unusable
Robot never moves · wrong object · camera blocked · cut off mid-task · wrong label.

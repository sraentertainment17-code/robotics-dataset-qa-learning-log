# Robotics Dataset QA: 30-day learning log

A beginner's 30-day log of learning how to check the quality of robot training data. I worked with robot datasets in the [LeRobot](https://github.com/huggingface/lerobot) format on the Hugging Face Hub, using Python. Each day note explains what I learned in simple words, the commands I used and why, the mistakes I made and how I fixed them.

Contact: SRA Robotics, founder@sra-robotics.com

## Progress
| Day | Topic | Date |
|---|---|---|
| 1 | [Install LeRobot + tour a real SO-101 dataset](day-01.md) | Oct 8, 2026 |
| 2 | [Dataset anatomy: meta/](day-02.md) | Oct 8, 2026 |
| 3 | [Dataset anatomy: data/ (parquet)](day-03.md) | Oct 8, 2026 |
| 4 | [Dataset anatomy: videos/](day-04.md) | Oct 8, 2026 |
| 5 | [Load a dataset in Python with LeRobot](day-05.md) | Oct 8, 2026 |
| 6 | [What "usable" means: the 85/15 rule](day-06.md) | Oct 8, 2026 |
| 7 | [Week 1 review: narrate a dataset](day-07.md) | Oct 9, 2026 |
| 8 | [Episode counts and integrity](day-08.md) | Oct 9, 2026 |
| 9 | [Frame rates and timestamps](day-09.md) | Oct 9, 2026 |
| 10 | [Action distributions](day-10.md) | Oct 9, 2026 |
| 11 | [Label quality](day-11.md) | Oct 9, 2026 |
| 12 | [Empty and junk episodes](day-12.md) | Oct 9, 2026 |
| 13 | [Script review and cleanup](day-13.md) | Oct 9, 2026 |
| 14 | [Week 2 review: run it on a second dataset](day-14.md) | Oct 9, 2026 |
| 15 | [Camera-robot sync](day-15.md) | Oct 9, 2026 |
| 16 | [Corrupted videos](day-16.md) | Oct 10, 2026 |
| 17 | [Truncated episodes](day-17.md) | Oct 10, 2026 |
| 18 | [Calibration gaps](day-18.md) | Oct 10, 2026 |
| 19 | [Edge-case coverage](day-19.md) | Oct 10, 2026 |
| 20 | [Assemble the full audit script](day-20.md) | Oct 10, 2026 |
| 21 | [Week 3 review: break it on purpose](day-21.md) | Oct 10, 2026 |
| 22 | [The audit report format](day-22.md) | Oct 10, 2026 |
| 23 | [Portfolio audit, part 1: run it](day-23.md) | Oct 10, 2026 |
| 24 | [Portfolio audit, part 2: write it up](day-24.md) | Oct 11, 2026 |
| 25 | [Business day (not published)](day-25.md) | Oct 13, 2026 |
| 26 | [Business day (not published)](day-26.md) | Oct 13, 2026 |
| 27 | [The 5-minute dataset scan](day-27.md) | Oct 14, 2026 |
| 28 | [Business day (not published)](day-28.md) | Oct 14, 2026 |
| 29 | [Business day (not published)](day-29.md) | Oct 14, 2026 |
| 30 | [Next steps for learning](day-30.md) |  |

Days marked "Business day (not published)" were not about dataset checking, so they are not included here.

## What the audit checks do (in plain words)
A robot dataset is like a robot's home videos of practicing one job many times. `videos/` holds the movies, `data/` holds the robot's diary (joint positions every moment), and `meta/` is the label on the box. The checks ask whether the label tells the truth and whether the movies and diary match.

1. **Episodes present (#1-2):** are all the tries there, numbered with no gaps, and none empty?
2. **Duplicates (#1c):** is any try an exact copy of another?
3. **Lengths (#3):** is any try much shorter or longer than the typical one (under half or over double)? This can mean a cut-off recording or a long dead start.
4. **Timing (#4):** do frames arrive at a steady beat (for example every 1/30 s), with no skipped frames?
5. **Sync (#5):** do the video length and the data length agree?
6. **Videos readable (#5b):** can every video frame be decoded?
7. **Action vs state (#6):** does the robot's actual position follow the commanded position closely?
8. **Actions (#7):** do all joints move, and are values stuck at the limit only rarely?
9. **Empty tries (#7):** does every try contain real movement?
10. **Endings (#9, a hint only):** does a try end in an unusual pose?

Two checks need a human: **#8 camera clear** (can you see the robot and the object?) and **#10 label correct** (does the video match the task text?). The tool only gives hints; a person has to watch the videos.

## Files
- Day notes: `day-01.md` to `day-30.md`
- [audit_checks_v1.py](audit_checks_v1.py): runs the automated checks and prints a one-page PASS/FAIL summary. Usage: `python audit_checks_v1.py [repo_id] [--videos]` (default `lerobot/svla_so101_pickplace`). `--videos` also decodes every MP4 (slower).
- Single-check scripts from Days 8-12: [check_episodes.py](check_episodes.py), [check_timing.py](check_timing.py), [check_actions.py](check_actions.py), [check_empty.py](check_empty.py)
- [qa_checklist_v1.md](qa_checklist_v1.md), [calibration_checklist_v1.md](calibration_checklist_v1.md), [coverage_rubric_v1.md](coverage_rubric_v1.md)
- [raw/maxt90_audit_raw.txt](raw/maxt90_audit_raw.txt): raw tool output on a public dataset
- `images/`: frames from public datasets used in some days

## Datasets used
Public datasets only: `lerobot/svla_so101_pickplace`, `lerobot/svla_so100_pickplace`, `MaxT90/so101-pick-place`.

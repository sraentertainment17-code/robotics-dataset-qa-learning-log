# Calibration Presence Checklist v1

Calibration is the robot's **settings sheet**: where each joint's zero is, how far it can move, and what the numbers mean. Without it, nobody can check or reproduce the measurements in a dataset.

Use these 5 questions on any LeRobot dataset. Each one is a yes/no.

| # | Check | Passes if the dataset tells you... |
|---|---|---|
| 1 | Zero position | Where **0** is for each joint (the reference pose the numbers are measured from). |
| 2 | Joint limits | The lowest and highest value each joint can physically reach. |
| 3 | Scale and units | What the numbers mean: e.g. a -100 to 100 percentage-style scale, or degrees. |
| 4 | Camera details | The name of each camera, where it's mounted, and its picture size (width × height). |
| 5 | Calibration file included | The robot's calibration file is uploaded with the dataset, so anyone can check it. |

**Where to look:** the dataset's file list (is there a calibration file?), `meta/info.json` (features: names, shapes, camera info), and the dataset README.

## Scores (Oct 10, 2026)

| # | Check | lerobot/svla_so101_pickplace | MaxT90/so101-pick-place |
|---|---|---|---|
| 1 | Zero position | ❌ not given | ❌ not given |
| 2 | Joint limits | ❌ not given | ❌ not given |
| 3 | Scale and units | ❌ not given (names only, e.g. `shoulder_pan.pos`) | ❌ not given (joints go past ±100 with no explanation; see Day 14) |
| 4 | Camera details | ✅ side + up, 640 × 480 (info.json) | ✅ wrist + overhead, 640 × 480 (info.json) |
| 5 | Calibration file included | ❌ no file | ❌ no file |
| | **Score** | **1 / 5** | **1 / 5** |

Files in both datasets: `.gitattributes`, `README.md`, `meta/episodes/chunk-000/file-000.parquet`, `meta/info.json`, `meta/stats.json`, `meta/tasks.parquet` (plus `data/` and `videos/`). None of them hold calibration settings: `info.json` gives names and shapes, `stats.json` gives results (min, max, mean of the recorded data), not settings.

Note on #4: camera mounting is only implied by the camera names (e.g. "side", "overhead"); no exact position is given.

## Recommendation for teams
LeRobot saves the calibration file on the **recording computer** (in a hidden settings folder), not in the dataset folder, so it's usually left behind when the dataset is uploaded. **Upload the calibration file with every dataset.** It turns "these numbers look odd" into "these numbers are explained".

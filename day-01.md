# Day 1: Install LeRobot + tour a real dataset ✅ (Oct 8, 2026)

## Big picture
A robot dataset is like a robot's home videos of practicing one job many times.
- **videos/**: the movies, what the cameras saw on every try.
- **data/**: the robot's diary, where each joint was and what move it made next, every moment.
- **meta/**: the label on the box, what robot, how many tries, fps, and the job.

My job as an auditor: check the label tells the truth, and the movies and diary match.

## Setup on a laptop
1. Check for conda: `conda --version` → `command not found`, so install Miniforge.
2. Install Miniforge:
   ```bash
   curl -L -O "https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-$(uname)-$(uname -m).sh"
   bash Miniforge3-$(uname)-$(uname -m).sh
   ```
   Accept license, default location, initialize conda: yes. Reopen Terminal.
3. Environment + ffmpeg (handles video):
   ```bash
   conda create -y -n lerobot python=3.12
   conda activate lerobot
   conda install -y ffmpeg -c conda-forge
   ```
4. Install and test LeRobot:
   ```bash
   pip install lerobot
   python -c "import lerobot; print('ok')"
   ```
   Result: `ok`.

## Dataset tour: lerobot/svla_so101_pickplace (86 MB)
- `meta/`: `info.json` (claims), `stats.json` (min/max/avg per joint), `tasks.parquet` (job instructions), `episodes/` (one record per try).
- `data/chunk-000/file-000.parquet` (370 kB): all 50 tries in one file (LeRobot v3 format).
- `videos/observation.images.side/` and `videos/observation.images.up/`: one 45 MB MP4 each, all tries back to back.

**My answer:** meta is the task and how many tries; videos are the side and up cameras; data is the numbers behind each try.

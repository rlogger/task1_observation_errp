# ErrP Observation Task (Pygame Version)

This repository implements a simplified version of the **Error-Related Potential (ErrP) observation task**, based on the experimental structure described in the literature (e.g., Fig. 1 in standard ErrP BCI studies).  
The paradigm displays a moving cursor and a target on a horizontal axis. On each trial, the autonomous agent moves left or right toward the target, with occasional injected erroneous movements.  
This design is suitable for collecting behavioral logs or synchronizing with EEG data for offline ErrP analysis.

---

## Features

- Cursor and target presented across **20 fixed horizontal positions**
- Automatic correct vs. incorrect movement behavior
- Random error injection (`ERROR_PROB`)
- Fixed trial timing (`TRIAL_DURATION`)
- Fixation cross at center
- Automatic CSV logging of:
  - Time (relative to experiment start)
  - Episode number
  - Cursor position
  - Target position
  - Error flag (0/1)
- ESC key to quit immediately
- **No PsychoPy dependency** — uses `pygame` only

---

## Environment Setup

This project runs on Python (3.8+ recommended) and requires only one dependency:

```bash
conda env create -f environment.yaml
conda activate errp_env
python errp_game.py
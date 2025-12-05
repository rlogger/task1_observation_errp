# Error-Related Potential (ErrP) Experiment

## Overview
A PsychoPy experiment to study Error-Related Potentials - brain signals when participants observe automated errors.

**Task**: Participants watch a blue cursor automatically move toward an orange target. Sometimes (20%) it moves the wrong way.

## Installation

### Option 1: Using Nix (macOS)

**Prerequisites**: macOS, Nix installed, `zsh` shell

1. Enter the Nix shell (uses `shell.nix` in this repo):
```bash
nix-shell
```

2. Create and activate a virtual environment:
```bash
python3 -m venv psychopy-venv
source psychopy-venv/bin/activate
```

3. Install PsychoPy:
```bash
pip install psychopy
```

### Option 2: Standard Python Installation

**Prerequisites**: Python 3.10 (recommended by PsychoPy)

1. Create and activate a virtual environment:
```bash
python3 -m venv psychopy-venv
source psychopy-venv/bin/activate  # macOS/Linux
# or
psychopy-venv\Scripts\activate  # Windows
```

2. Install PsychoPy:
```bash
pip install psychopy
```

**Note**: If you encounter dependency issues (e.g., `wxPython`), you may need to install platform-specific wheels. See [PsychoPy documentation](https://www.psychopy.org/download.html) for troubleshooting.

## Quick Start

```bash
source psychopy-venv/bin/activate
python task1_observation_errp.py
```

**Controls**: SPACE (continue through instructions), ESC (exit experiment)

## Experiment Design

### Trial Phases
1. **Preparation (1s)**: Gray square at center, orange target appears
2. **Movement (0.8s each)**: Blue square moves toward target, arrow shows direction
3. **Success (1s)**: Target turns yellow with "TARGET REACHED!"
4. **Inter-trial Interval (0.5s)**: Fixation cross

### Visual Elements
- **Gray square**: Starting position (waiting)
- **Blue square**: Active cursor (moving)
- **Orange target**: Destination
- **Yellow**: Success state
- **Arrow**: Movement direction indicator

### Colors (Colorblind-Friendly)
Uses blue-orange contrast, accessible for red-green colorblindness (8% of males).

## Parameters

```python
N_TRIALS = 30              # Number of trials
ERROR_PROB = 0.2           # 20% error rate
MOVEMENT_DURATION = 0.8    # Seconds per movement
PREP_DURATION = 1.0        # Preparation phase duration
SUCCESS_DURATION = 1.0     # Success feedback duration
ITI_DURATION = 0.5         # Inter-trial interval
```

## Data Output

**Location**: `data/logs/errp_log.csv`

**Columns**: 
- `time`: Global timestamp
- `trial`: Trial number
- `movement`: Movement number within trial
- `cursor_idx`: Current cursor position index
- `target_idx`: Target position index
- `prev_cursor_idx`: Previous cursor position
- `is_error`: 1 if error movement, 0 if correct
- `movement_direction`: "left" or "right"

## Customization

### Change error rate:
```python
ERROR_PROB = 0.3  # 30% errors
```

### Add breaks:
```python
if trial_num > 0 and trial_num % 10 == 0:
    break_text = visual.TextStim(win, text="Take a break\n\nPress SPACE to continue", height=0.08)
    break_text.draw()
    win.flip()
    event.waitKeys(keyList=["space"])
```

### Add EEG triggers:
```python
# Before movement
send_trigger(100)  # Movement start
if is_error:
    send_trigger(201)  # Error movement
else:
    send_trigger(200)  # Correct movement
```

## Analysis

### ERP Analysis
- Epoch: -200 to +800 ms around movement onset
- Look for error negativity (50-150ms) and error positivity (200-400ms)
- Compare error vs. correct movement trials

### Behavioral Analysis
- Error rate verification (~20%)
- Trial duration and movement patterns
- Movement counts per trial

## References

- Ferrez & Millán (2008). Error-related EEG potentials generated during simulated brain-computer interaction. *IEEE Trans Biomed Eng, 55*(3), 923-929.
- Chavarriaga & Millán (2010). Learning from EEG error-related potentials in noninvasive brain-computer interfaces. *IEEE Trans Neural Syst Rehabil Eng, 18*(4), 381-388.

## License

MIT License


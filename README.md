# Error-Related Potential (ErrP) Experiment

## Overview
A PsychoPy experiment to study Error-Related Potentials - brain signals when participants observe automated errors.

**Task**: Participants watch a blue cursor automatically move toward an orange target. Sometimes (20%) it moves the wrong way.

## Quick Start

```bash
pip install psychopy
python errp_task.py
```

**Controls**: SPACE (continue), ESC (exit)

## Experiment Design

### Trial Phases
1. **Prep (1s)**: Gray square at center, orange target appears
2. **Movement (0.8s each)**: Blue square moves toward target, arrow shows direction
3. **Success (1s)**: Target turns yellow with "TARGET REACHED!"
4. **ITI (0.5s)**: Fixation cross

### Visual Elements
- **Gray square**: Starting position
- **Blue square**: Active cursor
- **Orange target**: Destination
- **Yellow**: Success
- **Arrow**: Movement direction

### Colors (Colorblind-Friendly)
Uses blue-orange contrast, accessible for red-green colorblindness (8% of males).

## Parameters

```python
N_TRIALS = 30              # Number of trials
ERROR_PROB = 0.2           # 20% error rate
MOVEMENT_DURATION = 0.8    # Seconds per movement
```

## Data Output

**Location**: `data/logs/errp_log.csv`

**Columns**: time, trial, movement, cursor_idx, target_idx, prev_cursor_idx, is_error, movement_direction

## Customization

### Change error rate:
```python
ERROR_PROB = 0.3  # 30% errors
```

### Add breaks:
```python
if trial_num > 0 and trial_num % 10 == 0:
    # Show break screen
```

### Add EEG triggers:
```python
# Before movement
send_trigger(100)  # Movement start
if is_error:
    send_trigger(201)  # Error
else:
    send_trigger(200)  # Correct
```

## Analysis

**ERP Analysis**:
- Epoch: -200 to +800 ms around movement
- Look for error negativity (50-150ms) and error positivity (200-400ms)

**Behavioral**:
- Error rate verification (~20%)
- Trial duration and movement patterns

## References

- Ferrez & Millán (2008). *IEEE Trans Biomed Eng, 55*(3), 923-929.
- Chavarriaga & Millán (2010). *IEEE Trans Neural Syst Rehabil Eng, 18*(4), 381-388.

## License

MIT License

---

**Version**: 1.1 | Colorblind-friendly ✓
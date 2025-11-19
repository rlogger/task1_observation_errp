create_readme = """# Error-Related Potential (ErrP) Experiment

## Overview
This is a PsychoPy-based experiment designed to study Error-Related Potentials (ErrPs) - brain signals that occur when participants observe errors in automated systems.

## Experiment Design

### Task Description
Participants passively observe a cursor (green square) automatically moving toward a target (red square). The cursor occasionally moves in the **wrong direction** (20% error rate), and participants' task is simply to **observe and detect these errors**.

### Trial Structure
Each trial consists of 4 phases:

1. **Preparation Phase (1.0s)**
   - Gray square appears at center (0, 0)
   - Red target appears at a random position
   - Displays current trial number

2. **Movement Phase (0.8s per movement)**
   - Square turns green and begins moving
   - Arrow indicates movement direction
   - 20% chance of error (movement in wrong direction)
   - Continues until cursor reaches target

3. **Success Feedback (1.0s)**
   - Target turns yellow
   - Green border appears around target
   - "TARGET REACHED!" message displays

4. **Inter-Trial Interval (0.5s)**
   - Brief pause with fixation cross
   - Screen clears before next trial

### Visual Elements

| Element | Color | Meaning |
|---------|-------|---------|
| Gray Square | #808080 | Cursor at starting position (inactive) |
| Green Square | #33CC51 | Active cursor (moving) |
| Red Square | #E64D4D | Target position |
| Yellow Square | #FFFF4D | Target reached |
| Arrow | #B3B3B3 | Movement direction indicator |
| White + | #E6E6E6 | Fixation cross |

### Parameters
```python
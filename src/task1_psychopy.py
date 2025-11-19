from psychopy import visual, core, event
import os, csv, random

# --------------------------
# Experiment parameters
# --------------------------
N_POSITIONS = 20
TRIAL_DURATION = 2.0
ERROR_PROB = 0.2
N_EPISODES = 10

# --------------------------
# Colors
# --------------------------
BG_COLOR = [0.93, 0.93, 0.93]
CURSOR_COLOR = [0.3, 0.8, 0.5]
TARGET_LEFT = [0.3, 0.45, 0.9]     # blue
TARGET_RIGHT = [0.9, 0.45, 0.45]    # red
TARGET_REACHED = [1, 1, 1]
TEXT_COLOR = [-0.2, -0.2, -0.2]

# --------------------------
# Window setup
# --------------------------
win = visual.Window(
    size=[1280, 720],
    units="norm",
    color=BG_COLOR,
    fullscr=False
)

fixation = visual.TextStim(win, text="+", height=0.1, color=TEXT_COLOR)

instruction = visual.TextStim(
    win,
    text="Welcome to the ErrP Task\n\nPress SPACE to start",
    height=0.07,
    color=TEXT_COLOR
)

# --------------------------
# Cursor & Target
# --------------------------
cursor = visual.Circle(
    win,
    radius=0.05,
    fillColor=CURSOR_COLOR,
)

target = visual.Circle(
    win,
    radius=0.05,
    fillColor=[1,1,1]
)

# --------------------------
# Minimal Clean Labels
# --------------------------
cursor_label = visual.TextStim(
    win,
    text="Cursor",
    height=0.05,
    color=TEXT_COLOR,
)

target_label = visual.TextStim(
    win,
    text="Target",
    height=0.05,
    color=TEXT_COLOR,
)


# --------------------------
# Positions array
# --------------------------
positions = [-0.8 + i * (1.6/(N_POSITIONS-1)) for i in range(N_POSITIONS)]

def new_target(i):
    offset = random.choice([-3,-2,-1,1,2,3])
    j = i + offset
    return j if 0 <= j < N_POSITIONS else N_POSITIONS // 2

def direction(a,b):
    return (b > a) - (b < a)

# --------------------------
# Logging
# --------------------------
os.makedirs("data/logs", exist_ok=True)
log_file = "data/logs/errp_log.csv"
results = []

global_clock = core.Clock()

# Instruction screen
instruction.draw()
win.flip()
event.waitKeys(keyList=["space"])

# --------------------------
# Main experiment loop
# --------------------------
for ep in range(N_EPISODES):

    # FIXED initial cursor position
    cursor_idx = N_POSITIONS // 2
    target_idx = new_target(cursor_idx)

    reached = False

    while not reached:

        if "escape" in event.getKeys():
            win.close(); core.quit()

        # direction & movement
        d = direction(cursor_idx, target_idx)
        is_error = random.random() < ERROR_PROB
        move = -d if is_error else d
        cursor_idx = max(0, min(N_POSITIONS - 1, cursor_idx + move))

        # color logic
        if cursor_idx < target_idx:
            target.fillColor = TARGET_RIGHT
        elif cursor_idx > target_idx:
            target.fillColor = TARGET_LEFT
        else:
            target.fillColor = TARGET_REACHED

        # ------------------------
        # Update positions (layered)
        # ------------------------
        cursor.pos = (positions[cursor_idx], -0.15)
        target.pos = (positions[target_idx], 0.15)

        cursor_label.pos = (positions[cursor_idx], -0.28)
        target_label.pos = (positions[target_idx], 0.28)

        # ------------------------
        # Draw the trial
        # ------------------------
        clock = core.Clock()
        while clock.getTime() < TRIAL_DURATION:
            fixation.draw()
            cursor.draw()
            target.draw()
            cursor_label.draw()
            target_label.draw()
            win.flip()

        # ------------------------
        # Logging
        # ------------------------
        results.append({
            "time": global_clock.getTime(),
            "episode": ep,
            "cursor_idx": cursor_idx,
            "target_idx": target_idx,
            "is_error": int(is_error)
        })

        if cursor_idx == target_idx:
            reached = True

    target_idx = new_target(cursor_idx)

# Save results
with open(log_file, "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=results[0].keys())
    writer.writeheader()
    writer.writerows(results)

win.close()
core.quit()
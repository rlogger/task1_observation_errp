
from psychopy import visual, core, event
import os, csv, random

# --------------------------
# Experiment parameters
# --------------------------
N_POSITIONS = 20
N_TRIALS = 30
PREP_DURATION = 1.0
MOVEMENT_DURATION = 0.8
ITI_DURATION = 0.5
SUCCESS_DURATION = 1.0
ERROR_PROB = 0.2

# --------------------------
# color
# --------------------------
BG_COLOR = [0.2, 0.2, 0.2]           # dark gray
CURSOR_COLOR = [0.2, 0.6, 0.9]       # blue
CURSOR_PREP_COLOR = [0.5, 0.5, 0.5]  # gray
TARGET_COLOR = [0.95, 0.6, 0.1]      # orange
TARGET_REACHED = [1, 0.9, 0.1]       # yellow
ARROW_COLOR = [0.7, 0.7, 0.7]        # light gray
FIXATION_COLOR = [0.9, 0.9, 0.9]     # white
SUCCESS_COLOR = [1, 0.9, 0.1]        # yellow

# --------------------------
# Window setup
# --------------------------
win = visual.Window(
    size=[1280, 720],
    units="norm",
    color=BG_COLOR,
    fullscr=False,
    allowGUI=True
)
win.mouseVisible = True

fixation = visual.TextStim(
    win, 
    text="+", 
    height=0.1, 
    color=FIXATION_COLOR,
    pos=(0, 0)
)

# --------------------------
# Instruction screens (更新颜色描述)
# --------------------------
instruction_1 = visual.TextStim(
    win,
    text=(
        "Welcome to the Error-Related Potential (ErrP) Task\n\n"
        "In this experiment, you will observe a cursor (blue square)\n"
        "automatically moving toward a target (orange square).\n\n"
        "CLICK THIS WINDOW, then press SPACE to continue"
    ),
    height=0.06,
    color=FIXATION_COLOR,
    wrapWidth=1.6
)

instruction_2 = visual.TextStim(
    win,
    text=(
        "How it works:\n\n"
        "• Each trial starts with a GRAY square at the center\n"
        "• An ORANGE target will appear somewhere on the line\n"
        "• The square will turn BLUE and move toward the target\n"
        "• An arrow will show the movement direction\n\n"
        "Press SPACE to continue"
    ),
    height=0.06,
    color=FIXATION_COLOR,
    wrapWidth=1.6
)

instruction_3 = visual.TextStim(
    win,
    text=(
        "IMPORTANT:\n\n"
        "Sometimes the cursor will move in the WRONG direction!\n"
        "This is intentional - it happens automatically.\n\n"
        "Your task is to simply OBSERVE and pay attention\n"
        "to when the cursor makes these errors.\n\n"
        "Press SPACE to continue"
    ),
    height=0.06,
    color=FIXATION_COLOR,
    wrapWidth=1.6
)

instruction_4_text = visual.TextStim(
    win,
    text="Visual Guide:",
    height=0.07,
    color=FIXATION_COLOR,
    pos=(0, 0.35)
)

# Example visuals with new colors
example_gray = visual.Rect(win, width=0.06, height=0.06, fillColor=CURSOR_PREP_COLOR, pos=(-0.5, 0.15))
example_gray_label = visual.TextStim(win, text="Starting position\n(waiting)", height=0.05, color=FIXATION_COLOR, pos=(-0.5, -0.05))

example_blue = visual.Rect(win, width=0.06, height=0.06, fillColor=CURSOR_COLOR, pos=(0, 0.15))
example_blue_label = visual.TextStim(win, text="Active cursor\n(moving)", height=0.05, color=FIXATION_COLOR, pos=(0, -0.05))

example_orange = visual.Rect(win, width=0.06, height=0.06, fillColor=TARGET_COLOR, pos=(0.5, 0.15))
example_orange_label = visual.TextStim(win, text="Target\n(destination)", height=0.05, color=FIXATION_COLOR, pos=(0.5, -0.05))

instruction_4_bottom = visual.TextStim(
    win,
    text="Press SPACE to start the experiment",
    height=0.06,
    color=SUCCESS_COLOR,
    pos=(0, -0.35)
)

trial_counter = visual.TextStim(
    win,
    text="",
    height=0.06,
    color=FIXATION_COLOR,
    pos=(0, -0.4)
)

success_text = visual.TextStim(
    win,
    text="TARGET REACHED!",  
    height=0.1,
    color=SUCCESS_COLOR,
    pos=(0, 0.3),
    bold=True
)

# --------------------------
# Cursor & Target
# --------------------------
cursor = visual.Rect(
    win,
    width=0.08,
    height=0.08,
    fillColor=CURSOR_COLOR,
    lineColor=None
)

target = visual.Rect(
    win,
    width=0.08,
    height=0.08,
    fillColor=TARGET_COLOR,
    lineColor=None
)

# success highlight
success_highlight = visual.Rect(
    win,
    width=0.14,  
    height=0.14,
    fillColor=None,
    lineColor=SUCCESS_COLOR,
    lineWidth=6,  
    opacity=1.0  
)

# --------------------------
# Arrow
# --------------------------
def create_arrow_vertices(length=0.10, head_width=0.04):
    vertices = [
        [-length/2, -0.015],
        [length/2 - head_width, -0.015],
        [length/2 - head_width, -head_width/2],
        [length/2, 0],
        [length/2 - head_width, head_width/2],
        [length/2 - head_width, 0.015],
        [-length/2, 0.015],
    ]
    return vertices

arrow = visual.ShapeStim(
    win,
    vertices=create_arrow_vertices(),
    fillColor=ARROW_COLOR,
    lineColor=None,
    opacity=0.5
)

# --------------------------
# Reference line
# --------------------------
reference_line = visual.Line(
    win,
    start=(-0.85, 0),
    end=(0.85, 0),
    lineColor=[0.4, 0.4, 0.4],
    lineWidth=1,
    opacity=0.3
)

# --------------------------
# Positions array
# --------------------------
positions = [-0.8 + i * (1.6/(N_POSITIONS-1)) for i in range(N_POSITIONS)]
START_POSITION = min(range(len(positions)), key=lambda i: abs(positions[i]))

def new_target(cursor_pos):
    possible_positions = [i for i in range(N_POSITIONS) 
                         if abs(i - cursor_pos) >= 3]
    if possible_positions:
        return random.choice(possible_positions)
    else:
        return (cursor_pos + 5) % N_POSITIONS

def direction(a, b):
    return (b > a) - (b < a)

# --------------------------
# Logging
# --------------------------
os.makedirs("data/logs", exist_ok=True)
log_file = "data/logs/errp_log.csv"
results = []
global_clock = core.Clock()

# --------------------------
# Show instruction screens
# --------------------------
instruction_1.draw()
win.flip()
event.waitKeys(keyList=["space"])

instruction_2.draw()
win.flip()
event.waitKeys(keyList=["space"])

instruction_3.draw()
win.flip()
event.waitKeys(keyList=["space"])

instruction_4_text.draw()
example_gray.draw()
example_gray_label.draw()
example_blue.draw()
example_blue_label.draw()
example_orange.draw()
example_orange_label.draw()
instruction_4_bottom.draw()
win.flip()
event.waitKeys(keyList=["space"])

# --------------------------
# Main experiment loop
# --------------------------
for trial_num in range(N_TRIALS):
    
    keys = event.getKeys(['escape'])
    if 'escape' in keys:
        win.close()
        core.quit()
    
    # ------------------------
    # PHASE 1: PREPARATION
    # ------------------------
    cursor_idx = START_POSITION
    target_idx = new_target(cursor_idx)
    
    cursor.fillColor = CURSOR_PREP_COLOR
    cursor.pos = (positions[cursor_idx], 0)
    target.pos = (positions[target_idx], 0)
    target.fillColor = TARGET_COLOR
    
    trial_counter.text = f"Trial {trial_num + 1} / {N_TRIALS}"
    
    clock = core.Clock()
    while clock.getTime() < PREP_DURATION:
        reference_line.draw()
        cursor.draw()
        target.draw()
        trial_counter.draw()
        win.flip()
    
    # ------------------------
    # PHASE 2: MOVEMENT
    # ------------------------
    cursor.fillColor = CURSOR_COLOR
    movements = 0
    
    while cursor_idx != target_idx:
        movements += 1
        
        keys = event.getKeys(['escape'])
        if 'escape' in keys:
            win.close()
            core.quit()
        
        prev_cursor_idx = cursor_idx
        
        d = direction(cursor_idx, target_idx)
        is_error = random.random() < ERROR_PROB
        move = -d if is_error else d
        cursor_idx = max(0, min(N_POSITIONS - 1, cursor_idx + move))
        
        cursor.pos = (positions[cursor_idx], 0)
        target.pos = (positions[target_idx], 0)
        
        arrow_x = positions[cursor_idx]
        arrow.pos = (arrow_x, -0.15)
        if cursor_idx > prev_cursor_idx:
            arrow.ori = 0
        elif cursor_idx < prev_cursor_idx:
            arrow.ori = 180
        
        clock = core.Clock()
        while clock.getTime() < MOVEMENT_DURATION:
            if cursor_idx != START_POSITION:
                fixation.draw()
            reference_line.draw()
            arrow.draw()
            target.draw()
            cursor.draw()
            trial_counter.draw()
            win.flip()
        
        results.append({
            "time": global_clock.getTime(),
            "trial": trial_num,
            "movement": movements,
            "cursor_idx": cursor_idx,
            "target_idx": target_idx,
            "prev_cursor_idx": prev_cursor_idx,
            "is_error": int(is_error),
            "movement_direction": "right" if cursor_idx > prev_cursor_idx else "left"
        })
    
    # ------------------------
    # PHASE 3: SUCCESS 
    # ------------------------
    target.fillColor = TARGET_REACHED  
    success_highlight.pos = target.pos
    
    clock = core.Clock()
    while clock.getTime() < SUCCESS_DURATION:
        reference_line.draw()
        success_highlight.draw()  
        target.draw()  
        cursor.draw()  
        success_text.draw()  
        trial_counter.draw()
        win.flip()
    
    # ------------------------
    # PHASE 4: ITI
    # ------------------------
    clock = core.Clock()
    while clock.getTime() < ITI_DURATION:
        fixation.draw()
        win.flip()

# ------------------------
# End
# ------------------------
end_text = visual.TextStim(
    win,
    text="Experiment Complete!\n\nThank you for participating.",
    height=0.08,
    color=FIXATION_COLOR
)
end_text.draw()
win.flip()
core.wait(2.0)

# Save
with open(log_file, "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=results[0].keys())
    writer.writeheader()
    writer.writerows(results)

win.close()
core.quit()
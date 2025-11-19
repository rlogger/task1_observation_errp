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
# Colors
# --------------------------
BG_COLOR = [0.2, 0.2, 0.2]
CURSOR_COLOR = [0.2, 0.8, 0.3]
CURSOR_PREP_COLOR = [0.5, 0.5, 0.5]
TARGET_COLOR = [0.9, 0.3, 0.3]
TARGET_REACHED = [1, 1, 0.3]
ARROW_COLOR = [0.7, 0.7, 0.7]
FIXATION_COLOR = [0.9, 0.9, 0.9]
SUCCESS_COLOR = [0.3, 1, 0.3]

# --------------------------
# Window setup
# --------------------------
win = visual.Window(
    size=[1280, 720],
    units="norm",
    color=BG_COLOR,
    fullscr=False
)

fixation = visual.TextStim(
    win, 
    text="+", 
    height=0.1, 
    color=FIXATION_COLOR,
    pos=(0, 0)  # 中心位置
)

instruction = visual.TextStim(
    win,
    text="Welcome to the ErrP Task\n\nPress SPACE to start",
    height=0.08,
    color=FIXATION_COLOR
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
    height=0.08,
    color=SUCCESS_COLOR,
    pos=(0, 0.3)
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

success_highlight = visual.Rect(
    win,
    width=0.12,
    height=0.12,
    fillColor=None,
    lineColor=SUCCESS_COLOR,
    lineWidth=4
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
# Positions array (中心点在 (0, 0))
# --------------------------
positions = [-0.8 + i * (1.6/(N_POSITIONS-1)) for i in range(N_POSITIONS)]
# 找到最接近 0 的位置作为起始点
START_POSITION = min(range(len(positions)), key=lambda i: abs(positions[i]))

def new_target(cursor_pos):
    """Generate new target position away from cursor and center"""
    # 确保 target 不在中心附近
    possible_positions = [i for i in range(N_POSITIONS) 
                         if abs(i - cursor_pos) >= 3]  # 至少距离3个位置
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

# Instruction screen
instruction.draw()
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
    cursor_idx = START_POSITION  # 从中心开始
    target_idx = new_target(cursor_idx)
    
    cursor.fillColor = CURSOR_PREP_COLOR
    cursor.pos = (positions[cursor_idx], 0)  # 应该在 (0, 0) 附近
    target.pos = (positions[target_idx], 0)
    target.fillColor = TARGET_COLOR
    
    trial_counter.text = f"Trial {trial_num + 1} / {N_TRIALS}"
    
    # Prep phase - cursor 在中心，fixation 不显示（被 cursor 覆盖）
    clock = core.Clock()
    while clock.getTime() < PREP_DURATION:
        reference_line.draw()
        cursor.draw()  # cursor 在中心，代替 fixation
        target.draw()
        trial_counter.draw()
        win.flip()
    
    # ------------------------
    # PHASE 2: MOVEMENT
    # ------------------------
    cursor.fillColor = CURSOR_COLOR  # 变绿，开始移动
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
        
        # Arrow
        arrow_x = positions[cursor_idx]
        arrow.pos = (arrow_x, -0.15)
        if cursor_idx > prev_cursor_idx:
            arrow.ori = 0
        elif cursor_idx < prev_cursor_idx:
            arrow.ori = 180
        
        clock = core.Clock()
        while clock.getTime() < MOVEMENT_DURATION:
            # 当 cursor 离开中心后，显示 fixation
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
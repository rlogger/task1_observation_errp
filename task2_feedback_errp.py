from psychopy import visual, core, event
import pygame
import os, csv, random, math

# --------------------------
# Experiment parameters (Iwane et al. 2023)
# --------------------------
N_TRIALS = 90  # 90 trials per session (paper used 90)
ERROR_PROBABILITY = 0.30  # 30% error trials
ROTATION_ANGLES = [20, 40, 60]  # Degrees (paper used these angles)
CURSOR_SPEED = 5.0  # Normalized units per frame
MIN_DISTANCE = 0.6  # Minimum distance target must be from cursor
BOUNDARY_MIN = 0.30  # Rotation occurs between 30-60% of distance
BOUNDARY_MAX = 0.60
SUCCESS_DURATION = 1.0
ITI_DURATION = 0.5

# --------------------------
# Visual parameters
# --------------------------
BG_COLOR = [-0.8, -0.8, -0.8]  # Dark gray
CURSOR_COLOR = [0.2, 0.6, 0.9]  # Blue
TARGET_COLOR = [0.95, 0.2, 0.1]  # Red
SUCCESS_COLOR = [1, 0.9, 0.1]  # Yellow
TEXT_COLOR = [0.9, 0.9, 0.9]  # White
FIXATION_COLOR = [0.9, 0.9, 0.9]

CURSOR_RADIUS = 0.04
TARGET_SIZE = 0.08

# --------------------------
# Input method selection
# --------------------------
print("\nTask 2: Feedback ErrP Experiment")
print("=" * 50)
print("\nChoose your input method:")
print("1. Controller/Joystick")
print("2. Keyboard (Arrow keys)")
print()

while True:
    choice = input("Enter your choice (1 or 2): ").strip()
    if choice == "1":
        USE_CONTROLLER = True
        break
    elif choice == "2":
        USE_CONTROLLER = False
        break
    else:
        print("Invalid choice. Please enter 1 or 2.")

# --------------------------
# Joystick setup (if using controller)
# --------------------------
pygame.init()
joystick = None

if USE_CONTROLLER:
    pygame.joystick.init()

    if pygame.joystick.get_count() == 0:
        print("\nWARNING: No joystick detected!")
        print("Please connect a gamepad/controller and restart,")
        print("or choose keyboard controls instead.")
        input("Press Enter to exit...")
        exit()

    joystick = pygame.joystick.Joystick(0)
    joystick.init()
    print(f"\nJoystick detected: {joystick.get_name()}")
    print(f"Axes: {joystick.get_numaxes()}, Buttons: {joystick.get_numbuttons()}")
else:
    print("\nKeyboard controls selected!")
    print("Use Arrow Keys to move the cursor")
    print("Press SPACE to start trials")

# --------------------------
# Keyboard state tracking (if using keyboard)
# --------------------------
# We'll use pygame's key state for smooth continuous movement
if not USE_CONTROLLER:
    pygame.key.set_repeat(1, 1)  # Enable key repeat for smooth movement

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

# --------------------------
# Visual elements
# --------------------------
fixation = visual.TextStim(
    win,
    text="+",
    height=0.1,
    color=FIXATION_COLOR,
    pos=(0, 0)
)

cursor = visual.Circle(
    win,
    radius=CURSOR_RADIUS,
    fillColor=CURSOR_COLOR,
    lineColor=None
)

target = visual.Rect(
    win,
    width=TARGET_SIZE,
    height=TARGET_SIZE,
    fillColor=TARGET_COLOR,
    lineColor=None
)

success_text = visual.TextStim(
    win,
    text="TARGET REACHED!",
    height=0.08,
    color=SUCCESS_COLOR,
    pos=(0, 0.3),
    bold=True
)

trial_counter = visual.TextStim(
    win,
    text="",
    height=0.06,
    color=TEXT_COLOR,
    pos=(0, -0.85)
)

instruction_text = visual.TextStim(
    win,
    text="",
    height=0.06,
    color=TEXT_COLOR,
    pos=(0, 0),
    wrapWidth=1.6
)

# --------------------------
# Instruction screens
# --------------------------
def get_instructions():
    """Generate instructions based on input method."""
    if USE_CONTROLLER:
        control_desc = "the joystick"
        control_detail = "• Use the LEFT JOYSTICK to control a BLUE circle (cursor)\n"
        start_button = "Press A button"
        rotation_desc = "When you push the joystick in one direction,\nthe cursor may move in a slightly different direction."
    else:
        control_desc = "the keyboard"
        control_detail = "• Use the ARROW KEYS to control a BLUE circle (cursor)\n"
        start_button = "Press SPACE"
        rotation_desc = "When you press arrow keys in one direction,\nthe cursor may move in a slightly different direction."

    return [
        (
            "Task 2: Feedback ErrP Experiment\n"
            "Cursor Control with Visual Rotations\n\n"
            f"Welcome! In this experiment, you will ACTIVELY CONTROL\n"
            f"a cursor using {control_desc} to reach targets as quickly as possible.\n\n"
            "Unlike Task 1 where you observed, here YOU are in control.\n\n"
            f"{start_button} to continue"
        ),
        (
            "How It Works\n\n"
            f"{control_detail}"
            "• Move the cursor to reach a RED square (target)\n"
            "• Move as quickly and accurately as possible\n"
            f"• {start_button} to start each trial\n\n"
            f"{start_button} to continue"
        ),
        (
            "⚠️  Visual Rotations\n\n"
            "Sometimes (30% of trials), the cursor control will be ROTATED!\n\n"
            f"{rotation_desc}\n\n"
            "• Rotations occur UNPREDICTABLY during movement\n"
            "• Rotation magnitudes: 20°, 40°, or 60°\n"
            "• You must ADAPT QUICKLY to reach the target\n\n"
            "This is what triggers the error-related brain signals we're measuring.\n\n"
            f"{start_button} to continue"
        ),
        (
            "Visual Guide\n\n"
            "BLUE CIRCLE = Cursor (you control)\n"
            "RED SQUARE = Target (goal)\n"
            "YELLOW = Success!\n\n"
            "After trials with rotations, you'll be asked\n"
            "if you perceived the rotation.\n\n"
            "Ready to begin?\n\n"
            f"{start_button} to start experiment"
        )
    ]

def show_instructions():
    """Display all instruction screens."""
    instructions = get_instructions()
    for instr in instructions:
        instruction_text.text = instr
        instruction_text.draw()
        win.flip()

        # Wait for button press
        waiting = True
        while waiting:
            if USE_CONTROLLER:
                pygame.event.pump()
                for i in range(joystick.get_numbuttons()):
                    if joystick.get_button(i):
                        waiting = False
                        core.wait(0.3)  # Debounce
                        break
            else:
                pygame.event.pump()
                keys_pressed = pygame.key.get_pressed()
                if keys_pressed[pygame.K_SPACE]:
                    waiting = False
                    core.wait(0.3)  # Debounce

            # Check for escape in both modes
            keys = event.getKeys(['escape'])
            if 'escape' in keys:
                win.close()
                pygame.quit()
                core.quit()

def show_questionnaire():
    """Show questionnaire after error trials."""
    question = visual.TextStim(
        win,
        text="Did you perceive a rotation in the cursor control?",
        height=0.07,
        color=TEXT_COLOR,
        pos=(0, 0.3)
    )
    
    yes_btn = visual.Rect(
        win,
        width=0.3,
        height=0.15,
        fillColor=SUCCESS_COLOR,
        pos=(-0.4, -0.1)
    )
    yes_text = visual.TextStim(
        win,
        text="Yes\n(Y key)",
        height=0.06,
        color=[-0.8, -0.8, -0.8],
        pos=(-0.4, -0.1)
    )
    
    maybe_btn = visual.Rect(
        win,
        width=0.3,
        height=0.15,
        fillColor=TARGET_COLOR,
        pos=(0, -0.1)
    )
    maybe_text = visual.TextStim(
        win,
        text="Maybe\n(M key)",
        height=0.06,
        color=[0.9, 0.9, 0.9],
        pos=(0, -0.1)
    )
    
    no_btn = visual.Rect(
        win,
        width=0.3,
        height=0.15,
        fillColor=[0.3, 0.3, 0.3],
        pos=(0.4, -0.1)
    )
    no_text = visual.TextStim(
        win,
        text="No\n(N key)",
        height=0.06,
        color=[0.9, 0.9, 0.9],
        pos=(0.4, -0.1)
    )
    
    question.draw()
    yes_btn.draw()
    yes_text.draw()
    maybe_btn.draw()
    maybe_text.draw()
    no_btn.draw()
    no_text.draw()
    win.flip()
    
    # Wait for response
    waiting = True
    response = None
    while waiting:
        keys = event.getKeys(['y', 'm', 'n', 'escape'])
        if 'y' in keys:
            response = 'Yes'
            waiting = False
        elif 'm' in keys:
            response = 'Maybe'
            waiting = False
        elif 'n' in keys:
            response = 'No'
            waiting = False
        elif 'escape' in keys:
            win.close()
            pygame.quit()
            core.quit()
    
    return response

# --------------------------
# Helper functions
# --------------------------
def get_keyboard_input():
    """Get keyboard arrow key input and spacebar press."""
    pygame.event.pump()  # Process event queue

    x = 0
    y = 0
    button_pressed = False

    # Get current state of all keys
    keys = pygame.key.get_pressed()

    # Arrow keys for movement
    if keys[pygame.K_LEFT]:
        x = -1.0
    if keys[pygame.K_RIGHT]:
        x = 1.0
    if keys[pygame.K_UP]:
        y = -1.0  # Matches joystick convention (up = negative)
    if keys[pygame.K_DOWN]:
        y = 1.0  # Matches joystick convention (down = positive)

    # Check for spacebar
    if keys[pygame.K_SPACE]:
        button_pressed = True

    return x, y, button_pressed

def get_joystick_input():
    """Get joystick axis values and button press."""
    pygame.event.pump()

    # Left stick (axes 0, 1)
    x = joystick.get_axis(0)
    y = joystick.get_axis(1)

    # Apply deadzone
    if abs(x) < 0.15:
        x = 0
    if abs(y) < 0.15:
        y = 0

    # Check for button press (button 0 = A on Xbox, Cross on PS)
    button_pressed = joystick.get_button(0)

    return x, y, button_pressed

def get_input():
    """Get input from either keyboard or controller based on settings."""
    if USE_CONTROLLER:
        return get_joystick_input()
    else:
        return get_keyboard_input()

def wait_for_button():
    """Wait for button press to start trial."""
    if USE_CONTROLLER:
        instruction_text.text = "Press A button to start trial"
    else:
        instruction_text.text = "Press SPACE to start trial"
    instruction_text.pos = (0, 0)

    waiting = True
    while waiting:
        instruction_text.draw()
        win.flip()

        if USE_CONTROLLER:
            pygame.event.pump()
            if joystick.get_button(0):
                waiting = False
                core.wait(0.3)  # Debounce
        else:
            pygame.event.pump()
            keys_pressed = pygame.key.get_pressed()
            if keys_pressed[pygame.K_SPACE]:
                waiting = False
                core.wait(0.3)  # Debounce

        # Check for escape in both modes
        keys = event.getKeys(['escape'])
        if 'escape' in keys:
            return False

    return True

def apply_rotation(angle_rad, rotation_angle_deg):
    """Apply rotation to input angle."""
    rotation_rad = math.radians(rotation_angle_deg)
    return angle_rad + rotation_rad

# --------------------------
# Logging setup
# --------------------------
os.makedirs("data/logs", exist_ok=True)
log_file = "data/logs/task2_feedback_errp_log.csv"
results = []
global_clock = core.Clock()

# --------------------------
# Show instructions
# --------------------------
show_instructions()

# --------------------------
# Main experiment loop
# --------------------------
for trial_num in range(N_TRIALS):
    
    # Check for escape
    keys = event.getKeys(['escape'])
    if 'escape' in keys:
        break
    
    # Wait for button press to start trial
    if not wait_for_button():
        break
    
    # ------------------------
    # Trial setup
    # ------------------------
    is_error_trial = random.random() < ERROR_PROBABILITY
    rotation_angle = 0
    
    if is_error_trial:
        rotation_angle = random.choice(ROTATION_ANGLES)
        # Randomly choose positive or negative rotation
        rotation_angle *= random.choice([-1, 1])
    
    # Random cursor start position (left or right side)
    side = random.choice(['left', 'right'])
    if side == 'left':
        cursor_pos = [-0.7, random.uniform(-0.3, 0.3)]
        target_pos = [0.7, random.uniform(-0.3, 0.3)]
    else:
        cursor_pos = [0.7, random.uniform(-0.3, 0.3)]
        target_pos = [-0.7, random.uniform(-0.3, 0.3)]
    
    # Calculate rotation boundary
    distance = abs(target_pos[0] - cursor_pos[0])
    boundary_ratio = random.uniform(BOUNDARY_MIN, BOUNDARY_MAX)
    boundary_x = cursor_pos[0] + (target_pos[0] - cursor_pos[0]) * boundary_ratio
    
    # Set positions
    cursor.pos = cursor_pos
    target.pos = target_pos
    target.fillColor = TARGET_COLOR
    
    # Trial state
    rotation_active = False
    rotation_onset_time = None
    trial_start_time = global_clock.getTime()
    movement_start_time = None
    trajectory = []
    
    trial_counter.text = f"Trial {trial_num + 1} / {N_TRIALS}"
    
    # ------------------------
    # Movement phase
    # ------------------------
    reached_target = False
    clock = core.Clock()
    
    while not reached_target:
        # Get input (from controller or keyboard)
        joy_x, joy_y, button = get_input()
        
        # Check for escape
        keys = event.getKeys(['escape'])
        if 'escape' in keys:
            win.close()
            pygame.quit()
            core.quit()
        
        # Record movement start
        if movement_start_time is None and (abs(joy_x) > 0.1 or abs(joy_y) > 0.1):
            movement_start_time = global_clock.getTime()
        
        # Calculate input angle and magnitude
        if abs(joy_x) > 0.1 or abs(joy_y) > 0.1:
            input_angle = math.atan2(joy_y, joy_x)
            magnitude = math.sqrt(joy_x**2 + joy_y**2)
            magnitude = min(magnitude, 1.0)
            
            # Check if crossed boundary (trigger rotation)
            crossed_boundary = (cursor_pos[0] - boundary_x) * (target_pos[0] - boundary_x) > 0
            
            if is_error_trial and not rotation_active and crossed_boundary:
                rotation_active = True
                rotation_onset_time = global_clock.getTime()
            
            # Apply rotation if active
            if rotation_active:
                input_angle = apply_rotation(input_angle, rotation_angle)
            
            # Move cursor
            speed = magnitude * CURSOR_SPEED * 0.01
            cursor_pos[0] += math.cos(input_angle) * speed
            cursor_pos[1] += math.sin(input_angle) * speed
            
            # Keep cursor on screen
            cursor_pos[0] = max(-0.95, min(0.95, cursor_pos[0]))
            cursor_pos[1] = max(-0.95, min(0.95, cursor_pos[1]))
            
            cursor.pos = cursor_pos
            
            # Record trajectory
            trajectory.append({
                'time': global_clock.getTime(),
                'cursor_x': cursor_pos[0],
                'cursor_y': cursor_pos[1],
                'joystick_x': joy_x,
                'joystick_y': joy_y,
                'rotation_active': rotation_active
            })
        
        # Check if reached target
        dx = cursor_pos[0] - target_pos[0]
        dy = cursor_pos[1] - target_pos[1]
        distance_to_target = math.sqrt(dx**2 + dy**2)
        
        if distance_to_target < (TARGET_SIZE + CURSOR_RADIUS):
            reached_target = True
            trial_end_time = global_clock.getTime()
        
        # Draw
        target.draw()
        cursor.draw()
        trial_counter.draw()
        win.flip()
    
    # ------------------------
    # Success feedback
    # ------------------------
    target.fillColor = SUCCESS_COLOR
    cursor.fillColor = SUCCESS_COLOR
    
    clock = core.Clock()
    while clock.getTime() < SUCCESS_DURATION:
        target.draw()
        cursor.draw()
        success_text.draw()
        trial_counter.draw()
        win.flip()
    
    # Reset colors
    cursor.fillColor = CURSOR_COLOR
    
    # ------------------------
    # Log trial data
    # ------------------------
    trial_duration = trial_end_time - trial_start_time
    movement_duration = trial_end_time - movement_start_time if movement_start_time else 0
    
    trial_data = {
        'time': trial_start_time,
        'trial': trial_num,
        'is_error_trial': int(is_error_trial),
        'rotation_angle': rotation_angle if is_error_trial else 0,
        'rotation_onset_time': rotation_onset_time if rotation_active else None,
        'trial_duration': trial_duration,
        'movement_duration': movement_duration,
        'cursor_start_x': trajectory[0]['cursor_x'] if trajectory else cursor_pos[0],
        'cursor_start_y': trajectory[0]['cursor_y'] if trajectory else cursor_pos[1],
        'target_x': target_pos[0],
        'target_y': target_pos[1],
        'boundary_x': boundary_x,
        'perceived_rotation': None
    }
    
    # ------------------------
    # Questionnaire (error trials only)
    # ------------------------
    if is_error_trial:
        response = show_questionnaire()
        trial_data['perceived_rotation'] = response
    
    results.append(trial_data)
    
    # ------------------------
    # ITI
    # ------------------------
    clock = core.Clock()
    while clock.getTime() < ITI_DURATION:
        fixation.draw()
        win.flip()

# ------------------------
# End screen
# ------------------------
end_text = visual.TextStim(
    win,
    text="Experiment Complete!\n\nThank you for participating.\n\nData has been saved.",
    height=0.08,
    color=TEXT_COLOR
)
end_text.draw()
win.flip()
core.wait(3.0)

# ------------------------
# Save data
# ------------------------
with open(log_file, "w", newline="") as f:
    if results:
        writer = csv.DictWriter(f, fieldnames=results[0].keys())
        writer.writeheader()
        writer.writerows(results)

print(f"Data saved to: {log_file}")
print(f"Total trials completed: {len(results)}")

# Cleanup
win.close()
pygame.quit()
core.quit()

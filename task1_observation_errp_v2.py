"""
Task 1: PsychoPy Script to Elicit Observation ErrPs

Observation Error-Related Potential (ErrP) Experiment
Based on Chavarriaga & Millán (2010) paradigm

Subject passively observes cursor movements and generates EEG signals 
when perceiving errors in cursor performance.

USAGE:
    python task1_observation_errp_v2.py [preset]
    
    Available presets:
    - paper: Original Chavarriaga & Millán (2010) parameters (~20 min)
    - quick: Shortened version (~10 min) [DEFAULT]
    - full: Extended session (~25 min)
    - debug: Minimal trials for testing
"""

from psychopy import visual, core, event, gui, data
import os
import csv
import random
import time
import sys
from datetime import datetime
from config import get_config, print_preset_info, list_presets

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def select_preset():
    """
    Display GUI to select experiment preset.
    
    Returns:
        str: Selected preset name
    """
    preset_dlg = gui.Dlg(title='Experiment Configuration')
    preset_dlg.addField('Preset:', choices=['quick', 'paper', 'full', 'debug', 'v1_style'])
    preset_dlg.addText('')
    preset_dlg.addText('quick: ~10 min (2 blocks, 40 trials each)')
    preset_dlg.addText('paper: ~20 min (Original parameters)')
    preset_dlg.addText('full: ~25 min (4 blocks, 60 trials each)')
    preset_dlg.addText('debug: <2 min (Testing only)')
    preset_dlg.addText('v1_style: With TARGET REACHED feedback')
    
    preset_data = preset_dlg.show()
    
    if not preset_dlg.OK:
        core.quit()
    
    return preset_data[0]


def get_subject_info():
    """
    Display GUI dialog to collect subject information.
    
    Returns:
        dict: Subject information including ID, date, session number
    """
    exp_info = {
        'Subject ID': '',
        'Session Number': 1,
        'Experimenter Name': ''
    }
    
    dlg = gui.DlgFromDict(
        dictionary=exp_info,
        title='Observation ErrP Experiment',
        order=['Subject ID', 'Session Number', 'Experimenter Name']
    )
    
    if not dlg.OK:
        core.quit()  # User pressed cancel
    
    # Add session date
    exp_info['Session Date'] = datetime.now().strftime('%Y-%m-%d')
    exp_info['Session Time'] = datetime.now().strftime('%H:%M:%S')
    
    return exp_info


def generate_trial_sequence(n_trials, error_rate, max_consec_errors=3, max_consec_correct=5):
    """
    Generate pseudorandom sequence of trial types with constraints.
    
    Args:
        n_trials: Total number of trials
        error_rate: Proportion of error trials (0-1)
        max_consec_errors: Maximum consecutive error trials
        max_consec_correct: Maximum consecutive correct trials
    
    Returns:
        list: Sequence of trial types ('correct' or 'error')
    """
    n_errors = int(n_trials * error_rate)
    n_correct = n_trials - n_errors
    
    # Initialize sequence
    sequence = ['correct'] * n_correct + ['error'] * n_errors
    random.shuffle(sequence)
    
    # Enforce constraints
    valid = False
    attempts = 0
    max_attempts = 1000
    
    while not valid and attempts < max_attempts:
        valid = True
        
        # Check consecutive errors
        error_count = 0
        correct_count = 0
        
        for trial_type in sequence:
            if trial_type == 'error':
                error_count += 1
                correct_count = 0
                if error_count > max_consec_errors:
                    valid = False
                    break
            else:
                correct_count += 1
                error_count = 0
                if correct_count > max_consec_correct:
                    valid = False
                    break
        
        if not valid:
            random.shuffle(sequence)
            attempts += 1
    
    if attempts >= max_attempts:
        print(f"Warning: Could not generate valid sequence after {max_attempts} attempts")
    
    return sequence


def generate_target_position(current_pos, n_positions, min_distance=3):
    """
    Generate random target position with minimum distance constraint.
    
    Args:
        current_pos: Current cursor position index
        n_positions: Total number of positions
        min_distance: Minimum distance from current position
    
    Returns:
        int: Target position index
    """
    possible_positions = [i for i in range(n_positions) 
                         if abs(i - current_pos) >= min_distance]
    
    if not possible_positions:
        possible_positions = [i for i in range(n_positions) if i != current_pos]
    
    return random.choice(possible_positions)


def determine_error_direction(correct_direction):
    """
    Determine error movement direction (opposite or perpendicular).
    
    Args:
        correct_direction: 'left' or 'right'
    
    Returns:
        tuple: (error_direction, error_type)
    """
    # For 1D movement, only opposite direction is possible
    if correct_direction == 'right':
        return ('left', 'opposite')
    else:
        return ('right', 'opposite')


def get_unix_timestamp():
    """
    Get high-precision Unix timestamp.
    
    Returns:
        float: Unix timestamp with microsecond precision
    """
    return time.time()


def save_trial_data(filename, trial_data, exp_info):
    """
    Save trial data to CSV file.
    
    Args:
        filename: Output CSV filename
        trial_data: List of trial dictionaries
        exp_info: Experiment information dictionary
    """
    # Ensure data directory exists
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    
    # Define column order
    fieldnames = [
        'subject_id', 'session_date', 'session_num', 'block_num', 'trial_num',
        'trial_type', 'error_type', 'target_position', 'cursor_start', 'cursor_end',
        'movement_direction', 'trial_start_time', 'target_onset_time',
        'movement_onset_time', 'movement_end_time', 'trial_end_time',
        'response_key', 'response_time'
    ]
    
    with open(filename, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(trial_data)
    
    print(f"\nData saved to: {filename}")


# =============================================================================
# MAIN EXPERIMENT CLASS
# =============================================================================

class ObservationErrPExperiment:
    """Main experiment class for Observation ErrP paradigm."""
    
    def __init__(self, exp_info, config):
        """Initialize experiment with subject information and configuration."""
        self.exp_info = exp_info
        self.config = config
        self.trial_data = []
        self.experiment_start_time = get_unix_timestamp()
        
        # Create output filename
        self.output_filename = (
            f"data/sub-{exp_info['Subject ID']}_"
            f"date-{exp_info['Session Date']}_"
            f"preset-{exp_info.get('Preset', 'quick')}_"
            f"task-observation_errp.csv"
        )
        
        # Initialize PsychoPy window
        self.win = visual.Window(
            size=config['window_size'],
            units='pix',
            color=config['background_color'],
            fullscr=config['fullscreen'],
            allowGUI=not config['fullscreen']
        )
        
        self.win.mouseVisible = False
        
        # Create stimulus objects
        self.create_stimuli()
        
        # Generate spatial positions
        self.positions = self.generate_positions()
        
        # Initialize clocks
        self.global_clock = core.Clock()
    
    def create_stimuli(self):
        """Create all visual stimulus objects."""
        # Cursor
        self.cursor = visual.Circle(
            self.win,
            radius=self.config['cursor_radius'],
            fillColor=self.config['cursor_color'],
            lineColor=None
        )
        
        # Target
        self.target = visual.Circle(
            self.win,
            radius=self.config['target_radius'],
            fillColor=self.config['target_color'],
            lineColor=None
        )
        
        # Fixation cross
        self.fixation = visual.TextStim(
            self.win,
            text='+',
            height=self.config['fixation_size'],
            color=self.config['fixation_color']
        )
        
        # Instruction text
        self.instruction_text = visual.TextStim(
            self.win,
            text='',
            height=32,
            color=self.config['text_color'],
            wrapWidth=self.config['window_size'][0] * 0.8
        )
        
        # Block counter
        self.block_counter = visual.TextStim(
            self.win,
            text='',
            height=28,
            color=self.config['text_color'],
            pos=(0, -self.config['window_size'][1]//2 + 50)
        )
        
        # Target reached feedback (optional)
        if self.config['show_target_reached']:
            self.target_reached_text = visual.TextStim(
                self.win,
                text='TARGET REACHED!',
                height=40,
                color=self.config['target_reached_color'],
                bold=True,
                pos=(0, 100)
            )
    
    def generate_positions(self):
        """Generate array of cursor/target positions along horizontal axis."""
        screen_width = self.config['window_size'][0]
        margin = 100  # pixels from edge
        usable_width = screen_width - 2 * margin
        
        positions = []
        for i in range(self.config['n_positions']):
            x = -usable_width/2 + i * (usable_width / (self.config['n_positions'] - 1))
            positions.append(x)
        
        return positions
    
    def show_instructions(self, is_practice=False):
        """Display experiment instructions."""
        if is_practice:
            instructions = [
                "Practice Block\n\n"
                "You will now complete a short practice block.\n\n"
                "Remember:\n"
                "• Watch the cursor move toward the green target\n"
                "• The cursor may sometimes move in the WRONG direction\n"
                "• Simply observe - you do not control anything\n\n"
                "Press SPACE to begin practice"
            ]
        else:
            instructions = [
                "Welcome to the Observation ErrP Experiment\n\n"
                "In this task, you will observe a cursor moving on the screen.\n\n"
                "Your goal is to watch the cursor and determine whether it moves\n"
                "CORRECTLY toward the green target or INCORRECTLY (wrong direction).\n\n"
                "You do NOT control the cursor. Simply observe and pay attention.\n\n"
                "Press SPACE to continue",
                
                "Instructions:\n\n"
                "• Each trial begins with a fixation cross (+)\n"
                "• A green target will appear\n"
                "• The white cursor will move toward the target\n"
                "• Sometimes the cursor will move in the WRONG direction\n"
                "• This is intentional and happens automatically\n\n"
                "Press SPACE to continue",
                
                "Your Task:\n\n"
                "Simply OBSERVE the cursor movements.\n"
                "Pay attention to when errors occur.\n\n"
                f"The experiment will take approximately {int(self.config['estimated_duration_minutes'])} minutes.\n"
                f"Total trials: {self.config['total_trials']} ({self.config['n_blocks']} blocks)\n"
                "There will be short breaks between blocks.\n\n"
                "Press SPACE when ready to start"
            ]
        
        for instruction in instructions:
            self.instruction_text.text = instruction
            self.instruction_text.draw()
            self.win.flip()
            event.waitKeys(keyList=['space'])
    
    def show_break_screen(self, block_num, total_blocks):
        """Display break screen between blocks."""
        break_text = (
            f"Break Time!\n\n"
            f"Completed: {block_num} / {total_blocks} blocks\n\n"
            f"Take a {self.config['break_duration']} second break.\n"
            f"Relax and rest your eyes.\n\n"
            f"Press SPACE when ready to continue"
        )
        
        self.instruction_text.text = break_text
        self.instruction_text.draw()
        self.win.flip()
        event.waitKeys(keyList=['space'])
    
    def run_trial(self, trial_num, block_num, trial_type, is_practice=False):
        """
        Execute a single trial.
        
        Args:
            trial_num: Trial number within block
            block_num: Current block number
            trial_type: 'correct' or 'error'
            is_practice: Whether this is a practice trial
        
        Returns:
            dict: Trial data
        """
        # Initialize trial data
        trial_info = {
            'subject_id': self.exp_info['Subject ID'],
            'session_date': self.exp_info['Session Date'],
            'session_num': self.exp_info['Session Number'],
            'block_num': block_num,
            'trial_num': trial_num,
            'trial_type': trial_type,
            'error_type': 'none',
            'response_key': 'none',
            'response_time': None
        }
        
        # Check for escape
        if event.getKeys(['escape']):
            self.cleanup()
            core.quit()
        
        # Record trial start
        trial_info['trial_start_time'] = get_unix_timestamp()
        
        # PHASE 1: Inter-Trial Interval (ITI)
        iti_duration = random.uniform(self.config['iti_min'], self.config['iti_max'])
        self.fixation.draw()
        self.win.flip()
        core.wait(iti_duration)
        
        # PHASE 2: Target Presentation
        cursor_start_idx = self.config['start_position_idx']
        target_idx = generate_target_position(cursor_start_idx, self.config['n_positions'])
        
        self.cursor.pos = (self.positions[cursor_start_idx], 0)
        self.target.pos = (self.positions[target_idx], 0)
        
        trial_info['cursor_start'] = f"({self.positions[cursor_start_idx]}, 0)"
        trial_info['target_position'] = f"({self.positions[target_idx]}, 0)"
        
        # Show target
        trial_info['target_onset_time'] = get_unix_timestamp()
        self.target.draw()
        self.cursor.draw()
        self.win.flip()
        core.wait(self.config['target_presentation'])
        
        # PHASE 3: Movement
        # Determine correct direction
        if target_idx > cursor_start_idx:
            correct_direction = 'right'
            correct_end_idx = cursor_start_idx + 1
        else:
            correct_direction = 'left'
            correct_end_idx = cursor_start_idx - 1
        
        # Determine actual movement based on trial type
        if trial_type == 'error':
            actual_direction, error_type = determine_error_direction(correct_direction)
            trial_info['error_type'] = error_type
            
            if actual_direction == 'right':
                cursor_end_idx = cursor_start_idx + 1
            else:
                cursor_end_idx = cursor_start_idx - 1
        else:
            actual_direction = correct_direction
            cursor_end_idx = correct_end_idx
        
        # Ensure cursor stays within bounds
        cursor_end_idx = max(0, min(self.config['n_positions'] - 1, cursor_end_idx))
        
        trial_info['movement_direction'] = actual_direction
        trial_info['cursor_end'] = f"({self.positions[cursor_end_idx]}, 0)"
        
        # Animate movement
        trial_info['movement_onset_time'] = get_unix_timestamp()
        
        start_pos = self.positions[cursor_start_idx]
        end_pos = self.positions[cursor_end_idx]
        
        # Smooth animation
        n_frames = int(self.config['movement_duration'] * 60)  # Assuming 60 Hz refresh
        for frame in range(n_frames):
            t = frame / n_frames
            current_x = start_pos + t * (end_pos - start_pos)
            
            self.cursor.pos = (current_x, 0)
            self.target.draw()
            self.cursor.draw()
            self.win.flip()
        
        trial_info['movement_end_time'] = get_unix_timestamp()
        
        # PHASE 4: Post-Movement
        self.cursor.pos = (self.positions[cursor_end_idx], 0)
        self.target.draw()
        self.cursor.draw()
        self.win.flip()
        core.wait(self.config['post_movement'])
        
        # PHASE 5: Target Reached Feedback (optional)
        if self.config['show_target_reached'] and cursor_end_idx == target_idx:
            self.target.fillColor = self.config['target_reached_color']
            self.target.draw()
            self.cursor.draw()
            self.target_reached_text.draw()
            self.win.flip()
            core.wait(self.config['target_reached_duration'])
            self.target.fillColor = self.config['target_color']  # Reset color
        
        # Record trial end
        trial_info['trial_end_time'] = get_unix_timestamp()
        
        return trial_info
    
    def run_practice_block(self):
        """Run practice trials."""
        self.show_instructions(is_practice=True)
        
        # Generate practice trial sequence
        trial_sequence = generate_trial_sequence(
            self.config['n_practice_trials'],
            self.config['error_rate'],
            self.config['max_consecutive_errors'],
            self.config['max_consecutive_correct']
        )
        
        for trial_num, trial_type in enumerate(trial_sequence, 1):
            self.run_trial(trial_num, 0, trial_type, is_practice=True)
        
        # Practice complete message
        self.instruction_text.text = (
            "Practice Complete!\n\n"
            "You are now ready for the main experiment.\n\n"
            "Press SPACE to begin"
        )
        self.instruction_text.draw()
        self.win.flip()
        event.waitKeys(keyList=['space'])
    
    def run_experiment(self):
        """Run the complete experiment."""
        # Show instructions
        self.show_instructions(is_practice=False)
        
        # Run practice block
        self.run_practice_block()
        
        # Run experimental blocks
        for block_num in range(1, self.config['n_blocks'] + 1):
            # Generate trial sequence for this block
            trial_sequence = generate_trial_sequence(
                self.config['n_trials_per_block'],
                self.config['error_rate'],
                self.config['max_consecutive_errors'],
                self.config['max_consecutive_correct']
            )
            
            # Block start message
            self.instruction_text.text = (
                f"Block {block_num} of {self.config['n_blocks']}\n\n"
                f"Press SPACE to begin"
            )
            self.instruction_text.draw()
            self.win.flip()
            event.waitKeys(keyList=['space'])
            
            # Run trials in block
            for trial_num, trial_type in enumerate(trial_sequence, 1):
                trial_data = self.run_trial(trial_num, block_num, trial_type)
                self.trial_data.append(trial_data)
            
            # Show break screen (except after last block)
            if block_num < self.config['n_blocks']:
                self.show_break_screen(block_num, self.config['n_blocks'])
        
        # Experiment complete
        self.show_completion_message()
        
        # Save data
        save_trial_data(self.output_filename, self.trial_data, self.exp_info)
        
        # Cleanup
        self.cleanup()
    
    def show_completion_message(self):
        """Display experiment completion message."""
        self.instruction_text.text = (
            "Experiment Complete!\n\n"
            "Thank you for participating.\n\n"
            "Please inform the experimenter."
        )
        self.instruction_text.draw()
        self.win.flip()
        core.wait(3.0)
    
    def cleanup(self):
        """Clean up and close experiment."""
        self.win.close()


# =============================================================================
# MAIN EXECUTION
# =============================================================================

if __name__ == '__main__':
    # Check for command line preset argument
    if len(sys.argv) > 1:
        preset_name = sys.argv[1]
        if preset_name in ['help', '--help', '-h']:
            list_presets()
            core.quit()
        config = get_config(preset_name)
        print_preset_info(preset_name)
    else:
        # GUI selection
        preset_name = select_preset()
        config = get_config(preset_name)
        print(f"\nUsing preset: {preset_name}")
        print(f"Estimated duration: {config['estimated_duration_minutes']:.1f} minutes")
        print(f"Total trials: {config['total_trials']}\n")
    
    # Get subject information
    exp_info = get_subject_info()
    exp_info['Preset'] = preset_name
    
    # Create and run experiment
    experiment = ObservationErrPExperiment(exp_info, config)
    experiment.run_experiment()
    
    # Exit
    core.quit()

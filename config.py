"""
Configuration presets for Observation ErrP Experiment

Available presets:
- 'paper': Original Chavarriaga & Millán (2010) parameters
- 'quick': Shortened version for testing/demos
- 'full': Full experimental session
- 'debug': Minimal trials for debugging
"""

# =============================================================================
# PRESET CONFIGURATIONS
# =============================================================================

PRESETS = {
    # Original paper parameters (Chavarriaga & Millán, 2010)
    'paper': {
        'name': 'Paper Standard',
        'description': 'Original Chavarriaga & Millán (2010) parameters',
        'n_practice_trials': 20,
        'n_blocks': 3,
        'n_trials_per_block': 80,  # 240 total trials
        'iti_min': 1.5,
        'iti_max': 2.5,
        'target_presentation': 0.5,
        'movement_duration': 0.5,
        'post_movement': 0.5,
        'break_duration': 60,
        'error_rate': 0.25,
        'show_target_reached': False,  # Not mentioned in paper
        'target_reached_duration': 0.0,
    },
    
    # Quick version for shorter sessions
    'quick': {
        'name': 'Quick Session',
        'description': 'Shortened version (~10 minutes)',
        'n_practice_trials': 10,
        'n_blocks': 2,
        'n_trials_per_block': 40,  # 80 total trials
        'iti_min': 1.0,
        'iti_max': 1.5,
        'target_presentation': 0.5,
        'movement_duration': 0.5,
        'post_movement': 0.3,
        'break_duration': 30,
        'error_rate': 0.25,
        'show_target_reached': False,
        'target_reached_duration': 0.0,
    },
    
    # Full experimental session
    'full': {
        'name': 'Full Session',
        'description': 'Extended session for maximum data collection',
        'n_practice_trials': 20,
        'n_blocks': 4,
        'n_trials_per_block': 60,  # 240 total trials
        'iti_min': 1.0,
        'iti_max': 1.5,
        'target_presentation': 0.5,
        'movement_duration': 0.5,
        'post_movement': 0.5,
        'break_duration': 30,
        'error_rate': 0.25,
        'show_target_reached': False,
        'target_reached_duration': 0.0,
    },
    
    # Debug/testing
    'debug': {
        'name': 'Debug Mode',
        'description': 'Minimal trials for testing',
        'n_practice_trials': 3,
        'n_blocks': 1,
        'n_trials_per_block': 10,
        'iti_min': 0.5,
        'iti_max': 0.8,
        'target_presentation': 0.3,
        'movement_duration': 0.3,
        'post_movement': 0.2,
        'break_duration': 5,
        'error_rate': 0.3,
        'show_target_reached': True,  # For debugging
        'target_reached_duration': 0.5,
    },
    
    # Original v1 behavior (with TARGET REACHED feedback)
    'v1_style': {
        'name': 'Version 1 Style',
        'description': 'Original implementation with success feedback',
        'n_practice_trials': 15,
        'n_blocks': 2,
        'n_trials_per_block': 30,
        'iti_min': 0.5,
        'iti_max': 0.5,
        'target_presentation': 1.0,
        'movement_duration': 0.8,
        'post_movement': 0.0,
        'break_duration': 30,
        'error_rate': 0.2,
        'show_target_reached': True,
        'target_reached_duration': 1.0,
    },
}

# =============================================================================
# FIXED PARAMETERS (Not usually changed)
# =============================================================================

FIXED_PARAMS = {
    # Spatial parameters
    'n_positions': 20,
    'start_position_idx': 10,  # Center
    
    # Error constraints
    'max_consecutive_errors': 3,
    'max_consecutive_correct': 5,
    
    # Visual parameters
    'window_size': [1920, 1080],
    'fullscreen': True,
    'cursor_radius': 15,
    'target_radius': 20,
    'fixation_size': 30,
    
    # Colors (normalized -1 to 1)
    'background_color': [0, 0, 0],  # Black
    'cursor_color': [1, 1, 1],  # White
    'target_color': [0, 1, 0],  # Green
    'target_reached_color': [1, 1, 0],  # Yellow
    'fixation_color': [1, 1, 1],  # White
    'text_color': [1, 1, 1],  # White
}

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_config(preset='quick'):
    """
    Get complete configuration by merging preset with fixed parameters.
    
    Args:
        preset: Name of preset configuration ('paper', 'quick', 'full', 'debug')
    
    Returns:
        dict: Complete configuration dictionary
    """
    if preset not in PRESETS:
        raise ValueError(f"Unknown preset: {preset}. Available: {list(PRESETS.keys())}")
    
    config = FIXED_PARAMS.copy()
    config.update(PRESETS[preset])
    
    # Calculate derived values
    config['total_trials'] = config['n_blocks'] * config['n_trials_per_block']
    config['estimated_duration_minutes'] = estimate_duration(config)
    
    return config


def estimate_duration(config):
    """
    Estimate total experiment duration in minutes.
    
    Args:
        config: Configuration dictionary
    
    Returns:
        float: Estimated duration in minutes
    """
    # Average trial duration
    avg_iti = (config['iti_min'] + config['iti_max']) / 2
    trial_duration = (
        avg_iti + 
        config['target_presentation'] + 
        config['movement_duration'] + 
        config['post_movement']
    )
    
    if config['show_target_reached']:
        trial_duration += config['target_reached_duration']
    
    # Practice time
    practice_time = config['n_practice_trials'] * trial_duration
    
    # Experimental blocks time
    experimental_time = config['total_trials'] * trial_duration
    
    # Break time (between blocks, not after last block)
    break_time = (config['n_blocks'] - 1) * config['break_duration']
    
    # Instruction time (rough estimate)
    instruction_time = 120  # 2 minutes
    
    total_seconds = practice_time + experimental_time + break_time + instruction_time
    return total_seconds / 60


def print_preset_info(preset='quick'):
    """
    Print detailed information about a preset.
    
    Args:
        preset: Name of preset to display
    """
    config = get_config(preset)
    
    print(f"\n{'='*60}")
    print(f"PRESET: {config['name']}")
    print(f"{'='*60}")
    print(f"Description: {config['description']}")
    print(f"\nSession Structure:")
    print(f"  Practice trials: {config['n_practice_trials']}")
    print(f"  Experimental blocks: {config['n_blocks']}")
    print(f"  Trials per block: {config['n_trials_per_block']}")
    print(f"  Total trials: {config['total_trials']}")
    print(f"\nTiming:")
    print(f"  ITI: {config['iti_min']:.1f}-{config['iti_max']:.1f}s")
    print(f"  Target presentation: {config['target_presentation']:.1f}s")
    print(f"  Movement duration: {config['movement_duration']:.1f}s")
    print(f"  Post-movement: {config['post_movement']:.1f}s")
    print(f"  Break duration: {config['break_duration']}s")
    print(f"\nError Parameters:")
    print(f"  Error rate: {config['error_rate']*100:.0f}%")
    print(f"  Max consecutive errors: {config['max_consecutive_errors']}")
    print(f"  Max consecutive correct: {config['max_consecutive_correct']}")
    print(f"\nFeedback:")
    print(f"  Show 'TARGET REACHED': {config['show_target_reached']}")
    if config['show_target_reached']:
        print(f"  Duration: {config['target_reached_duration']:.1f}s")
    print(f"\nEstimated Duration: {config['estimated_duration_minutes']:.1f} minutes")
    print(f"{'='*60}\n")


def list_presets():
    """Print all available presets with brief descriptions."""
    print("\nAvailable Presets:")
    print("="*60)
    for preset_name, preset_data in PRESETS.items():
        config = get_config(preset_name)
        print(f"\n'{preset_name}':")
        print(f"  {preset_data['description']}")
        print(f"  Duration: ~{config['estimated_duration_minutes']:.0f} minutes")
        print(f"  Trials: {config['total_trials']} ({config['n_blocks']} blocks × {config['n_trials_per_block']})")
    print()


if __name__ == '__main__':
    # Demo: show all presets
    list_presets()
    
    # Show detailed info for each preset
    for preset_name in PRESETS.keys():
        print_preset_info(preset_name)

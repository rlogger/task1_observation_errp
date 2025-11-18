import pygame
import random
import csv
import os
import time

# -------------------------------
# Experiment parameters
# -------------------------------
N_POSITIONS = 20
TRIAL_DURATION = 2.0     # seconds
ERROR_PROB = 0.2
N_EPISODES = 10

# -------------------------------
# Setup pygame window
# -------------------------------
pygame.init()
screen = pygame.display.set_mode((1280, 720))
pygame.display.set_caption("ErrP Observation Task")
clock = pygame.time.Clock()

# Colors
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
BLUE  = (0, 128, 255)
RED   = (255, 80, 80)
BLACK = (0, 0, 0)

# Fixation font
font = pygame.font.SysFont("Arial", 60)

# -------------------------------
# Prepare positions
# -------------------------------
positions = [int(100 + i * (1080 / (N_POSITIONS - 1))) for i in range(N_POSITIONS)]

cursor_idx = N_POSITIONS // 2

def choose_new_target(i):
    offset = random.choice([-3,-2,-1,1,2,3])
    j = i + offset
    if 0 <= j < N_POSITIONS:
        return j
    else:
        return N_POSITIONS // 2

def direction(a, b):
    if b > a:
        return 1
    elif b < a:
        return -1
    return 0

# -------------------------------
# Logging
# -------------------------------
os.makedirs("data", exist_ok=True)
log_file = "data/errp_log.csv"

results = []
start_time = time.time()

# -------------------------------
# Main experiment loop
# -------------------------------
target_idx = choose_new_target(cursor_idx)

for ep in range(N_EPISODES):

    reached = False
    while not reached:

        # Quit key
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                pygame.quit()
                exit()

        # Movement step
        d = direction(cursor_idx, target_idx)

        # Inject error with probability
        is_error = random.random() < ERROR_PROB
        move = -d if is_error else d

        cursor_idx = max(0, min(N_POSITIONS - 1, cursor_idx + move))

        # Target color
        if target_idx < cursor_idx:
            target_color = BLUE
        elif target_idx > cursor_idx:
            target_color = RED
        else:
            target_color = WHITE

        # -------------------------------
        # Draw frame
        # -------------------------------
        screen.fill(BLACK)

        # Fixation
        fix = font.render("+", True, WHITE)
        screen.blit(fix, (640 - 20, 360 - 40))

        # Cursor (green square)
        pygame.draw.rect(screen, GREEN,
                         pygame.Rect(positions[cursor_idx], 340, 40, 40))

        # Target square
        pygame.draw.rect(screen, target_color,
                         pygame.Rect(positions[target_idx], 340, 40, 40))

        pygame.display.flip()

        # Trial duration
        pygame.time.delay(int(TRIAL_DURATION * 1000))

        # Log
        results.append({
            "time": time.time() - start_time,
            "episode": ep,
            "cursor_idx": cursor_idx,
            "target_idx": target_idx,
            "is_error": int(is_error)
        })

        # Check if target reached
        if cursor_idx == target_idx:
            reached = True

    # New target for next episode
    target_idx = choose_new_target(cursor_idx)

# -------------------------------
# Save log
# -------------------------------
with open(log_file, "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=results[0].keys())
    writer.writeheader()
    writer.writerows(results)

pygame.quit()
print("Experiment finished. Log saved to", log_file)

from psychopy import visual, core, event
import os, csv, random

N_POSITIONS = 20
TRIAL_DURATION = 2.0
ERROR_PROB = 0.2
N_EPISODES = 10

os.makedirs("data/logs", exist_ok=True)
log_file = "data/logs/errp_log.csv"

win = visual.Window([1280, 720], units="norm")

positions = [-0.8 + i * (1.6/(N_POSITIONS-1)) for i in range(N_POSITIONS)]
cursor = visual.Rect(win, width=0.06, height=0.06, fillColor="green")
target = visual.Rect(win, width=0.06, height=0.06)
fixation = visual.TextStim(win, text="+")

def new_target(i):
    offset = random.choice([-3,-2,-1,1,2,3])
    j = i + offset
    return j if 0 <= j < N_POSITIONS else N_POSITIONS//2

def direction(a,b):
    return 1 if b>a else -1 if b<a else 0

results=[]
cursor_idx = N_POSITIONS//2
target_idx = new_target(cursor_idx)
global_clock = core.Clock()

for ep in range(N_EPISODES):

    reached=False
    while not reached:

        if "escape" in event.getKeys():
            win.close(); core.quit()

        d = direction(cursor_idx,target_idx)
        is_error = random.random()<ERROR_PROB
        move = -d if is_error else d
        cursor_idx = max(0,min(N_POSITIONS-1,cursor_idx+move))

        target.fillColor = "blue" if target_idx<cursor_idx else "red" if target_idx>cursor_idx else "white"
        cursor.pos=(positions[cursor_idx],0)
        target.pos=(positions[target_idx],0)

        clock = core.Clock()
        while clock.getTime()<TRIAL_DURATION:
            fixation.draw(); cursor.draw(); target.draw()
            win.flip()

        results.append({
            "time": global_clock.getTime(),
            "episode": ep,
            "cursor_idx": cursor_idx,
            "target_idx": target_idx,
            "is_error": int(is_error)
        })

        if cursor_idx==target_idx:
            reached=True

    target_idx=new_target(cursor_idx)

with open(log_file,"w",newline="") as f:
    writer=csv.DictWriter(f,fieldnames=results[0].keys())
    writer.writeheader(); writer.writerows(results)

win.close()
core.quit()
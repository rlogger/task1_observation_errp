# PsychoPy (minimal install)

Minimal instructions to set up PsychoPy on macOS using Nix and a Python virtual environment.

**Prerequisites**
- macOS
- Nix installed
- `zsh` (default shell)

**Steps**

1. Enter the Nix shell (uses `shell.nix` in this repo):

```bash
nix-shell
```

2. Create and activate a virtual environment:

```bash
python3 -m venv psychopy-venv
source psychopy-venv/bin/activate
```

3. Install PsychoPy inside the venv:

```bash
pip install psychopy
```

Notes:
- If you run into dependency issues (e.g., `wxPython`), you may need extra Nix packages or to install platform-specific wheels.
- PsychoPy recommends Python 3.10 for best compatibility: https://www.psychopy.org/download.html

That's it — this README is intentionally minimal. If you want, I can expand it to include troubleshooting, GUI launch instructions, or a `requirements.txt`.

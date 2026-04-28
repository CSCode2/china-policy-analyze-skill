import os
import subprocess
import sys


def run_daily_update():
    cwd = os.getcwd()
    script = os.path.join(cwd, "scripts", "_run_daily_update.py")
    if not os.path.exists(script):
        print(f"Error: {script} not found. Run from the project root directory.", file=sys.stderr)
        sys.exit(1)
    os.execv(sys.executable, [sys.executable, script] + sys.argv[1:])

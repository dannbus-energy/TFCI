#!/usr/bin/env python3
"""TFCI app command hub. Run from tfci_app/."""
import subprocess, sys

def run(cmd):
    print("$", " ".join(cmd))
    return subprocess.call(cmd)

def up():
    return run(["docker", "compose", "up", "-d"])

def down():
    return run(["docker", "compose", "down"])

def load():
    return run([sys.executable, "db/load.py"])

def api():
    return run([sys.executable, "-m", "uvicorn", "api.main:app", "--reload", "--port", "8000"])

def gate():
    return run([sys.executable, "pipelines/run_gate.py"])

def check():
    return run([sys.executable, "../bootstrap_tfci_v1.py", "--check-only"])

CMDS = {"up": up, "down": down, "load": load, "api": api, "gate": gate, "check": check}

if __name__ == "__main__":
    what = sys.argv[1] if len(sys.argv) > 1 else ""
    if what not in CMDS:
        print("usage: python tasks.py {up|down|load|api|gate|check}")
        sys.exit(2)
    sys.exit(CMDS[what]())

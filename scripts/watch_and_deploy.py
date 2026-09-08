#!/usr/bin/env python3
"""
Continuous file watcher for Hero VIDA Intelligence Agent.
Watches the 'agent/' folder and automatically deploys changes to
Vertex AI Agent Engine (3838207625833480192) when files are modified.
"""

import os
import sys
import time
import subprocess
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
AGENT_DIR = ROOT_DIR / "agent"
DEPLOY_SCRIPT = ROOT_DIR / "deploy.sh"
ENGINE_ID = os.environ.get("AGENT_ENGINE_ID", "3838207625833480192")
DEBOUNCE_SECONDS = 3.0

def get_dir_mtime(dir_path: Path) -> float:
    latest = 0.0
    for p in dir_path.rglob("*"):
        if "__pycache__" in str(p) or ".pyc" in str(p):
            continue
        try:
            mtime = p.stat().st_mtime
            if mtime > latest:
                latest = mtime
        except (OSError, FileNotFoundError):
            pass
    return latest

def trigger_deploy():
    print(f"\n🚀 [Auto-Deploy] Detected change in 'agent/'. Triggering deploy to Engine {ENGINE_ID}...")
    cmd = [str(DEPLOY_SCRIPT), "--auto", f"--id={ENGINE_ID}"]
    try:
        proc = subprocess.Popen(cmd, cwd=str(ROOT_DIR))
        proc.wait()
        if proc.returncode == 0:
            print(f"✅ [Auto-Deploy] Successfully deployed update to Agent Engine {ENGINE_ID}!")
        else:
            print(f"❌ [Auto-Deploy] Deploy exited with code {proc.returncode}")
    except Exception as e:
        print(f"❌ [Auto-Deploy] Error during deploy: {e}")

def main():
    print("==========================================================")
    print(f"👀 Watching '{AGENT_DIR}' for code changes...")
    print(f"🎯 Target Agent Engine: {ENGINE_ID}")
    print("💡 Saving any file in 'agent/' will automatically trigger deployment.")
    print("==========================================================")

    last_mtime = get_dir_mtime(AGENT_DIR)

    while True:
        try:
            time.sleep(1.0)
            current_mtime = get_dir_mtime(AGENT_DIR)
            if current_mtime > last_mtime:
                # Debounce rapid edits
                time.sleep(DEBOUNCE_SECONDS)
                last_mtime = get_dir_mtime(AGENT_DIR)
                trigger_deploy()
        except KeyboardInterrupt:
            print("\nExiting watcher.")
            break
        except Exception as e:
            time.sleep(2.0)

if __name__ == "__main__":
    main()

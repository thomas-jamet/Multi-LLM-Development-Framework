#!/usr/bin/env python3
"""Session management for Gemini workspaces."""
import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

def load_sessions():
    log_path = Path("logs/sessions/history.json")
    if log_path.exists():
        try:
            with open(log_path) as f:
                return json.load(f)
        except json.JSONDecodeError:
            pass
    return []

def save_session(entry):
    log_dir = Path("logs/sessions")
    log_dir.mkdir(parents=True, exist_ok=True)
    
    history = load_sessions()
    history.append(entry)
    
    with open(log_dir / "history.json", "w") as f:
        json.dump(history, f, indent=2)
        
    # Also append to human readable log
    with open(log_dir / "session.log", "a") as f:
        f.write(f"[{entry['timestamp']}] {entry['action'].upper()}: {entry['message']}\n")

def get_git_status():
    try:
        # Get brief stats
        res = subprocess.run(
            ["git", "diff", "--shortstat"], 
            capture_output=True, text=True
        )
        if res.stdout.strip():
            return f"Auto-generated: {res.stdout.strip()}"
            
        # If no diff, maybe staged changes?
        res = subprocess.run(
            ["git", "diff", "--cached", "--shortstat"],
            capture_output=True, text=True
        )
        if res.stdout.strip():
            return f"Auto-generated (staged): {res.stdout.strip()}"
            
        return "Session ended (no changes detected)"
    except FileNotFoundError:
        return "Session ended (git not available)"

def start_session(msg):
    message = msg if msg else "Session started"
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "action": "start",
        "message": message
    }
    save_session(entry)
    print(f"🚀 Session started: {message}")

def end_session(msg):
    message = msg if msg else get_git_status()
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "action": "end",
        "message": message
    }
    save_session(entry)
    print(f"🎬 Session ended: {message}")

def main():
    parser = argparse.ArgumentParser(description="Session Manager")
    parser.add_argument("command", choices=["start", "end", "force-end-all"])
    parser.add_argument("msg", nargs="?", default="", help="Session message")
    
    args = parser.parse_args()
    
    if args.command == "start":
        start_session(args.msg)
    elif args.command == "end":
        end_session(args.msg)
    elif args.command == "force-end-all":
        print("Force ending all sessions...")

if __name__ == "__main__":
    main()

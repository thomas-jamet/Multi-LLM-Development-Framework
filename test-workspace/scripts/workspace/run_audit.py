#!/usr/bin/env python3
"""Workspace structure auditor - validates against Gemini Standard."""
import os
import sys
from pathlib import Path

def main():
    print("🔍 Auditing workspace structure...")
    errors = 0
    
    # Check core files
    required = ["GEMINI.md", "Makefile", ".gemini/workspace.json"]
    for f in required:
        if not Path(f).exists():
            print(f"❌ Missing core file: {f}")
            errors += 1
            
    # Check directories
    required_dirs = ["logs", "docs"]
    for d in required_dirs:
        if not Path(d).exists():
            print(f"❌ Missing directory: {d}/")
            errors += 1
            
    if errors == 0:
        print("✅ Audit passed.")
        sys.exit(0)
    else:
        print(f"❌ Audit failed with {errors} errors.")
        sys.exit(1)

if __name__ == "__main__":
    main()

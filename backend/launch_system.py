#!/usr/bin/env python3
"""
Launcher script to run both main.py (face recognition)
and sales_call_analyzer.py (sales call analysis) simultaneously.
"""

import subprocess
import sys
import os
import time
from pathlib import Path

def main():
    print("="*70)
    print("🚀 UNIFIED SALES CALL SYSTEM LAUNCHER")
    print("="*70)
    print()
    print("This will start:")
    print("  1. Face Recognition System (main.py)")
    print("  2. Sales Call Analyzer (sales_call_analyzer.py)")
    print()
    print("Press Ctrl+C to stop both processes")
    print("="*70)
    print()

    # Get the directory where this script is located
    script_dir = Path(__file__).parent

    # Paths to the scripts
    main_py = script_dir / "main.py"
    sales_analyzer = script_dir / "sales_call_analyzer.py"

    # Check if files exist
    if not main_py.exists():
        print(f"❌ Error: {main_py} not found!")
        sys.exit(1)

    if not sales_analyzer.exists():
        print(f"❌ Error: {sales_analyzer} not found!")
        sys.exit(1)

    # Start both processes
    processes = []

    try:
        # Start main.py (Face Recognition)
        print("🎥 Starting Face Recognition System (main.py)...")
        main_process = subprocess.Popen(
            [sys.executable, str(main_py)],
            cwd=str(script_dir)
        )
        processes.append(("Face Recognition", main_process))
        time.sleep(2)  # Give it time to initialize

        # Start sales_call_analyzer.py
        print("📞 Starting Sales Call Analyzer (sales_call_analyzer.py)...")
        analyzer_process = subprocess.Popen(
            [sys.executable, str(sales_analyzer)],
            cwd=str(script_dir)
        )
        processes.append(("Sales Analyzer", analyzer_process))

        print()
        print("✅ Both systems started successfully!")
        print()
        print("="*70)
        print("SYSTEM STATUS:")
        print("  Face Recognition: RUNNING")
        print("  Sales Analyzer: RUNNING")
        print("="*70)
        print()
        print("💡 TIP: Use the Face Recognition window to register new faces")
        print("💡 TIP: Sales Analyzer will use the recognized faces for calls")
        print()
        print("Press Ctrl+C to stop all processes...")
        print()

        # Wait for processes
        while True:
            # Check if any process died
            for name, proc in processes:
                if proc.poll() is not None:
                    print(f"⚠️  {name} stopped unexpectedly (exit code: {proc.returncode})")

            time.sleep(1)

    except KeyboardInterrupt:
        print()
        print("="*70)
        print("🛑 Stopping all processes...")
        print("="*70)

        # Terminate all processes
        for name, proc in processes:
            if proc.poll() is None:  # Still running
                print(f"  Stopping {name}...")
                proc.terminate()
                try:
                    proc.wait(timeout=5)
                    print(f"  ✅ {name} stopped")
                except subprocess.TimeoutExpired:
                    print(f"  ⚠️  Force killing {name}...")
                    proc.kill()

        print()
        print("✅ All processes stopped")
        print("="*70)

    except Exception as e:
        print(f"❌ Error: {e}")
        # Clean up processes
        for name, proc in processes:
            if proc.poll() is None:
                proc.kill()
        sys.exit(1)

if __name__ == "__main__":
    main()

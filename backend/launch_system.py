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
    print("     → Detects & locks customer faces")
    print("     → Updates active_session table in Supabase")
    print()
    print("  2. Sales Call Analyzer (sales_call_analyzer.py)")
    print("     → Reads customer_id from active_session")
    print("     → Transcribes call & provides AI insights")
    print("     → Saves conversation & customer profile")
    print()
    print("🔄 The systems communicate via Supabase active_session table")
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
        # Start main.py (Face Recognition) - runs in background
        print("🎥 Starting Face Recognition System (main.py)...")
        main_process = subprocess.Popen(
            [sys.executable, str(main_py)],
            cwd=str(script_dir),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        processes.append(("Face Recognition", main_process))
        time.sleep(2)  # Give it time to initialize

        # Start sales_call_analyzer.py - runs in foreground with input access
        print("📞 Starting Sales Call Analyzer (sales_call_analyzer.py)...")
        print("    This will take over the terminal for keyboard input.")
        print("    Face Recognition will run in the background.\n")
        time.sleep(1)
        
        analyzer_process = subprocess.Popen(
            [sys.executable, str(sales_analyzer)],
            cwd=str(script_dir)
            # No stdout/stderr redirect - inherits terminal
        )
        processes.append(("Sales Analyzer", analyzer_process))

        print()
        print("✅ Both systems started successfully!")
        print()
        print("="*70)
        print("SYSTEM STATUS:")
        print("  ✅ Face Recognition: RUNNING")
        print("  ✅ Sales Analyzer: RUNNING")
        print("="*70)
        print()
        print("📋 HOW IT WORKS:")
        print("  1. main.py detects face → locks customer → writes to Supabase")
        print("  2. sales_call_analyzer.py reads customer_id from Supabase")
        print("  3. When call ends, Gemini extracts personal/professional/sales info")
        print("  4. Customer profile is saved/updated in customers table")
        print()
        print("⌨️  HOW TO END CALL:")
        print("  • Type 'q' + ENTER in THIS terminal")
        print("    → This ends call gracefully and saves customer profile")
        print("  • To force stop everything: Press Ctrl+C")
        print()
        print("💡 TIP: Face Recognition runs in background with camera window")
        print("💡 TIP: Customer must be locked for 2+ seconds to save profile")
        print("💡 TIP: You can type 'q' anytime to end the call")
        print()

        # Wait for sales analyzer to finish (it controls the terminal)
        # Face recognition keeps running in background
        print("📞 Sales Call Analyzer is now active...")
        print("    (You should see its output above)")
        print("    Type 'q' + ENTER when ready to end the call\n")
        
        analyzer_process.wait()  # Blocks until sales analyzer exits
        
        print("\n✅ Sales Analyzer stopped")
        print("🛑 Stopping Face Recognition...")
        
        # Stop main.py (face recognition)
        if main_process.poll() is None:
            main_process.terminate()
            try:
                main_process.wait(timeout=3)
                print("✅ Face Recognition stopped")
            except subprocess.TimeoutExpired:
                main_process.kill()
                print("✅ Face Recognition killed")
        
        print("\n" + "="*70)
        print("✅ ALL SYSTEMS STOPPED")
        print("="*70)

    except KeyboardInterrupt:
        print()
        print("="*70)
        print("🛑 Ctrl+C detected - Stopping all processes...")
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

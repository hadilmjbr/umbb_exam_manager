import sys
import os
import pandas as pd

# Add project root to path
sys.path.append(os.getcwd())

from backend.admin import audit_quality

def verify_audit():
    print("Running audit_quality...")
    reports = audit_quality()
    if not reports:
        print("Audit returned empty report set (error?)")
        return

    print("--- 1. Student Conflicts ---")
    if not reports['etudiants'].empty:
        print(reports['etudiants'])
    else:
        print("None detected.")

    print("\n--- 2. Room Capacity ---")
    if not reports['salles'].empty:
        print(reports['salles'])
    else:
        print("None detected.")

    print("\n--- 3. Professor Conflicts ---")
    if not reports['profs'].empty:
        print(reports['profs'])
    else:
        print("None detected.")

if __name__ == "__main__":
    verify_audit()

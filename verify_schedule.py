import sys
import os
import pandas as pd

# Add project root to path
sys.path.append(os.getcwd())

from backend.db import get_connection
from backend.admin import get_global_schedule

def verify():
    print("Verifying get_global_schedule...")
    df = get_global_schedule()
    if not df.empty:
        print("Schedule retrieved successfully.")
        print("Columns:", df.columns.tolist())
        print("First row:", df.iloc[0].to_dict())
    else:
        print("Schedule is empty (might be expected if generation not run, or error).")
        
    # Check if we can run generation (mock call or real?)
    # Real call might take time or duplicate exams if run multiple times.
    # But user wants functionality.
    
if __name__ == "__main__":
    verify()

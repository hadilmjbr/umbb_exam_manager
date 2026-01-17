import sys
import os

# Add the project root to sys.path
sys.path.append(os.getcwd())

from backend.admin import get_dashboard_kpis

try:
    kpis = get_dashboard_kpis()
    if kpis:
        print("KPIs retrieved successfully:")
        print(kpis)
    else:
        print("Failed to retrieve KPIs (returned None)")
except Exception as e:
    print(f"Error retrieving KPIs: {e}")

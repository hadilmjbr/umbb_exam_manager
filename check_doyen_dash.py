import backend.doyen_dashboard as dd
import pandas as pd

print("--- KPIs ---")
kpis = dd.get_global_kpis()
print(kpis)

print("\n--- By Dept ---")
df = dd.get_exams_by_dept()
print(df)

print("\n--- By Level ---")
df2 = dd.get_exams_by_level()
print(df2)

print("\n--- Prof Load ---")
df3, df4 = dd.get_prof_load_stats()
print(df4)

print("\n--- Compliance ---")
comp = dd.get_compliance_metrics()
print(comp)

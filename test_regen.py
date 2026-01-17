from backend.admin_workflow import regenerate_formation_schedule
import pandas as pd
from backend.db import get_connection

print("Testing regeneration for Formation ID = 2...")
ok, msg = regenerate_formation_schedule(2)
print(f"Status: {ok}")
print(f"Message: {msg}")

# Check status in DB
conn = get_connection()
status = pd.read_sql("SELECT statut, commentaire FROM validation_pedagogique WHERE formation_id = 2", conn)
print("DB Status:")
print(status)
conn.close()

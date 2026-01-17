
import os

def clean_ui():
    path = "frontend/app.py"
    try:
        with open(path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        
        new_lines = []
        for line in lines:
            # Fix Review 1: Alerts
            if 'alerts.append(f"❌ CHEVAUCHEMENT' in line:
                line = line.replace("❌", "[!]")
            elif 'alerts.append(f"⚠️ PAUSE COURTE' in line:
                line = line.replace("⚠️", "(!)")
            
            # Fix Review 2: Alert Check
            elif 'if "❌" in a: st.error(a)' in line:
                line = line.replace('"❌"', '"[!]"')
            elif 'if "CHEVAUCHEMENT" in a: st.error(a)' in line:
                # This one was modified in previous step, checking integrity
                pass 

            # Fix Review 3: Login Title (handle unknown char)
            elif 'st.title("' in line and 'UMBB Exam Manager")' in line:
                # Force clean title
                line = '        st.title("UMBB Exam Manager")\n'
                
            new_lines.append(line)
            
        with open(path, "w", encoding="utf-8") as f:
            f.writelines(new_lines)
            
        print("✅ UI Force Cleaned.")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    clean_ui()

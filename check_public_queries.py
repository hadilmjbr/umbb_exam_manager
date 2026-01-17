from backend.public import get_all_professors, get_professor_exams, get_all_departments, get_formations_by_dept_public

print("--- Testing Professors Query ---")
profs = get_all_professors()
print(f"Found {len(profs)} professors.")
if not profs.empty:
    print(profs.head(2))
    pid = profs.iloc[0]['id']
    print(f"\nExams for professor {pid}:")
    exams = get_professor_exams(pid)
    print(exams)

print("\n--- Testing Students Query ---")
depts = get_all_departments()
if not depts.empty:
    did = depts.iloc[0]['id']
    print(f"\nFormations for dept {did}:")
    fmts = get_formations_by_dept_public(did)
    # Note: fmts might be empty if no validation status VALIDE_DOYEN
    print(fmts)

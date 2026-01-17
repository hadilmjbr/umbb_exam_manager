"""
TEST ULTRA-SIMPLE
"""
from backend.auth import verify_user

print("\n" + "="*50)
print("TEST AUTHENTIFICATION")
print("="*50)

# Test 1: Admin
print("\n1. Test Admin (admin@umbb.dz / admin123):")
result = verify_user("admin@umbb.dz", "admin123")
if result:
    print(f"   ✅ SUCCÈS: {result}")
else:
    print(f"   ❌ ÉCHEC")

# Test 2: Doyen
print("\n2. Test Doyen (doyen@umbb.dz / 123456):")
result = verify_user("doyen@umbb.dz", "123456")
if result:
    print(f"   ✅ SUCCÈS: {result}")
else:
    print(f"   ❌ ÉCHEC")

print("\n" + "="*50)
print("Si les deux tests sont ✅, redémarrez Streamlit!")
print("="*50 + "\n")

"""
Final authentication test
"""
import sys
sys.path.insert(0, '.')

from backend.auth import verify_user

# Test cases
test_cases = [
    ("admin@umbb.dz", "admin123", "Admin"),
    ("doyen@umbb.dz", "123456", "Doyen"),  
    ("chef.informatique@umbb.dz", "123456", "Chef Informatique"),
]

print("="*60)
print("FINAL AUTHENTICATION TEST")
print("="*60)

for email, password, label in test_cases:
    print(f"\n Testing {label}:")
    print(f"   Email: {email}")
    print(f"   Password: {password}")
    
    result = verify_user(email, password)
    
    if result:
        print(f"   ✅ SUCCESS!")
        print(f"   User data: {result}")
    else:
        print(f"   ❌ FAILED - Identifiants incorrects")

print("\n" + "="*60)
print("If all tests passed, restart Streamlit and try logging in!")
print("If tests failed, there's still an issue with verify_user function")
print("="*60)

# generate_hash.py
# ==========================================
# Run this script ONCE to generate a proper password hash
# for inserting into the admin_users table.
#
# Usage:
#   python generate_hash.py
#
# Then copy the hash into your database.sql INSERT statement.
# ==========================================

from werkzeug.security import generate_password_hash, check_password_hash

def main():
    print("=" * 50)
    print("  CleanConnect - Admin Password Hash Generator")
    print("=" * 50)

    password = input("\nEnter the admin password you want to use: ").strip()

    if len(password) < 6:
        print("❌ Password must be at least 6 characters!")
        return

    # Generate the hash
    hashed = generate_password_hash(password)

    print("\n✅ Password hashed successfully!\n")
    print(f"Password : {password}")
    print(f"Hash     : {hashed}")
    print("\n📋 Use this SQL to update admin password:")
    print(f"""
UPDATE admin_users SET password = '{hashed}' WHERE username = 'admin';
""")
    print("Or use this to insert a new admin:")
    print(f"""
INSERT INTO admin_users (username, password) VALUES ('admin', '{hashed}');
""")

    # Verify it works
    verify = check_password_hash(hashed, password)
    print(f"✅ Verification: {'PASSED' if verify else 'FAILED'}")

if __name__ == '__main__':
    main()
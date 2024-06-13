from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
import os
import base64
import sqlite3
from pysqlcipher3 import dbapi2 as sqlcipher


class PasswordManager:
    def __init__(self, db_path='password_manager.db', iterations=100000):
        self.iterations = iterations
        self.backend = default_backend()
        self.salt_length = 16
        self.key_length = 32
        self.db_path = db_path

        # Initialize the database
        self.initialize_db()

    def initialize_db(self):
        db_exists = os.path.exists(self.db_path)
        if not db_exists:
            # Initialize the database only if it doesn't exist
            conn = sqlcipher.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''CREATE TABLE IF NOT EXISTS master_password
                              (id INTEGER PRIMARY KEY, salt BLOB, derived_key BLOB)''')
            conn.commit()
            conn.close()

    def derive_key_from_password(self, password, salt):
        # Derive a key from the master password using PBKDF2
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=self.key_length,
            salt=salt,
            iterations=self.iterations,
            backend=self.backend
        )
        return kdf.derive(password.encode())

    def create_master_password(self, master_password):
        # Generate a random salt
        salt = os.urandom(self.salt_length)
        # Derive a key from the master password
        derived_key = self.derive_key_from_password(master_password, salt)

        # Store the salt and derived key in the database
        conn = sqlcipher.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(f"PRAGMA key = '{base64.urlsafe_b64encode(derived_key).decode()}'")
        cursor.execute('DELETE FROM master_password')  # Ensure only one master password is stored
        cursor.execute('INSERT INTO master_password (salt, derived_key) VALUES (?, ?)', (salt, derived_key))
        conn.commit()
        conn.close()

    def verify_master_password(self, master_password):
        # Retrieve the salt and derived key from the database
        conn = sqlcipher.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT salt, derived_key FROM master_password')
        row = cursor.fetchone()
        conn.close()

        if row is None:
            return False

        salt, stored_derived_key = row
        # Derive the key from the provided master password
        derived_key = self.derive_key_from_password(master_password, salt)

        # Verify the derived key with the stored derived key
        if derived_key == stored_derived_key:
            # If the keys match, reinitialize the database connection with the correct key
            self.reinitialize_db_with_key(base64.urlsafe_b64encode(derived_key).decode())
            return True
        else:
            return False

    def reinitialize_db_with_key(self, key):
        conn = sqlcipher.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(f"PRAGMA key = '{key}'")
        conn.commit()
        conn.close()


if __name__ == "__main__":
    pm = PasswordManager()
    master_password = input("Enter a master password: ")

    # Create the master password
    pm.create_master_password(master_password)
    print("Master password stored successfully.")

    # Verify the master password
    verification_password = input("Re-enter the master password for verification: ")
    if pm.verify_master_password(verification_password):
        print("Master password verified successfully!")
    else:
        print("Master password verification failed.")

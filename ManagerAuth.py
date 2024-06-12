from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
import os
import base64

class AppAuthentication:
    def __init__(self, iterations=100000):
        self.iterations = iterations
        self.backend = default_backend()
        self.salt_length = 16
        self.key_length = 32

    def create_master_password(self, master_password):
        # Generate a random salt
        salt = os.urandom(self.salt_length)

        # Derive a key from the master password using PBKDF2
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=self.key_length,
            salt=salt,
            iterations=self.iterations,
            backend=self.backend
        )
        derived_key = kdf.derive(master_password.encode())

        # Combine the salt and derived key
        combined_key = salt + derived_key

        # Encode the combined key using base64 for storage
        encoded_combined_key = base64.urlsafe_b64encode(combined_key)

        return encoded_combined_key

    def verify_master_password(self, master_password, encoded_combined_key):
        combined_key = base64.urlsafe_b64decode(encoded_combined_key)
        salt = combined_key[:self.salt_length]
        derived_key = combined_key[self.salt_length:]

        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=self.key_length,
            salt=salt,
            iterations=self.iterations,
            backend=self.backend
        )

        # Verify the derived key with the provided master password
        try:
            kdf.verify(master_password.encode(), derived_key)
            return True
        except Exception:
            return False


if __name__ == "__main__":
    pm = AppAuthentication()
    master_password = input("Enter a master password: ")

    # Create the master password
    encoded_combined_key = pm.create_master_password(master_password)
    print(f"Encoded combined key: {encoded_combined_key.decode()}")

    # Verify the master password
    verification_password = input("Re-enter the master password for verification: ")
    if pm.verify_master_password(verification_password, encoded_combined_key):
        print("Master password verified successfully!")
    else:
        print("Master password verification failed.")

from cryptography.fernet import Fernet
from typing import Optional

from private import env_dev

class EncryptionUtils:
    def __init__(self, key: bytes = env_dev.shh):
        """Initialize the EncryptionUtils with the provided key."""
        self.fernet = self._get_encryption(key)

    def _get_encryption(self, key: bytes) -> Fernet:
        """Initialize a Fernet object with the provided key."""
        if key:
            try:
                fernet = Fernet(key)
                return fernet
            except ValueError:
                raise ValueError(
                    "Invalid Fernet key: It must be 32 bytes long and base64-encoded."
                )
            except TypeError:
                raise TypeError(
                    "Key type mismatch: Expected bytes but received a different type."
                )
            except Exception as e:
                raise Exception(
                    f"An unexpected error occurred during encryption initialization: {str(e)}"
                )
        raise ValueError("No key provided. Please provide a valid Fernet key.")

    def decrypt_bytes(self, b: bytes, key: Optional[bytes] = None) -> bytes:
        """Decrypt bytes using the provided key or the initialized key."""
        fernet = self.fernet if key is None else self._get_encryption(key)
        return fernet.decrypt(b)

    def decrypt_string(
        self, string: str, encoding: str = "utf-8", key: Optional[bytes] = None
    ) -> str:
        """Decrypt a string using the specified encoding and key."""
        return self.decrypt_bytes(string.encode(encoding), key=key).decode(encoding)

    def get_user_pass(self, user_key: str, user_pass: str) -> str:
        """Get the decrypted user password based on the user key."""
        d_user_key = self.decrypt_bytes(user_key.encode("utf-8"))
        d_user_pass = self.decrypt_string(
            string=user_pass, encoding="utf-8", key=d_user_key
        )
        return d_user_pass


if __name__ == "__main__":
    # For Testing...
    pwd = "gAAAAABm4ZrWCvmQ7xWKQN62SG9u0BVueCDvFObruZkesEnJvhyNlZEK2JTX22OJpFFczVVFpUznSTTeiWlc_dfbqxJhLyZd-Q=="
    user_key = "gAAAAABmmS0Lv3UjqjG6FqFtYWqnSOG8w8UPV76ihnotpYWu2fjyf4MR_RuTniGhz5pjcQOSKKP7I2jMn-hyxa1nFaSpa_bCDMHsrOgRO6BcO_5QHIm0cMtpJCpnP4yjBWMWMaK3ax4v"
    encryption_utils = EncryptionUtils()
    print(encryption_utils.get_user_pass(user_key, user_pass=pwd))

import binascii
import os
import sys
import traceback
from cryptography.fernet import Fernet
from digitalarzengine.utils.crypto import CryptoUtils




# env_path = os.path.join(BASE_DIR, ".env")
# load_dotenv(env_path)
"""
usage: 
    python -m digitalarzengine.manage generate_crypto_key

"""

def encrypt_password(txt: str):
    crypto = CryptoUtils()
    encrypted_txt = crypto.encrypt_txt(txt)
    print(encrypted_txt)


def generate_crypto_key():
    """Generates a Fernet key."""
    key = Fernet.generate_key()
    print(key.decode("utf-8"))


def generate_secret_key_bytes(length: int):
    """
    Generates a cryptographically strong random byte string.
    :param length_bytes: The desired length of the key in bytes.
    """
    val = os.urandom(int(length))
    print(val)


def generate_secret_key_hex(length: int):  # Added type hint for clarity
    """
    Generates a cryptographically strong random secret key as a hex string.
    This is often preferred for readability and easy handling in config files.
    :param length_bytes: The desired length of the key in bytes (must be an integer).
    """
    # Ensure 'length_bytes' is an integer before passing to os.urandom
    val = binascii.hexlify(os.urandom(int(length))).decode('utf-8')
    print(val)


def parse_params(argv):
    """
    Parses CLI args into a dictionary like:
    --app_label auth --database default → {'app_label': 'auth', 'database': 'default'}
    """
    params = {}
    key = None
    for val in argv:
        if key:
            params[key] = val
            key = None
        elif val.startswith("--"):
            key = val[2:]
    return params


def main():
    if len(sys.argv) < 2:
        print("Usage: python manage.py <command> [--key value ...]")
        sys.exit(1)

    command = sys.argv[1]
    params = parse_params(sys.argv[2:])

    # Get function from globals
    func = globals().get(command)
    if not callable(func):
        print(f"Unknown command: {command}")
        sys.exit(1)

    try:
        print(f"Executing command: {command}")
        print(f"With parameters: {params}")
        func(**params)
    except Exception as e:
        print("An error occurred while executing the command:")
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

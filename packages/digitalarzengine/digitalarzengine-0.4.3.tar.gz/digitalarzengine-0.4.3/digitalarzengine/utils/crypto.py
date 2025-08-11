import base64
import os

from cryptography.fernet import Fernet


class CryptoUtils:
    def __init__(self):
        # key = Fernet.generate_key()
        """
            generate key using
            from fernet import Fernet
            Fernet.generate_key().decode("utf-8")
        """
        self.encode_scheme = 'utf-8'
        key = os.getenv('CRYPTO_KEY')
        self.fernet_key = key.encode(self.encode_scheme)

    def decode_base64_urlsafe(self, txt):
        # Add missing padding
        padding_needed = 4 - (len(txt) % 4)
        if padding_needed and padding_needed != 4:
            txt += "=" * padding_needed
        return base64.urlsafe_b64decode(txt)

    def encrypt_txt(self, txt: str, fernet_key=None) -> str:
        fernet_key = self.fernet_key if fernet_key is None else fernet_key
        cipher_suite = Fernet(fernet_key)
        encrypted_bytes = cipher_suite.encrypt(txt.encode(self.encode_scheme))  # returns bytes
        return encrypted_bytes.decode("utf-8")  # save as string

    def decrypt_txt(self, txt: str, fernet_key=None) -> str:
        fernet_key = self.fernet_key if fernet_key is None else fernet_key
        cipher_suite = Fernet(fernet_key)
        return cipher_suite.decrypt(txt.encode("utf-8")).decode("utf-8")


if __name__ == "__main__":
    encode_txt = CryptoUtils().encrypt_txt("da7%6fast1@3map")
    print(encode_txt)
    decode_txt = CryptoUtils().decrypt_txt(encode_txt)
    print(decode_txt)

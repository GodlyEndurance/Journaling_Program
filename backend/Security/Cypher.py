'''
Cypher.py
Manages encryption and decryption operations within the journaling program.
'''
import os
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from argon2.low_level import hash_secret_raw, Type

class Cypher():
    def __init__(self):
        self.NONCE_SIZE = 12  # 12 bytes for AES-GCM nonce
        self.SALT_SIZE = 16  # 16 bytes for salt
        self.KEY_SIZE = 32  # 32 bytes for AES-256 key

    # cypher: AES-256 GCM
    def encrypt(self, plaintext: bytes, key: bytes, aad: bytes | None = None) -> bytes:
        nonce = os.urandom(self.NONCE_SIZE)                      # new nonce every call
        encryptedKey_Tag = AESGCM(key).encrypt(nonce, plaintext, aad)   # encrypted data + tag
        return nonce + encryptedKey_Tag

    def decrypt(self, data: bytes, key: bytes, aad: bytes | None = None) -> bytes:
        nonce = data[:self.NONCE_SIZE]
        encryptedKey_Tag = data[self.NONCE_SIZE:]
        return AESGCM(key).decrypt(nonce, encryptedKey_Tag, aad)

    # Return wrapping key as bytes
    def generateWrappingKey(self, salt, privateKeyPhrase) -> bytes:
        return self.transformPrivateKey(salt, privateKeyPhrase)

    def generateSalt(self) -> bytes: return os.urandom(self.SALT_SIZE)

    def transformPrivateKey(self, salt, privateKeyPhrase) -> bytes:
        return hash_secret_raw(
            secret=privateKeyPhrase.encode("utf-8"),
            salt=salt,
            time_cost=3,          # iterations
            memory_cost=65536,    # 64 MiB, in KiB
            parallelism=4,
            hash_len=self.KEY_SIZE,
            type=Type.ID,         # Argon2id hash function
        )

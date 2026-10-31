'''
Cypher.py
Manages encryption and decryption operations within the journaling program.
'''
import os
import sys
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from argon2.low_level import hash_secret_raw, Type

# config lives in the Journaling package, which has no package/path link to
# Security. Add it to sys.path so TEST_MODE can be checked here too.
_JOURNALING_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "Journaling")
if _JOURNALING_DIR not in sys.path:
    sys.path.insert(0, _JOURNALING_DIR)

import config

class Cypher():
    def __init__(self):
        self.NONCE_SIZE = 12  # 12 bytes for AES-GCM nonce
        self.SALT_SIZE = 16  # 16 bytes for salt
        self.KEY_SIZE = 32  # 32 bytes for AES-256 key

    # cypher: AES-256 GCM library
    # Plaintext/key bytes are never printed, even in TEST_MODE, since this is
    # the exact material encryption exists to protect. Only lengths are logged.
    def encrypt(self, plaintext: bytes, key: bytes, aad: bytes | None = None) -> bytes:
        if (config.TEST_MODE): print(f"\nEncrypting: [{len(plaintext)} bytes of plaintext]")
        nonce = os.urandom(self.NONCE_SIZE)                      # new nonce every call
        encryptedKey_Tag = AESGCM(key).encrypt(nonce, plaintext, aad)   # encrypted data + tag
        result = nonce + encryptedKey_Tag
        if (config.TEST_MODE): print(f"Encryption complete: [{len(result)} bytes of ciphertext]")
        return result

    def decrypt(self, data: bytes, key: bytes, aad: bytes | None = None) -> bytes:
        if (config.TEST_MODE): print(f"\nDecrypting: [{len(data)} bytes of ciphertext]")
        nonce = data[:self.NONCE_SIZE]
        encryptedKey_Tag = data[self.NONCE_SIZE:]
        plaintext = AESGCM(key).decrypt(nonce, encryptedKey_Tag, aad)
        if (config.TEST_MODE): print(f"Decryption complete: [{len(plaintext)} bytes of plaintext]")
        return plaintext

    # Return Public key as bytes
    def generateWrappingKey(self, salt, privateKeyPhrase) -> bytes:
        if (config.TEST_MODE): print(f"\nGenerating wrapping key from passphrase: [redacted] and salt: [{len(salt)} bytes]")
        wrappingKey = self.transformPrivateKey(salt, privateKeyPhrase)
        if (config.TEST_MODE): print(f"Wrapping key generated: [{len(wrappingKey)} bytes]")
        return wrappingKey

    def generateSalt(self) -> bytes:
        salt = os.urandom(self.SALT_SIZE)
        if (config.TEST_MODE): print(f"\nGenerated salt: [{len(salt)} bytes]")
        return salt

    def transformPrivateKey(self, salt, privateKeyPhrase) -> bytes:
        if (config.TEST_MODE): print(f"\nTransforming private key phrase: [redacted] with salt: [{len(salt)} bytes]")
        key = hash_secret_raw(
            secret=privateKeyPhrase.encode("utf-8"),
            salt=salt,
            time_cost=3,          # iterations
            memory_cost=65536,    # 64 MiB, in KiB
            parallelism=4,
            hash_len=self.KEY_SIZE,
            type=Type.ID,         # Argon2id hash function
        )
        if (config.TEST_MODE): print(f"Private key phrase transformed: [{len(key)} bytes]")
        return key


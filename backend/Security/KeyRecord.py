'''
KeyRecord.py

Manages key records within the journaling program.

'''
import os
import sys

from enum import Enum
from datetime import datetime

# config lives in the Journaling package, which has no package/path link to
# Security. Add it to sys.path so TEST_MODE can be checked here too.
_JOURNALING_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "Journaling")
if _JOURNALING_DIR not in sys.path:
    sys.path.insert(0, _JOURNALING_DIR)

import config

class KeyStatus(Enum):
    ACTIVE = "Current"
    RETIRED = "Retired"

class KeyRecord():
    def __init__(self, version: int, salt: bytes, encryptKey: bytes):
        self.keyVersion = version
        self.userID = ""
        self.encryptedKey: bytes = encryptKey
        self.salt: bytes = salt
        self.status = KeyStatus.ACTIVE
        self.createdAt = datetime.now()
        self.retiredAt = None
        # The same dataKey is also wrapped under a one-time recovery code
        # (an independent envelope, same dataKey), so either the passphrase
        # or the recovery code alone can unwrap it. None until a recovery
        # code has actually been generated for this key.
        self.recoverySalt: bytes = None
        self.recoveryEncryptedKey: bytes = None

    def getKeyVersion(self) -> int:
        if (config.TEST_MODE): print(f"\nGetting key version: {self.keyVersion}")
        return self.keyVersion

    def getUserID(self) -> str:
        if (config.TEST_MODE): print(f"\nGetting user ID: {self.userID}")
        return self.userID

    # Wrapped (encrypted) dataKey bytes are not printed, only their length.
    def getEncryptedKey(self) -> bytes:
        if (config.TEST_MODE): print(f"\nGetting encrypted key: [{len(self.encryptedKey)} bytes]")
        return self.encryptedKey

    def getSalt(self) -> bytes:
        if (config.TEST_MODE): print(f"\nGetting salt: [{len(self.salt)} bytes]")
        return self.salt

    def getStatus(self) -> 'KeyStatus':
        if (config.TEST_MODE): print(f"\nGetting status: {self.status}")
        return self.status

    def getCreatedAt(self) -> 'datetime':
        if (config.TEST_MODE): print(f"\nGetting created at: {self.createdAt}")
        return self.createdAt

    def getRetiredAt(self) -> 'datetime':
        if (config.TEST_MODE): print(f"\nGetting retired at: {self.retiredAt}")
        return self.retiredAt

    # Wrapped (encrypted) dataKey bytes are not printed, only their length.
    # Both are None until a recovery code has been generated for this key.
    def getRecoverySalt(self) -> bytes:
        length = len(self.recoverySalt) if self.recoverySalt is not None else 0
        if (config.TEST_MODE): print(f"\nGetting recovery salt: [{length} bytes]" if self.recoverySalt is not None else "\nGetting recovery salt: None (no recovery code set)")
        return self.recoverySalt

    def getRecoveryEncryptedKey(self) -> bytes:
        length = len(self.recoveryEncryptedKey) if self.recoveryEncryptedKey is not None else 0
        if (config.TEST_MODE): print(f"\nGetting recovery encrypted key: [{length} bytes]" if self.recoveryEncryptedKey is not None else "\nGetting recovery encrypted key: None (no recovery code set)")
        return self.recoveryEncryptedKey

    def setKeyVersion(self, keyVersion: int):
        if (config.TEST_MODE): print(f"\nSetting key version: {keyVersion}")
        self.keyVersion = keyVersion
        if (config.TEST_MODE): print(f"Key version set to: {self.keyVersion}")

    def setUserID(self, userID: str):
        if (config.TEST_MODE): print(f"\nSetting user ID: {userID}")
        self.userID = userID
        if (config.TEST_MODE): print(f"User ID set to: {self.userID}")

    def setEncryptedKey(self, encryptedKey: bytes):
        if (config.TEST_MODE): print(f"\nSetting encrypted key: [{len(encryptedKey)} bytes]")
        self.encryptedKey = encryptedKey
        if (config.TEST_MODE): print(f"Encrypted key set: [{len(self.encryptedKey)} bytes]")

    def setSalt(self, salt: bytes):
        if (config.TEST_MODE): print(f"\nSetting salt: [{len(salt)} bytes]")
        self.salt = salt
        if (config.TEST_MODE): print(f"Salt set: [{len(self.salt)} bytes]")

    def setStatus(self, status: 'KeyStatus'):
        if (config.TEST_MODE): print(f"\nSetting status: {status}")
        self.status = status
        if (config.TEST_MODE): print(f"Status set to: {self.status}")

    def setCreatedAt(self, createdAt: 'datetime'):
        if (config.TEST_MODE): print(f"\nSetting created at: {createdAt}")
        self.createdAt = createdAt
        if (config.TEST_MODE): print(f"Created at set to: {self.createdAt}")

    def setRetiredAt(self, retiredAt: 'datetime'):
        if (config.TEST_MODE): print(f"\nSetting retired at: {retiredAt}")
        self.retiredAt = retiredAt
        if (config.TEST_MODE): print(f"Retired at set to: {self.retiredAt}")

    def setRecoverySalt(self, recoverySalt: bytes):
        length = len(recoverySalt) if recoverySalt is not None else 0
        if (config.TEST_MODE): print(f"\nSetting recovery salt: [{length} bytes]")
        self.recoverySalt = recoverySalt
        if (config.TEST_MODE): print(f"Recovery salt set: [{length} bytes]")

    def setRecoveryEncryptedKey(self, recoveryEncryptedKey: bytes):
        length = len(recoveryEncryptedKey) if recoveryEncryptedKey is not None else 0
        if (config.TEST_MODE): print(f"\nSetting recovery encrypted key: [{length} bytes]")
        self.recoveryEncryptedKey = recoveryEncryptedKey
        if (config.TEST_MODE): print(f"Recovery encrypted key set: [{length} bytes]")


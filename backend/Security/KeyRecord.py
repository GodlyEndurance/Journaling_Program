'''
KeyRecord.py

Manages key records within the journaling program.

'''

from enum import Enum
from datetime import datetime

class KeyStatus(Enum):
    ACTIVE = "Current" = 1
    RETIRED = "Retired" = 2

class KeyRecord():
    def __init__(self, privateKeyPhrase: str, publicKey: str, keyVersion: str, userID: str, wrappedKey: bytes, salt: bytes, kdfParams: str, status: 'KeyStatus', createdAt: 'datetime', retiredAt: 'datetime'):
        self.keyVersion = keyVersion
        self.userID = userID
        self.wrappedKey = wrappedKey
        self.salt = salt
        self.kdfParams = kdfParams
        self.status = status
        self.createdAt = createdAt
        self.retiredAt = retiredAt

    def getPrivateKeyPhrase(self) -> str:
        return self.privateKeyPhrase

    def getPublicKey(self) -> str:
        return self.publicKey

    def getKeyVersion(self) -> str:
        return self.keyVersion

    def getUserID(self) -> str:
        return self.userID

    def getWrappedKey(self) -> bytes:
        return self.wrappedKey

    def getSalt(self) -> bytes:
        return self.salt

    def getKdfParams(self) -> str:
        return self.kdfParams

    def getStatus(self) -> 'KeyStatus':
        return self.status

    def getCreatedAt(self) -> 'datetime':
        return self.createdAt

    def getRetiredAt(self) -> 'datetime':
        return self.retiredAt

    def setPrivateKeyPhrase(self, privateKeyPhrase: str):
        self.privateKeyPhrase = privateKeyPhrase

    def setPublicKey(self, publicKey: str):
        self.publicKey = publicKey

    def setKeyVersion(self, keyVersion: str):
        self.keyVersion = keyVersion

    def setUserID(self, userID: str):
        self.userID = userID

    def setWrappedKey(self, wrappedKey: bytes):
        self.wrappedKey = wrappedKey

    def setSalt(self, salt: bytes):
        self.salt = salt

    def setKdfParams(self, kdfParams: str):
        self.kdfParams = kdfParams

    def setStatus(self, status: 'KeyStatus'):
        self.status = status

    def setCreatedAt(self, createdAt: 'datetime'):
        self.createdAt = createdAt

    def setRetiredAt(self, retiredAt: 'datetime'):
        self.retiredAt = retiredAt
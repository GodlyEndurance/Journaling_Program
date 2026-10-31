
'''
EncryptedFile.py

Represents an encrypted file within the journaling program.
Subclasses File so it satisfies the StorageNode interface that
JournalEntryDatabaseAdapter is documented to persist, while keeping the
plaintext metadata (name, entryType, entryNum, date_modified, isFavorite)
needed for sorting/display without decryption. The plaintext `data`
field is inherited but intentionally left empty here; the encrypted
content lives in `cyphertext` instead.

'''
import os
import sys

# StorageNode (and File) live in the Journaling package, which has no
# package/path link to Security. Add it to sys.path so it can be imported
# without restructuring the project into proper packages.
_JOURNALING_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "Journaling")
if _JOURNALING_DIR not in sys.path:
    sys.path.insert(0, _JOURNALING_DIR)

from StorageNode import File
import config


class EncryptedFile(File):
    def __init__(self):
        super().__init__()
        self.cyphertext: bytes = b''  # Encrypted replacement for the plaintext `data`
        self.keyVersion: int = 0      # Which KeyRecord version wrapped the data key used to encrypt this
        self.creationTime = None

    # Ciphertext bytes are not printed in full, only their length.
    def getCyphertext(self) -> bytes:
        if (config.TEST_MODE): print(f"\nGetting cyphertext: [{len(self.cyphertext)} bytes]")
        return self.cyphertext

    def setCyphertext(self, cyphertext: bytes):
        if (config.TEST_MODE): print(f"\nSetting cyphertext: [{len(cyphertext)} bytes]")
        self.cyphertext = cyphertext
        if (config.TEST_MODE): print(f"Cyphertext set: [{len(self.cyphertext)} bytes]")

    def getKeyVersion(self) -> int:
        if (config.TEST_MODE): print(f"\nGetting key version: {self.keyVersion}")
        return self.keyVersion

    def setKeyVersion(self, keyVersion: int):
        if (config.TEST_MODE): print(f"\nSetting key version: {keyVersion}")
        self.keyVersion = keyVersion
        if (config.TEST_MODE): print(f"Key version set to: {self.keyVersion}")

    def getCreationTime(self):
        if (config.TEST_MODE): print(f"\nGetting creation time: {self.creationTime}")
        return self.creationTime

    def setCreationTime(self, creationTime):
        if (config.TEST_MODE): print(f"\nSetting creation time: {creationTime}")
        self.creationTime = creationTime
        if (config.TEST_MODE): print(f"Creation time set to: {self.creationTime}")


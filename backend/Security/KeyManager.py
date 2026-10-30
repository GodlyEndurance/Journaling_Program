'''
KeyManager.py

Manages encryption keys within the journaling program.
'''
import os

from Cypher import Cypher
from KeyRecord import KeyRecord

class KeyManager():
    def __init__(self):
        self.keys: list[KeyRecord] = []
        self.Cypher = Cypher()

    def getKeyByVersion(self, version: int) -> 'KeyRecord':
        for key in self.keys:
            if key.getKeyVersion() == version:
                return key
        return None

    def getCurrentKeyId(self) -> str:
        if self.keys:
            return self.keys[-1].getKeyVersion()
        return ''

    def rotateKey(self):
        newKey = self.generateKey()
        self.keys.append(newKey)

    def changePassphrase(self, User, newPass: str): User.setPrivateKeyPhrase(newPass)
    
    # A KeyRecord is an attachment onto a file
    # Returns (for keyRecordDB) salt, completeWrappedKey, keyVersion, (for journalDB) encryptedFile
    def encryptFile(self, File, KeyRecord, User) -> bytes:

        # Generate WrappingKey
        salt = self.Cypher.generateSalt()
        wrappingKey = self.Cypher.generateWrappingKey(salt, User.getPrivateKeyPhrase())

        # Generate wrappedKey
        # Wrappedkey stores the nonce and the encrypted data key
        dataKey = self.generateDataKey() 
        wrappedKey = self.Cypher.encrypt(dataKey, wrappingKey)

        # Returns (for keyRecordDB) salt, wrappedKey, keyVersion, (for journalDB) encryptedFile
        return salt, wrappedKey, KeyRecord.getKeyVersion(), self.Cypher.encrypt(File, wrappedKey)

    # Later to do: Ensure that the dataKey for encryption of the files has no duplicate
    def generateDataKey(self) -> bytes: return os.urandom(32)  # 32 bytes for AES-256 key

    # Private
    def generateKey(self) -> KeyRecord():
        pass
    

    
    



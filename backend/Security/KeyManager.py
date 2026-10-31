'''
KeyManager.py

Manages encryption keys within the journaling program.
'''
import os
import sys
import secrets
import hmac
from datetime import datetime

from cryptography.exceptions import InvalidTag

from Cypher import Cypher
from KeyRecord import KeyRecord, KeyStatus
from EncryptedFile import EncryptedFile

# StorageNode/File live in the Journaling package, which has no package/path
# link to Security. Add it to sys.path so File can be imported for use as
# the decrypted return type without restructuring the project into packages.
_JOURNALING_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "Journaling")
if _JOURNALING_DIR not in sys.path:
    sys.path.insert(0, _JOURNALING_DIR)

from StorageNode import File
import config


# Raised when an entry cannot be decrypted (wrong passphrase/key or tampered data).
class CorruptedEntryError(Exception): pass


class SecurityVerificationError(Exception): pass


class KeyManager():
    def __init__(self):
        # KeyRecords are the DataKey holders, each containing a unique (encrypted) data key and its associated metadata
        self.key: KeyRecord = None
        self.previousKey: KeyRecord = None  # implicitly retired by the last generateKeyRecord() call, if any
        self.Cypher = Cypher()

    def getKeyByVersion(self, version: int) -> 'KeyRecord':
        if (config.TEST_MODE): print(f"\nGetting key by version: {version}")
        if self.key and self.key.getKeyVersion() == version:
            return self.key
        return None

    def getCurrentKeyVersion(self) -> int:
        if self.key:
            version = self.key.getKeyVersion()
        else:
            version = 0
        if (config.TEST_MODE): print(f"\nGetting current key version: {version}")
        return version

    # This function is for testing
    def getKeyRecord(self) -> 'KeyRecord':
        if (config.TEST_MODE): print(f"\nGetting key record: {self.key}")
        return self.key
    
    # For the KeyRecord database
    # Later to do: Ensure that the dataKey for encryption of the files has no duplicate
    # For the EncryptionManager usage

    # Reset(Public Key) to encrypt files (requires user's private key)
    # Generates a new KeyRecord containing a unique (encrypted) data key and its associated metadata. 
    # Generating a new key implicitly retires whichever key was previously active (from self.previousKey)
    # Generating a new key (n) <=> Retiring previous key (n-1), iteratively
    # Every existing journal entry (in the journal DB) for the  user is also re-encrypted under the new key here. 
    def generateKeyRecord(self, user, journalDBAdapter=None) -> KeyRecord:
        if (config.TEST_MODE): print(f"\n====== KeyManager.generateKeyRecord ======")

        userPrivateKeyPhrase = user.getPrivateKeyPhrase()
        dataKey = os.urandom(32)  # 32 bytes for AES-256 key

        # encryptKey = wrappedKey = Encrypt(wrappingKey, dataKey) + tag + nonce
        salt, encryptKey = self.encryptDataKey(self._asStr(userPrivateKeyPhrase), dataKey)
        version = 1 if self.key is None else self.key.getKeyVersion() + 1

        # Version is continuous, incrementing from the previous key if it exists.
        # Retiring it is implicit in generating a new one.
        self.previousKey = self.key
        if self.previousKey:
            if (config.TEST_MODE): print(f"Retiring previous key version: {self.previousKey.getKeyVersion()}")
            self.previousKey.setStatus(KeyStatus.RETIRED)

        self.key = KeyRecord(version, salt, encryptKey)
        if (config.TEST_MODE): print(f"Generated new key record, version: {self.key.getKeyVersion()}")

        # Re-encrypt existing journal entries under the new key, if requested
        # and there was actually a previous key to rotate away from.
        if self.previousKey is not None and journalDBAdapter is not None:
            oldDataKey = self.unwrapDataKey(self.previousKey, userPrivateKeyPhrase)
            # dataKey (the new key's plaintext data key) is already in hand --
            # no need to unwrap self.key right after just having wrapped it.

            entries = journalDBAdapter.getAll(user.getUserID()) or []
            if (config.TEST_MODE): print(f"Re-encrypting {len(entries)} journal entries from key version {self.previousKey.getKeyVersion()} to {self.key.getKeyVersion()}")
            for entry in entries:
                try:
                    plaintext = self.Cypher.decrypt(entry.getCyphertext(), oldDataKey)
                except InvalidTag:
                    if (config.TEST_MODE): print(f"Failed to re-encrypt entry: {entry.getName()} (corrupted or wrong key)")
                    if (config.TEST_MODE): print(f"====== End KeyManager.generateKeyRecord ======\n")
                    raise CorruptedEntryError()

                entry.setCyphertext(self.Cypher.encrypt(plaintext, dataKey))
                entry.setKeyVersion(self.key.getKeyVersion())
                journalDBAdapter.update(entry)
            if (config.TEST_MODE): print(f"Re-encryption complete.")

        if (config.TEST_MODE): print(f"====== End KeyManager.generateKeyRecord ======\n")
        return self.key

    # CASE 1: See EncryptionManager for the corresponding usage scenarios and recovery paths.
    # Re-wraps the current key's dataKey under a wrapping key derived from the new passphrase. 
    def changePassphrase(self, user, oldPassphrase, newPassphrase, candidateAnswers: dict = None):
        if (config.TEST_MODE): print(f"\n====== KeyManager.changePassphrase ======")
        if (config.TEST_MODE): print(f"Changing passphrase for user: {user.getUserID()}")

        if user.getSecurityQuestions() and not self.verifySecurityAnswers(user, candidateAnswers or {}):
            if (config.TEST_MODE): print("Security question verification failed.")
            if (config.TEST_MODE): print(f"====== End KeyManager.changePassphrase ======\n")
            raise SecurityVerificationError()

        if self.key is not None:
            dataKey = self.unwrapDataKey(self.key, oldPassphrase)
            newSalt, newEncryptedKey = self.encryptDataKey(self._asStr(newPassphrase), dataKey)
            self.key.setSalt(newSalt)
            self.key.setEncryptedKey(newEncryptedKey)
            if (config.TEST_MODE): print(f"Re-wrapped dataKey for key version: {self.key.getKeyVersion()}")

        user.setPrivateKeyPhrase(newPassphrase)
        if (config.TEST_MODE): print(f"Passphrase changed for user: {user.getUserID()}")
        if (config.TEST_MODE): print(f"====== End KeyManager.changePassphrase ======\n")
        return self.key

    # CASE 1.A+: Security question verification. See EncryptionManager for the corresponding usage scenarios and recovery paths.
    # Verifies a full set of candidate answers against the user's stored
    # security-question hashes (constant-time compare). If the user never
    # configured any security questions, this gate is simply not in effect.
    # All configured questions must be answered correctly.
    def verifySecurityAnswers(self, user, candidateAnswers: dict) -> bool:
        storedQuestions = user.getSecurityQuestions()
        for question, record in storedQuestions.items():
            candidate = candidateAnswers.get(question)
            if candidate is None:
                return False
            candidateHash = self.hashSecurityAnswer(candidate, record["salt"])
            if not hmac.compare_digest(candidateHash, record["answerHash"]):
                return False
        return True
    
    # CASE 1.B+: Recovery code (master key) setup. See EncryptionManager for the corresponding usage scenarios and recovery paths.
    # Generates a brand-new, high-entropy, one-time recovery code and wraps
    # the same dataKey (public key) under it
    # Returns the updated KeyRecord (to persist) and the plaintext code (to display once).
    def generateMasterKey(self, user):
        if (config.TEST_MODE): print(f"\n====== KeyManager.generateMasterKey ======")
        if (config.TEST_MODE): print(f"Generating recovery code for user: {user.getUserID()}")

        if self.key is None:
            if (config.TEST_MODE): print("No key exists yet; generate a key before attaching a recovery code.")
            if (config.TEST_MODE): print(f"====== End KeyManager.generateMasterKey ======\n")
            raise CorruptedEntryError()

        dataKey = self.unwrapDataKey(self.key, user.getPrivateKeyPhrase())
        recoveryCode = secrets.token_urlsafe(16)  # ~128 bits of entropy
        recoverySalt, recoveryEncryptedKey = self.encryptDataKey(recoveryCode, dataKey)
        self.key.setRecoverySalt(recoverySalt)
        self.key.setRecoveryEncryptedKey(recoveryEncryptedKey)

        if (config.TEST_MODE): print(f"Recovery code generated for key version: {self.key.getKeyVersion()} [code redacted]")
        if (config.TEST_MODE): print(f"====== End KeyManager.generateMasterKey ======\n")
        return self.key, recoveryCode

    # CASE 2: See EncryptionManager.recoverWithCode for the corresponding usage scenario.
    # Recovers access using the one-time recovery code when the passphrase is lost
    # Returns the updated KeyRecord so the caller can persist it.
    def recoverWithMasterKey(self, user, recoveryCode, newPassphrase) -> KeyRecord:
        if (config.TEST_MODE): print(f"\n====== KeyManager.recoverWithMasterKey ======")
        if (config.TEST_MODE): print(f"Recovering access via recovery code for user: {user.getUserID()}")

        if self.key is None:
            if (config.TEST_MODE): print("No key exists to recover.")
            if (config.TEST_MODE): print(f"====== End KeyManager.recoverWithMasterKey ======\n")
            raise CorruptedEntryError()

        dataKey = self.unwrapDataKeyWithRecoveryCode(self.key, recoveryCode)

        newSalt, newEncryptedKey = self.encryptDataKey(self._asStr(newPassphrase), dataKey)
        self.key.setSalt(newSalt)
        self.key.setEncryptedKey(newEncryptedKey)

        # One-time use: invalidate the consumed recovery code.
        self.key.setRecoverySalt(None)
        self.key.setRecoveryEncryptedKey(None)

        user.setPrivateKeyPhrase(newPassphrase)
        if (config.TEST_MODE): print(f"Access recovered and passphrase reset for user: {user.getUserID()}")
        if (config.TEST_MODE): print(f"====== End KeyManager.recoverWithMasterKey ======\n")
        return self.key


    # CYPHER
    # For the Journal Database
    # For the encryptionManager usage
    # Encrypts only the sensitive content (the journal text) of a File, leaving
    # plaintext metadata (name, entryType, entryNum, isFavorite, date_modified)
    # on the returned EncryptedFile so the storage tree can sort/display it
    # without decryption.
    def encryptFile(self, file, keyRecord: KeyRecord, user) -> EncryptedFile:
        if (config.TEST_MODE): print(f"\n====== KeyManager.encryptFile ======")
        if (config.TEST_MODE): print(f"Encrypting file: {file.getName()} with key version: {keyRecord.getKeyVersion()}")

        dataKey = self.unwrapDataKey(keyRecord, user.getPrivateKeyPhrase())

        encryptedFile = EncryptedFile()
        encryptedFile.setName(file.getName())
        encryptedFile.setEntryType(file.getEntryType())
        encryptedFile.setEntryNum(file.getEntryNum())
        encryptedFile.setFavorite(file.getFavorite())
        encryptedFile.setDateModified(file.getDateModified())
        encryptedFile.setCyphertext(self.Cypher.encrypt(file.getData().encode("utf-8"), dataKey))
        encryptedFile.setKeyVersion(keyRecord.getKeyVersion())
        encryptedFile.setCreationTime(datetime.now())

        if (config.TEST_MODE): print(f"File encrypted: {encryptedFile.getName()}")
        if (config.TEST_MODE): print(f"====== End KeyManager.encryptFile ======\n")
        return encryptedFile
    
    # CYPHER
    # KeyRecord Database will only store KeyRecord() and the UserID for said key.
    # Status indicates for the respective user whether the key is active or retired.
    # Many users will be using the same database, so UserID is necessary to distinguish between different users' keys.
    def decryptFile(self, encryptedFile: EncryptedFile, userPrivateKeyPhrase, keyRecord: KeyRecord) -> File:
        if (config.TEST_MODE): print(f"\n====== KeyManager.decryptFile ======")
        if (config.TEST_MODE): print(f"Decrypting file: {encryptedFile.getName()} with key version: {keyRecord.getKeyVersion()}")

        dataKey = self.unwrapDataKey(keyRecord, userPrivateKeyPhrase)

        # Decrypt the file
        try:
            plaintext = self.Cypher.decrypt(encryptedFile.getCyphertext(), dataKey)
        except InvalidTag:
            if (config.TEST_MODE): print(f"Failed to decrypt file: {encryptedFile.getName()} (wrong passphrase/key or tampered data)")
            if (config.TEST_MODE): print(f"====== End KeyManager.decryptFile ======\n")
            raise CorruptedEntryError()

        file = File()
        file.setName(encryptedFile.getName())
        file.setEntryType(encryptedFile.getEntryType())
        file.setEntryNum(encryptedFile.getEntryNum())
        file.setFavorite(encryptedFile.getFavorite())
        file.setDateModified(encryptedFile.getDateModified())
        file.setData(plaintext.decode("utf-8"))

        if (config.TEST_MODE): print(f"File decrypted: {file.getName()}")
        if (config.TEST_MODE): print(f"====== End KeyManager.decryptFile ======\n")
        return file



    @staticmethod
    def _normalizeAnswer(answer: str) -> str:
        return answer.strip().lower()

    def hashSecurityAnswer(self, answer: str, salt: bytes) -> bytes:
        return self.Cypher.transformPrivateKey(salt, self._normalizeAnswer(answer))


    # PRIVATE
    # Basic construct for KeyRecord and EncryptedFile
    # Returns (for keyRecordDB) salt, wrappedKey
    def encryptDataKey(self, userPrivateKeyPhrase, dataKey: bytes) -> bytes:
        if (config.TEST_MODE): print(f"\nEncrypting dataKey: [{len(dataKey)} bytes]")
        # Generate WrappingKey
        salt = self.Cypher.generateSalt()
        wrappingKey = self.Cypher.generateWrappingKey(salt, self._asStr(userPrivateKeyPhrase))

        # Generate wrappedKey
        # encryptKey = wrappedKey = Encrypt(wrappingKey, dataKey) + tag + nonce
        encryptKey = self.Cypher.encrypt(dataKey, wrappingKey)

        if (config.TEST_MODE): print(f"DataKey encrypted (wrapped): [{len(encryptKey)} bytes]")
        return salt, encryptKey

    # Unwraps the dataKey stored (wrapped) in a KeyRecord using the user's passphrase.
    def unwrapDataKey(self, keyRecord: KeyRecord, userPrivateKeyPhrase) -> bytes:
        if (config.TEST_MODE): print(f"\n====== KeyManager.unwrapDataKey ======")
        if (config.TEST_MODE): print(f"Unwrapping dataKey for key version: {keyRecord.getKeyVersion()}")
        wrappingKey = self.Cypher.generateWrappingKey(keyRecord.getSalt(), self._asStr(userPrivateKeyPhrase))
        try:
            dataKey = self.Cypher.decrypt(keyRecord.getEncryptedKey(), wrappingKey)
        except InvalidTag:
            if (config.TEST_MODE): print(f"Failed to unwrap dataKey: wrong passphrase or corrupted key record.")
            if (config.TEST_MODE): print(f"====== End KeyManager.unwrapDataKey ======\n")
            raise CorruptedEntryError()
        if (config.TEST_MODE): print(f"DataKey unwrapped: [{len(dataKey)} bytes]")
        if (config.TEST_MODE): print(f"====== End KeyManager.unwrapDataKey ======\n")
        return dataKey

    # Unwraps the SAME dataKey via the independent recovery-code envelope
    # instead of the passphrase envelope. Used when the passphrase is lost
    # but the one-time recovery code (saved by the user at generation time)
    # is still available.
    def unwrapDataKeyWithRecoveryCode(self, keyRecord: KeyRecord, recoveryCode) -> bytes:
        if (config.TEST_MODE): print(f"\n====== KeyManager.unwrapDataKeyWithRecoveryCode ======")
        if (config.TEST_MODE): print(f"Unwrapping dataKey via recovery code for key version: {keyRecord.getKeyVersion()}")
        if keyRecord.getRecoverySalt() is None or keyRecord.getRecoveryEncryptedKey() is None:
            if (config.TEST_MODE): print(f"No recovery code was ever generated for this key.")
            if (config.TEST_MODE): print(f"====== End KeyManager.unwrapDataKeyWithRecoveryCode ======\n")
            raise CorruptedEntryError()
        wrappingKey = self.Cypher.generateWrappingKey(keyRecord.getRecoverySalt(), self._asStr(recoveryCode))
        try:
            dataKey = self.Cypher.decrypt(keyRecord.getRecoveryEncryptedKey(), wrappingKey)
        except InvalidTag:
            if (config.TEST_MODE): print(f"Failed to unwrap dataKey: wrong recovery code or corrupted key record.")
            if (config.TEST_MODE): print(f"====== End KeyManager.unwrapDataKeyWithRecoveryCode ======\n")
            raise CorruptedEntryError()
        if (config.TEST_MODE): print(f"DataKey unwrapped via recovery code: [{len(dataKey)} bytes]")
        if (config.TEST_MODE): print(f"====== End KeyManager.unwrapDataKeyWithRecoveryCode ======\n")
        return dataKey

    # Normalize a passphrase to str since Cypher.transformPrivateKey encodes it internally.
    @staticmethod
    def _asStr(phrase) -> str:
        return phrase.decode("utf-8") if isinstance(phrase, bytes) else phrase

'''
EncryptionManager.py
Handles encryption and decryption of data within the journaling program.

'''
import os
import sys

from KeyManager import KeyManager
from EncryptedFile import EncryptedFile

# StorageNode/config live in the Journaling package, which has no
# package/path link to Security. Add it to sys.path so they can be imported
# without restructuring the project into packages.
_JOURNALING_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "Journaling")
if _JOURNALING_DIR not in sys.path:
    sys.path.insert(0, _JOURNALING_DIR)

import config
from StorageNode import File
from Database import JournalEntryDatabaseAdapter, KeyRecordDatabaseAdapter


'''
3 Cases: (for key recovery and encryption management)
Case 1. User remembers their privateKeyPhrase -> Reset(Private key) and still be able to access previous entries
Case 2. User does not remember their privateKeyPhrase but remembers their master keys -> Reset(Private key) and still be able to access previous entries
Case 3. User does not remember either of them -> Reset(Private key) but not be able to access previous entries

'''

class EncryptionManager():
    # journalDBAdapter/keyRecordDBAdapter are injected rather than instantiated
    # here, since DatabaseAdapter subclasses require a real connection string
    # and should be shared/reused rather than recreated on every call.
    def __init__(self, journalDBAdapter: JournalEntryDatabaseAdapter, keyRecordDBAdapter: KeyRecordDatabaseAdapter):
        self.kM = KeyManager()
        self.journalDBAdapter = journalDBAdapter
        self.keyRecordDBAdapter = keyRecordDBAdapter

    # CYPHER
    # RQ: If a file is encrypted, every previous file should be encrypted with the same key version to maintain consistency.
    # This allows the user to decrypt all previous entries easily, without having to manage multiple key versions manually.
    # That is, if you use Encrypt(), you also haveto do updateJDB() to ensure all previous entries are encrypted with the current key version.
    # Encrypt the file to be stored in the Journal DB
    def Encrypt(self, file: File, user):
        if (config.TEST_MODE): print(f"\n====== EncryptionManager.Encrypt ======")
        if self.kM.getKeyRecord() is None:
            # kM gets its "Key" set, to allow for .getKeyRecord() to work correctly.
            self.generateEncryptKey(user)

        # If you are to re-encrypt, first decrypt the file to get its original content.
        # This ensures that if the attacker Eve has access to the user account, 
        # and Eve wants to re-encrypt the file, they will not be able to do so without presenting the information
        # that only the legitimate user can provide, namely the private key phrase.
        if (isinstance(file, EncryptedFile)):
            decryptedFile = self.Decrypt(file, user)
            file = decryptedFile

        encryptedFile = self.kM.encryptFile(file, self.kM.getKeyRecord(), user)
        self.journalDBAdapter.add(encryptedFile)

        if (config.TEST_MODE): print(f"====== End EncryptionManager.Encrypt ======\n")
        return encryptedFile

    # CYPHER
    # Decrypt the file from the Journal DB
    # Precondition: the journalDB has ALL entries re-encrypted with the current key version. That is, updateJDB()
    # should have been called IF generateEncryptKey() is done [generateEncryptKey{} -> updateJDB()->Decrypt()]
    def Decrypt(self, encryptedFile, user) -> File:
        if (config.TEST_MODE): print(f"\n====== EncryptionManager.Decrypt ======")
        keyRecord = self.kM.getKeyByVersion(encryptedFile.getKeyVersion())
        if keyRecord is None:
            keyRecord = self.keyRecordDBAdapter.get(user.getUserID(), encryptedFile.getKeyVersion())

        decryptedFile = self.kM.decryptFile(encryptedFile, user.getPrivateKeyPhrase(), keyRecord)
        if (config.TEST_MODE): print(f"====== End EncryptionManager.Decrypt ======\n")
        return decryptedFile

    # UpdateJournalDB() is removed, in favor of generateKeyRecord() which now handles re-encryption of all journal entries.

    # Reset(Public Key) to encrypt files (requires user's private key)
    # Done when a new encryption key needs to be generated for the user 
    # Triggers all existing journal entries to be re-encrypted under the new key.
    def generateEncryptKey(self, user):
        if (config.TEST_MODE): print(f"\n====== EncryptionManager.generateEncryptKey ======")
        keyRecord = self.kM.generateKeyRecord(user)
        keyRecord.setUserID(user.getUserID())
        self.keyRecordDBAdapter.add(keyRecord)
        if (config.TEST_MODE): print(f"====== End EncryptionManager.generateEncryptKey ======\n")
        return keyRecord


    # CASE 1: Helpdesk still needs to authenticate the user, since the attacker can potentially have access to the device and
    # the private key, but not the authentication credentials of the user. 
    # E.g., Eve uses Bob's physical device and Bob makes the cookies remember the account password, so Eve uses that
    # device to access Bob's account, but does not know Bob's security questions.
    # This is because the user may not remember their recovery code(s), which are needed for the recovery process.
    def knowResetPrivateKey(self, user, oldPassphrase, newPassphrase, candidateAnswers: dict = None):
        if (config.TEST_MODE): print(f"\n====== EncryptionManager.knowResetPrivateKey ======")
        keyRecord = self.kM.changePassphrase(user, oldPassphrase, newPassphrase, candidateAnswers)
        if keyRecord is not None:
            # Persist the re-wrapped key (same keyVersion, new salt/encryptedKey)
            # so KeyRecordDB reflects the passphrase change.
            self.keyRecordDBAdapter.update(keyRecord)
        if (config.TEST_MODE): print(f"====== End EncryptionManager.knowResetPrivateKey ======\n")
        return keyRecord

    # CASE 1.A+
    # Sets up (or replaces) the user's security-question answers for the
    # changePassphrase defense-in-depth gate above. Answers are hashed before
    # storage -- plaintext answers are never persisted. Opt-in: if this is
    # never called, changePassphrase behaves exactly as before (no extra gate).
    def setupSecurityQuestions(self, user, questionAnswers: dict):
        if (config.TEST_MODE): print(f"\n====== EncryptionManager.setupSecurityQuestions ======")
        for question, answer in questionAnswers.items():
            salt = self.kM.Cypher.generateSalt()
            answerHash = self.kM.hashSecurityAnswer(answer, salt)
            user.setSecurityAnswerHash(question, salt, answerHash)
        if (config.TEST_MODE): print(f"====== End EncryptionManager.setupSecurityQuestions ======\n")

    # CASE 1.B+: Recovery code displayed after every change in passphrase
    # Recovery code (master key) setup: Generates this upon request while the user still knows their passphrase, and 
    # the user is responsible for storing it themselves.
    def generateRecoveryCode(self, user):
        if (config.TEST_MODE): print(f"\n====== EncryptionManager.generateRecoveryCode ======")
        keyRecord, recoveryCode = self.kM.generateMasterKey(user)
        self.keyRecordDBAdapter.update(keyRecord)
        if (config.TEST_MODE): print(f"====== End EncryptionManager.generateRecoveryCode ======\n")
        # recoveryCode must be shown to the user exactly once here and never logged/stored.
        return recoveryCode

    # CASE 2: Helpdesk recovery path (using the recovery code)
    # resets the passphrase using the recovery code. One-time use. 
    # Calling recoverWithCode invalidates the recovery code.
    # Note: the recovery code is given upfront to the user, treated as a master key, in case the private key is lost.
    # The user will then use this recovery code to get another privateKeyPhrase.
    def recoverResetPrivateKey(self, user, recoveryCode, newPassphrase):
        if (config.TEST_MODE): print(f"\n====== EncryptionManager.recoverResetPrivateKey ======")
        keyRecord = self.kM.recoverWithMasterKey(user, recoveryCode, newPassphrase)
        self.keyRecordDBAdapter.update(keyRecord)
        if (config.TEST_MODE): print(f"====== End EncryptionManager.recoverResetPrivateKey ======\n")
        return keyRecord

    # CASE 3: Helpdesk recovery (last resort): both the passphrase and master key 
    # are lost, so the old dataKey is unrecoverable. 
    # Wipes the old journal entries/key records and provisions a fresh key under the new passphrase.
    # User will not be able to access previous entries.
    def wipeAndReprovision(self, user, newPassphrase):
        if (config.TEST_MODE): print(f"\n====== EncryptionManager.wipeAndReprovision ======")
        if (config.TEST_MODE): print(f"Wiping old (undecryptable) data and reprovisioning for user: {user.getUserID()}")

        self.journalDBAdapter.deleteAll(user.getUserID())
        self.keyRecordDBAdapter.deleteAll(user.getUserID())
        self.kM.discardKey()

        user.setPrivateKeyPhrase(newPassphrase)
        keyRecord = self.generateEncryptKey(user)
        recoveryCode = self.generateRecoveryCode(user)

        if (config.TEST_MODE): print(f"====== End EncryptionManager.wipeAndReprovision ======\n")
        # recoveryCode must be shown to the user exactly once here and never logged/stored.
        return keyRecord, recoveryCode


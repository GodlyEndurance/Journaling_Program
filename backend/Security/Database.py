'''
Database.py

Manages database interactions within the journaling program.

'''
import os
import sys

# config lives in the Journaling package, which has no package/path link to
# Security. Add it to sys.path so TEST_MODE can be checked here too.
_JOURNALING_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "Journaling")
if _JOURNALING_DIR not in sys.path:
    sys.path.insert(0, _JOURNALING_DIR)

import config


class DatabaseAdapter():
    def __init__(self, connectionString: str):
        self.connectionString = connectionString

    def connect(self):
        raise BaseException("Function to be used within a subclass")

    def disconnect(self):
        raise BaseException("Function to be used within a subclass")

    def add(self):
        raise BaseException("Function to be used within a subclass")

    def get(self):
        raise BaseException("Function to be used within a subclass")

    def getAll(self):
        raise BaseException("Function to be used within a subclass")

    def update(self):
        raise BaseException("Function to be used within a subclass")

    def delete(self):
        raise BaseException("Function to be used within a subclass")

    def deleteAll(self):
        raise BaseException("Function to be used within a subclass")
    

# Stores User() information
class UserDatabaseAdapter(DatabaseAdapter):
    def __init__(self, connectionString: str):
        super().__init__(connectionString)

    def add(self, userID: str, userName: str, email: str):
        # Implement logic to add a user to the database
        if (config.TEST_MODE): print(f"\n[STUB] UserDatabaseAdapter.add called for userID: {userID}")
        pass

    def get(self, userID: str):
        # Implement logic to retrieve a user from the database
        if (config.TEST_MODE): print(f"\n[STUB] UserDatabaseAdapter.get called for userID: {userID}")
        pass

    def update(self, userID: str, userName: str = None, email: str = None):
        # Implement logic to update a user's information in the database
        if (config.TEST_MODE): print(f"\n[STUB] UserDatabaseAdapter.update called for userID: {userID}")
        pass

    def delete(self, userID: str):
        # Implement logic to delete a user from the database
        if (config.TEST_MODE): print(f"\n[STUB] UserDatabaseAdapter.delete called for userID: {userID}")
        pass

# Stores KeyRecord() information
class KeyRecordDatabaseAdapter(DatabaseAdapter):
    def __init__(self, connectionString: str):
        super().__init__(connectionString)

    def add(self, keyRecord: 'KeyRecord'):
        # Implement logic to add a key record to the database
        if (config.TEST_MODE): print(f"\n[STUB] KeyRecordDatabaseAdapter.add called for version: {keyRecord.getKeyVersion()}")
        pass

    def get(self, userID: str, keyVersion: str):
        # Implement logic to retrieve a key record from the database
        if (config.TEST_MODE): print(f"\n[STUB] KeyRecordDatabaseAdapter.get called for userID: {userID}, keyVersion: {keyVersion}")
        pass

    def getAll(self, userID: str):
        # Implement logic to retrieve every key record for a user from the database
        if (config.TEST_MODE): print(f"\n[STUB] KeyRecordDatabaseAdapter.getAll called for userID: {userID}")
        pass

    def update(self, keyRecord: 'KeyRecord'):
        # Implement logic to update a key record in the database
        if (config.TEST_MODE): print(f"\n[STUB] KeyRecordDatabaseAdapter.update called for version: {keyRecord.getKeyVersion()}")
        pass

    def delete(self, userID: str, keyVersion: str):
        # Implement logic to delete a key record from the database
        if (config.TEST_MODE): print(f"\n[STUB] KeyRecordDatabaseAdapter.delete called for userID: {userID}, keyVersion: {keyVersion}")
        pass

    def deleteAll(self, userID: str):
        # Implement logic to delete every key record for a user from the database
        # (used by EncryptionManager.wipeAndReprovision when both the passphrase
        # and the recovery code have been lost -- old keys become permanently
        # useless garbage since nothing can ever unwrap them again).
        if (config.TEST_MODE): print(f"\n[STUB] KeyRecordDatabaseAdapter.deleteAll called for userID: {userID}")
        pass

# Stores StorageNode() information
class JournalEntryDatabaseAdapter(DatabaseAdapter):
    def __init__(self, connectionString: str):
        super().__init__(connectionString)

    def add(self, journalEntry: 'JournalEntry'):
        # Implement logic to add a journal entry to the database
        if (config.TEST_MODE): print(f"\n[STUB] JournalEntryDatabaseAdapter.add called")
        pass

    def getAll(self, userID: str):
        # Implement logic to retrieve all journal entries for a user from the database
        # (used by KeyManager.rotateKey to re-encrypt every entry under a new key)
        if (config.TEST_MODE): print(f"\n[STUB] JournalEntryDatabaseAdapter.getAll called for userID: {userID}")
        pass

    def get(self, userID: str, entryID: str):
        # Implement logic to retrieve a journal entry from the database
        if (config.TEST_MODE): print(f"\n[STUB] JournalEntryDatabaseAdapter.get called for userID: {userID}, entryID: {entryID}")
        pass

    def update(self, journalEntry: 'JournalEntry'):
        # Implement logic to update a journal entry in the database
        if (config.TEST_MODE): print(f"\n[STUB] JournalEntryDatabaseAdapter.update called")
        pass

    def delete(self, userID: str, entryID: str):
        # Implement logic to delete a journal entry from the database
        if (config.TEST_MODE): print(f"\n[STUB] JournalEntryDatabaseAdapter.delete called for userID: {userID}, entryID: {entryID}")
        pass

    def deleteAll(self, userID: str):
        # Implement logic to delete every journal entry for a user from the database
        # (used by EncryptionManager.wipeAndReprovision -- entries encrypted under
        # a key nobody can unwrap anymore are permanently undecryptable garbage,
        # so an honest "lost access" recovery wipes them rather than keeping them around)
        if (config.TEST_MODE): print(f"\n[STUB] JournalEntryDatabaseAdapter.deleteAll called for userID: {userID}")
        pass


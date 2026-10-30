'''
Database.py

Manages database interactions within the journaling program.

'''



class Database():
    def __init__(self, connectionString: str):
        self.connectionString = connectionString

    def connect(self):
        raise BaseException("Function to be used within a subclass")

    def disconnect(self):
        raise BaseException("Function to be used within a subclass")

class UserDatabase(Database):
    def __init__(self, connectionString: str):
        super().__init__(connectionString)

    def addUser(self, userID: str, userName: str, email: str):
        # Implement logic to add a user to the database
        pass

    def getUser(self, userID: str):
        # Implement logic to retrieve a user from the database
        pass

    def updateUser(self, userID: str, userName: str = None, email: str = None):
        # Implement logic to update a user's information in the database
        pass

    def deleteUser(self, userID: str):
        # Implement logic to delete a user from the database
        pass

class KeyRecordDatabase(Database):
    def __init__(self, connectionString: str):
        super().__init__(connectionString)

    def addKeyRecord(self, keyRecord: 'KeyRecord'):
        # Implement logic to add a key record to the database
        pass

    def getKeyRecord(self, userID: str, keyVersion: str):
        # Implement logic to retrieve a key record from the database
        pass

    def updateKeyRecord(self, keyRecord: 'KeyRecord'):
        # Implement logic to update a key record in the database
        pass

    def deleteKeyRecord(self, userID: str, keyVersion: str):
        # Implement logic to delete a key record from the database
        pass

class JournalEntryDatabase(Database):
    def __init__(self, connectionString: str):
        super().__init__(connectionString)

    def addJournalEntry(self, journalEntry: 'JournalEntry'):
        # Implement logic to add a journal entry to the database
        pass

    def getJournalEntry(self, userID: str, entryID: str):
        # Implement logic to retrieve a journal entry from the database
        pass

    def updateJournalEntry(self, journalEntry: 'JournalEntry'):
        # Implement logic to update a journal entry in the database
        pass

    def deleteJournalEntry(self, userID: str, entryID: str):
        # Implement logic to delete a journal entry from the database
        pass
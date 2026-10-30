'''
User.py

Manages user information within the journaling program.

'''


class User():
    def __init__(self, username: str, email: str):
        self.username = username
        self.email = email
        self.privateKeyPhrase = ""
        self.publicKey = ""

    def setPrivateKeyPhrase(self, phrase: str):
        self.privateKeyPhrase = phrase

    def setPublicKey(self, key: str):
        self.publicKey = key

    def getPrivateKeyPhrase(self) -> str:
        return self.privateKeyPhrase

    def getPublicKey(self) -> str:
        return self.publicKey

    def getUsername(self) -> str:
        return self.username

    def getEmail(self) -> str:
        return self.email

    def setUsername(self, username: str):
        self.username = username

    def setEmail(self, email: str):
        self.email = email


    
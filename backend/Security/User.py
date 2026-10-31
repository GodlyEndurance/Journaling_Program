'''
User.py

Manages user information within the journaling program.

'''
import os
import sys

# config lives in the Journaling package, which has no package/path link to
# Security. Add it to sys.path so TEST_MODE can be checked here too.
_JOURNALING_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "Journaling")
if _JOURNALING_DIR not in sys.path:
    sys.path.insert(0, _JOURNALING_DIR)

import config


class User():
    def __init__(self, username: str, email: str):
        self.username = username
        self.email = email
        self.privateKeyPhrase = ""      # Asymmetric key (with the corresponding public key (dataKey))
        self.password = ""
        self.userID = ""  # Unique identifier for the user
        # question -> {"salt": bytes, "answerHash": bytes}. Empty until the
        # user opts in via EncryptionManager.setupSecurityQuestions.
        self.securityQuestions: dict = {}

    # Secrets (passphrase/password) are never printed, even in TEST_MODE.
    def setPrivateKeyPhrase(self, phrase: str):
        if (config.TEST_MODE): print(f"\nSetting private key phrase: [redacted, {len(phrase)} chars]")
        self.privateKeyPhrase = phrase
        if (config.TEST_MODE): print(f"Private key phrase set: [redacted, {len(self.privateKeyPhrase)} chars]")

    def getPrivateKeyPhrase(self) -> str:
        if (config.TEST_MODE): print(f"\nGetting private key phrase: [redacted, {len(self.privateKeyPhrase)} chars]")
        return self.privateKeyPhrase

    def getUsername(self) -> str:
        if (config.TEST_MODE): print(f"\nGetting username: {self.username}")
        return self.username

    def getUserID(self) -> str:
        if (config.TEST_MODE): print(f"\nGetting user ID: {self.userID}")
        return self.userID

    def getEmail(self) -> str:
        if (config.TEST_MODE): print(f"\nGetting email: {self.email}")
        return self.email

    def setUsername(self, username: str):
        if (config.TEST_MODE): print(f"\nSetting username: {username}")
        self.username = username
        if (config.TEST_MODE): print(f"Username set to: {self.username}")

    def setUserID(self, userID: str):
        if (config.TEST_MODE): print(f"\nSetting user ID: {userID}")
        self.userID = userID
        if (config.TEST_MODE): print(f"User ID set to: {self.userID}")

    def setEmail(self, email: str):
        if (config.TEST_MODE): print(f"\nSetting email: {email}")
        self.email = email
        if (config.TEST_MODE): print(f"Email set to: {self.email}")

    def setPassword(self, password: str):
        if (config.TEST_MODE): print(f"\nSetting password: [redacted, {len(password)} chars]")
        self.password = password
        if (config.TEST_MODE): print(f"Password set: [redacted, {len(self.password)} chars]")

    def getPassword(self) -> str:
        if (config.TEST_MODE): print(f"\nGetting password: [redacted, {len(self.password)} chars]")
        return self.password

    # Answer hashes are not printed, only question text and hash/salt length.
    def setSecurityAnswerHash(self, question: str, salt: bytes, answerHash: bytes):
        if (config.TEST_MODE): print(f"\nSetting security answer hash for question: {question!r} [hash redacted, {len(answerHash)} bytes]")
        self.securityQuestions[question] = {"salt": salt, "answerHash": answerHash}
        if (config.TEST_MODE): print(f"Security answer hash set for question: {question!r}")

    def getSecurityQuestions(self) -> dict:
        if (config.TEST_MODE): print(f"\nGetting security questions: {list(self.securityQuestions.keys())}")
        return self.securityQuestions

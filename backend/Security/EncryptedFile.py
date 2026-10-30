
'''
EncryptedFile.py

Represents an encrypted file within the journaling program.

'''


class EncryptedFile():
    def __init__(self):
        self.cyphertext: bytes = b''
        self.keyVersion = 0
        self.creationTime = None
        self.fileName = None

        
        
    
    
    

'''
test_unit.py

The test_* is the syntax for pytest.
Covers the Security section: KeyRecord, EncryptedFile, Cypher, KeyManager, User.

'''
import os
import copy

import pytest
from cryptography.exceptions import InvalidTag

from KeyRecord import KeyRecord, KeyStatus
from EncryptedFile import EncryptedFile
from Cypher import Cypher
from KeyManager import KeyManager, CorruptedEntryError, SecurityVerificationError
from Database import DatabaseAdapter
from EncryptionManager import EncryptionManager
from User import User
from StorageNode import File, StorageNode, EntryType

# TODO:
# - Database Adapters
# - EncryptionManager using fake adapters and testing key rotation to Journal DB and decryption with retired keys

# ---- Helpers ----

def make_user(phrase="correct horse battery staple", user_id="user-1"):
    user = User("alice", "alice@example.com")
    user.setUserID(user_id)
    user.setPrivateKeyPhrase(phrase)
    return user

def make_file(name="2026-10-30", data="Today's entry.", favorite=False):
    file = File()
    file.setName(name)
    file.setEntryType(EntryType.D)
    file.setEntryNum(1)
    file.setData(data)
    file.setFavorite(favorite)
    file.setDateModified(name)
    return file

class FakeJournalDBAdapter:
    # Minimal in-memory stand-in for JournalEntryDatabaseAdapter, used to test
    # rotateKey and EncryptionManager.Encrypt. Method names follow the
    # DatabaseAdapter contract (add/get/getAll/update/delete/deleteAll).
    def __init__(self):
        self.entries = []

    def add(self, journalEntry):
        self.entries.append(journalEntry)

    def getAll(self, userID):
        return self.entries

    def update(self, entry):
        pass  # entries are mutated in place by KeyManager.rotateKey

    def deleteAll(self, userID):
        self.entries = []

class FakeKeyRecordDBAdapter:
    # Minimal in-memory stand-in for KeyRecordDatabaseAdapter, keyed by key
    # version, used to test EncryptionManager (where a retired key may need
    # to be looked back up to decrypt an older entry). Stores deep copies
    # (like a real DB round-trip would) so tests can catch a missing
    # update() call instead of silently passing via object identity. Method
    # names follow the DatabaseAdapter contract (add/get/getAll/update/delete/deleteAll).
    def __init__(self):
        self.records = {}

    def add(self, keyRecord):
        self.records[keyRecord.getKeyVersion()] = copy.deepcopy(keyRecord)

    def get(self, userID, keyVersion):
        return self.records.get(keyVersion)

    def update(self, keyRecord):
        self.records[keyRecord.getKeyVersion()] = copy.deepcopy(keyRecord)

    def deleteAll(self, userID):
        self.records = {}


# KeyRecord tests

def test_KeyStatus_values():
    assert KeyStatus.ACTIVE.value == "Current"
    assert KeyStatus.RETIRED.value == "Retired"

def test_KeyRecord_init_defaults_to_active():
    record = KeyRecord(1, b"salt", b"wrapped-key")
    assert record.getKeyVersion() == 1
    assert record.getSalt() == b"salt"
    assert record.getEncryptedKey() == b"wrapped-key"
    assert record.getStatus() == KeyStatus.ACTIVE

def test_KeyRecord_setters():
    record = KeyRecord(1, b"salt", b"wrapped-key")
    record.setKeyVersion(2)
    record.setUserID("user-1")
    record.setStatus(KeyStatus.RETIRED)
    assert record.getKeyVersion() == 2
    assert record.getUserID() == "user-1"
    assert record.getStatus() == KeyStatus.RETIRED

## Edge Cases

# Database tests


## Edge Cases

def test_DatabaseAdapter_requires_connection_string():
    with pytest.raises(TypeError):
        DatabaseAdapter()

def test_DatabaseAdapter_base_methods_are_abstract():
    adapter = DatabaseAdapter("fake-connection-string")
    with pytest.raises(BaseException):
        adapter.connect()
    with pytest.raises(BaseException):
        adapter.disconnect()


# Cypher tests

def test_Cypher_encrypt_decrypt_roundtrip():
    cypher = Cypher()
    key = os.urandom(32)
    plaintext = b"super secret data"

    cyphertext = cypher.encrypt(plaintext, key)

    assert cyphertext != plaintext
    assert cypher.decrypt(cyphertext, key) == plaintext

def test_Cypher_generateWrappingKey_is_deterministic_for_same_salt_and_phrase():
    cypher = Cypher()
    salt = cypher.generateSalt()

    key1 = cypher.generateWrappingKey(salt, "my passphrase")
    key2 = cypher.generateWrappingKey(salt, "my passphrase")

    assert key1 == key2

def test_Cypher_generateWrappingKey_differs_for_different_passphrase():
    cypher = Cypher()
    salt = cypher.generateSalt()

    key1 = cypher.generateWrappingKey(salt, "passphrase one")
    key2 = cypher.generateWrappingKey(salt, "passphrase two")

    assert key1 != key2

## Edge Cases

def test_Cypher_decrypt_wrong_key_raises_InvalidTag():
    cypher = Cypher()
    key = os.urandom(32)
    wrongKey = os.urandom(32)
    ciphertext = cypher.encrypt(b"secret", key)

    with pytest.raises(InvalidTag):
        cypher.decrypt(ciphertext, wrongKey)

# KeyManager tests

def test_generateKeyRecord_first_key_is_version_1_and_active():
    keyManager = KeyManager()
    user = make_user()

    record = keyManager.generateKeyRecord(user)

    assert record.getKeyVersion() == 1
    assert record.getStatus() == KeyStatus.ACTIVE
    assert keyManager.getKeyRecord() is record

def test_generateKeyRecord_increments_version_and_retires_previous():
    keyManager = KeyManager()
    user = make_user()

    first = keyManager.generateKeyRecord(user)
    second = keyManager.generateKeyRecord(user)

    assert second.getKeyVersion() == first.getKeyVersion() + 1
    assert first.getStatus() == KeyStatus.RETIRED
    assert second.getStatus() == KeyStatus.ACTIVE
    assert keyManager.getKeyRecord() is second

def test_getKeyByVersion_returns_current_key_only():
    keyManager = KeyManager()
    user = make_user()
    record = keyManager.generateKeyRecord(user)

    assert keyManager.getKeyByVersion(record.getKeyVersion()) is record
    assert keyManager.getKeyByVersion(record.getKeyVersion() + 1) is None

def test_changePassphrase_updates_user():
    keyManager = KeyManager()
    user = make_user(phrase="old passphrase")

    keyManager.changePassphrase(user, "old passphrase", "new passphrase")

    assert user.getPrivateKeyPhrase() == "new passphrase"

def test_changePassphrase_with_no_existing_key_just_sets_passphrase():
    keyManager = KeyManager()
    user = make_user(phrase="old passphrase")

    result = keyManager.changePassphrase(user, "old passphrase", "new passphrase")

    assert result is None  # nothing to re-wrap yet
    assert user.getPrivateKeyPhrase() == "new passphrase"

def test_changePassphrase_rewraps_key_without_rekeying_or_touching_entries():
    # Changing the passphrase should re-wrap the SAME dataKey (new salt +
    # encryptedKey under the new passphrase) rather than generating a new
    # dataKey -- so the key version never changes and no journal entries
    # need to be re-encrypted.
    keyManager = KeyManager()
    user = make_user(phrase="old passphrase")
    original = keyManager.generateKeyRecord(user)
    originalSalt = original.getSalt()
    originalEncryptedKey = original.getEncryptedKey()

    updated = keyManager.changePassphrase(user, "old passphrase", "new passphrase")

    assert updated is original  # same KeyRecord object, same key version
    assert updated.getKeyVersion() == original.getKeyVersion()
    assert updated.getSalt() != originalSalt
    assert updated.getEncryptedKey() != originalEncryptedKey

def test_changePassphrase_wrong_old_passphrase_raises_CorruptedEntryError():
    keyManager = KeyManager()
    user = make_user(phrase="old passphrase")
    keyManager.generateKeyRecord(user)

    with pytest.raises(CorruptedEntryError):
        keyManager.changePassphrase(user, "wrong passphrase", "new passphrase")

    # Nothing should have changed: user's passphrase stays the old one.
    assert user.getPrivateKeyPhrase() == "old passphrase"

def test_changePassphrase_then_decryptFile_with_new_passphrase_still_works():
    keyManager = KeyManager()
    user = make_user(phrase="old passphrase")
    keyManager.generateKeyRecord(user)
    file = make_file(data="entry encrypted before passphrase change")

    encrypted = keyManager.encryptFile(file, keyManager.getKeyRecord(), user)

    keyManager.changePassphrase(user, "old passphrase", "new passphrase")

    decrypted = keyManager.decryptFile(encrypted, user.getPrivateKeyPhrase(), keyManager.getKeyRecord())
    assert decrypted.getData() == "entry encrypted before passphrase change"

def test_changePassphrase_with_no_security_questions_configured_skips_the_gate():
    # Opt-in: if the user never set up security questions, changePassphrase
    # behaves exactly as before -- passing None/empty answers is fine.
    keyManager = KeyManager()
    user = make_user(phrase="old passphrase")
    keyManager.generateKeyRecord(user)

    keyManager.changePassphrase(user, "old passphrase", "new passphrase")

    assert user.getPrivateKeyPhrase() == "new passphrase"

def test_verifySecurityAnswers_matches_correct_answers_case_and_whitespace_insensitive():
    keyManager = KeyManager()
    user = make_user()
    salt = keyManager.Cypher.generateSalt()
    user.setSecurityAnswerHash("What is your pet's name?", salt, keyManager.hashSecurityAnswer("Fluffy", salt))

    assert keyManager.verifySecurityAnswers(user, {"What is your pet's name?": "  fluffy  "})

def test_changePassphrase_with_security_questions_requires_correct_answers():
    keyManager = KeyManager()
    user = make_user(phrase="old passphrase")
    keyManager.generateKeyRecord(user)
    salt = keyManager.Cypher.generateSalt()
    user.setSecurityAnswerHash("What is your pet's name?", salt, keyManager.hashSecurityAnswer("Fluffy", salt))

    keyManager.changePassphrase(user, "old passphrase", "new passphrase",
                                 {"What is your pet's name?": "Fluffy"})

    assert user.getPrivateKeyPhrase() == "new passphrase"

def test_encryptFile_produces_EncryptedFile_with_plaintext_metadata_and_ciphertext():
    keyManager = KeyManager()
    user = make_user()
    keyManager.generateKeyRecord(user)
    file = make_file(data="my private journal entry", favorite=True)

    encrypted = keyManager.encryptFile(file, keyManager.getKeyRecord(), user)

    assert isinstance(encrypted, EncryptedFile)
    assert encrypted.getName() == file.getName()
    assert encrypted.getFavorite() == file.getFavorite()
    assert encrypted.getDateModified() == file.getDateModified()
    assert encrypted.getKeyVersion() == keyManager.getKeyRecord().getKeyVersion()
    assert encrypted.getCyphertext() != b""
    assert b"my private journal entry" not in encrypted.getCyphertext()

def test_encryptFile_then_decryptFile_roundtrip_restores_original_data():
    keyManager = KeyManager()
    user = make_user()
    keyManager.generateKeyRecord(user)
    file = make_file(data="round trip content")

    encrypted = keyManager.encryptFile(file, keyManager.getKeyRecord(), user)
    decrypted = keyManager.decryptFile(encrypted, user.getPrivateKeyPhrase(), keyManager.getKeyRecord())

    assert decrypted.getData() == file.getData()
    assert decrypted.getName() == file.getName()
    assert decrypted.getEntryType() == file.getEntryType()
    assert decrypted.getEntryNum() == file.getEntryNum()

def test_rotateKey_reencrypts_all_entries_under_new_key():
    keyManager = KeyManager()
    user = make_user()
    keyManager.generateKeyRecord(user)
    file = make_file(data="entry encrypted under key v1")
    encrypted = keyManager.encryptFile(file, keyManager.getKeyRecord(), user)
    assert encrypted.getKeyVersion() == 1

    adapter = FakeJournalDBAdapter()
    adapter.entries.append(encrypted)

    # "Rotating" is just generating a key while one already exists, with a
    # journalDBAdapter given so existing entries get re-encrypted too.
    newRecord = keyManager.generateKeyRecord(user, adapter)
    oldRecord = keyManager.previousKey

    assert newRecord.getKeyVersion() == 2
    assert encrypted.getKeyVersion() == 2  # entry re-keyed in place
    assert oldRecord.getKeyVersion() == 1
    assert oldRecord.getStatus() == KeyStatus.RETIRED

    decrypted = keyManager.decryptFile(encrypted, user.getPrivateKeyPhrase(), keyManager.getKeyRecord())
    assert decrypted.getData() == "entry encrypted under key v1"

def test_IdenticalFile_afterCypher():
    keyManager = KeyManager()
    user = make_user()

    keyManager.generateKeyRecord(user)
    file = make_file(data="identical content")

    encrypted1 = keyManager.encryptFile(file, keyManager.getKeyRecord(), user)
    encrypted2 = keyManager.encryptFile(file, keyManager.getKeyRecord(), user)

    decrypted1 = keyManager.decryptFile(encrypted1, user.getPrivateKeyPhrase(), keyManager.getKeyRecord())
    decrypted2 = keyManager.decryptFile(encrypted2, user.getPrivateKeyPhrase(), keyManager.getKeyRecord())

    assert decrypted1.getData() == decrypted2.getData() == "identical content"
    assert file.getData() == decrypted1.getData() == decrypted2.getData()

def test_generateRecoveryCode_can_unwrap_and_decrypt_without_the_passphrase():
    keyManager = KeyManager()
    user = make_user(phrase="original passphrase")
    keyManager.generateKeyRecord(user)
    file = make_file(data="entry readable via recovery code")
    encrypted = keyManager.encryptFile(file, keyManager.getKeyRecord(), user)

    keyRecord, recoveryCode = keyManager.generateMasterKey(user)

    assert isinstance(recoveryCode, str)
    assert len(recoveryCode) > 0
    # The recovery code alone (no passphrase at all) can unwrap the dataKey.
    dataKeyViaRecovery = keyManager.unwrapDataKeyWithRecoveryCode(keyRecord, recoveryCode)
    dataKeyViaPassphrase = keyManager.unwrapDataKey(keyRecord, user.getPrivateKeyPhrase())
    assert dataKeyViaRecovery == dataKeyViaPassphrase

def test_recoverWithCode_resets_passphrase_and_journal_entries_still_decrypt():
    keyManager = KeyManager()
    user = make_user(phrase="forgotten passphrase")
    keyManager.generateKeyRecord(user)
    file = make_file(data="entry from before the passphrase was forgotten")
    encrypted = keyManager.encryptFile(file, keyManager.getKeyRecord(), user)
    _, recoveryCode = keyManager.generateMasterKey(user)

    oldKeyVersion = keyManager.getKeyRecord().getKeyVersion()
    keyManager.recoverWithMasterKey(user, recoveryCode, "brand new passphrase")

    assert user.getPrivateKeyPhrase() == "brand new passphrase"
    assert keyManager.getKeyRecord().getKeyVersion() == oldKeyVersion  # re-wrapped in place, not rotated

    decrypted = keyManager.decryptFile(encrypted, user.getPrivateKeyPhrase(), keyManager.getKeyRecord())
    assert decrypted.getData() == "entry from before the passphrase was forgotten"

## Edge Cases

def test_getCurrentKeyVersion_defaults_to_zero_before_any_key():
    keyManager = KeyManager()
    assert keyManager.getCurrentKeyVersion() == 0

def test_decryptFile_wrong_passphrase_raises_CorruptedEntryError():
    keyManager = KeyManager()
    user = make_user()
    keyManager.generateKeyRecord(user)
    file = make_file(data="sensitive")

    encrypted = keyManager.encryptFile(file, keyManager.getKeyRecord(), user)

    with pytest.raises(CorruptedEntryError):
        keyManager.decryptFile(encrypted, "wrong passphrase", keyManager.getKeyRecord())

def test_decryptFile_tampered_ciphertext_raises_CorruptedEntryError():
    keyManager = KeyManager()
    user = make_user()
    keyManager.generateKeyRecord(user)
    file = make_file(data="sensitive")

    encrypted = keyManager.encryptFile(file, keyManager.getKeyRecord(), user)
    tampered = bytearray(encrypted.getCyphertext())
    tampered[-1] ^= 0xFF  # flip a bit to invalidate the AES-GCM auth tag
    encrypted.setCyphertext(bytes(tampered))

    with pytest.raises(CorruptedEntryError):
        keyManager.decryptFile(encrypted, user.getPrivateKeyPhrase(), keyManager.getKeyRecord())

def test_rotateKey_with_no_previous_key_just_generates_first_key():
    keyManager = KeyManager()
    user = make_user()
    adapter = FakeJournalDBAdapter()

    record = keyManager.generateKeyRecord(user, adapter)
    oldRecord = keyManager.previousKey

    assert record.getKeyVersion() == 1
    assert oldRecord is None  # nothing existed to retire
    assert adapter.entries == []

def test_generateRecoveryCode_without_an_existing_key_raises_CorruptedEntryError():
    keyManager = KeyManager()
    user = make_user()

    with pytest.raises(CorruptedEntryError):
        keyManager.generateMasterKey(user)

def test_recoverWithCode_without_a_recovery_code_ever_generated_raises_CorruptedEntryError():
    keyManager = KeyManager()
    user = make_user()
    keyManager.generateKeyRecord(user)

    with pytest.raises(CorruptedEntryError):
        keyManager.recoverWithMasterKey(user, "some code nobody ever generated", "new passphrase")

def test_recoverWithCode_wrong_code_raises_CorruptedEntryError():
    keyManager = KeyManager()
    user = make_user()
    keyManager.generateKeyRecord(user)
    keyManager.generateMasterKey(user)

    with pytest.raises(CorruptedEntryError):
        keyManager.recoverWithMasterKey(user, "definitely the wrong code", "new passphrase")

    # Nothing should have changed on a failed recovery attempt.
    assert user.getPrivateKeyPhrase() != "new passphrase"

def test_recoverWithCode_invalidates_the_consumed_code_one_time_use():
    keyManager = KeyManager()
    user = make_user()
    keyManager.generateKeyRecord(user)
    _, recoveryCode = keyManager.generateMasterKey(user)

    keyManager.recoverWithMasterKey(user, recoveryCode, "new passphrase")

    # The same code cannot be reused a second time.
    with pytest.raises(CorruptedEntryError):
        keyManager.recoverWithMasterKey(user, recoveryCode, "yet another passphrase")

def test_changePassphrase_wrong_security_answer_raises_SecurityVerificationError():
    keyManager = KeyManager()
    user = make_user(phrase="old passphrase")
    keyManager.generateKeyRecord(user)
    salt = keyManager.Cypher.generateSalt()
    user.setSecurityAnswerHash("What is your pet's name?", salt, keyManager.hashSecurityAnswer("Fluffy", salt))

    with pytest.raises(SecurityVerificationError):
        keyManager.changePassphrase(user, "old passphrase", "new passphrase",
                                     {"What is your pet's name?": "wrong answer"})

    # Nothing should have changed on a failed gate -- not even the passphrase.
    assert user.getPrivateKeyPhrase() == "old passphrase"

def test_changePassphrase_missing_security_answer_raises_SecurityVerificationError():
    keyManager = KeyManager()
    user = make_user(phrase="old passphrase")
    keyManager.generateKeyRecord(user)
    salt = keyManager.Cypher.generateSalt()
    user.setSecurityAnswerHash("What is your pet's name?", salt, keyManager.hashSecurityAnswer("Fluffy", salt))

    with pytest.raises(SecurityVerificationError):
        keyManager.changePassphrase(user, "old passphrase", "new passphrase")  # no answers at all

# EncryptedFile tests


def test_EncryptedFile_is_a_File_and_StorageNode():
    encryptedFile = EncryptedFile()
    assert isinstance(encryptedFile, File)
    assert isinstance(encryptedFile, StorageNode)

def test_EncryptedFile_fields():
    encryptedFile = EncryptedFile()
    encryptedFile.setName("2026-10-30")
    encryptedFile.setCyphertext(b"\x01\x02\x03")
    encryptedFile.setKeyVersion(2)

    assert encryptedFile.getName() == "2026-10-30"
    assert encryptedFile.getCyphertext() == b"\x01\x02\x03"
    assert encryptedFile.getKeyVersion() == 2
    assert encryptedFile.getData() == ""  # plaintext data is never populated on EncryptedFile

## Edge Cases

def test_EncryptedFile_has_no_redundant_fileName_field():
    encryptedFile = EncryptedFile()
    assert not hasattr(encryptedFile, "fileName")  # name/getName() already cover this

# EncryptionManager tests

def test_EncryptionManager_encrypt():
    journalAdapter = FakeJournalDBAdapter()
    keyRecordAdapter = FakeKeyRecordDBAdapter()
    encryptionManager = EncryptionManager(journalAdapter, keyRecordAdapter)
    user = make_user()
    file = make_file(data="my private journal entry")

    encryptedFile = encryptionManager.Encrypt(file, user)

    assert isinstance(encryptedFile, EncryptedFile)
    assert encryptedFile in journalAdapter.entries  # persisted to the journal DB
    assert b"my private journal entry" not in encryptedFile.getCyphertext()
    # The key used to encrypt should also have been persisted, for later decryption.
    assert keyRecordAdapter.get(user.getUserID(), encryptedFile.getKeyVersion()) is not None

def test_Encrypt_does_not_rotate_key_on_every_call():
    # Encrypt() should reuse the current persistent key for every new entry
    # rather than rotating (and re-encrypting every past entry) on each call --
    # the "same key version across all entries" invariant holds for free since
    # the key only ever changes via an explicit updateJDB() rotation.
    journalAdapter = FakeJournalDBAdapter()
    keyRecordAdapter = FakeKeyRecordDBAdapter()
    encryptionManager = EncryptionManager(journalAdapter, keyRecordAdapter)
    user = make_user()

    first = encryptionManager.Encrypt(make_file(data="entry one"), user)
    second = encryptionManager.Encrypt(make_file(data="entry two"), user)
    third = encryptionManager.Encrypt(make_file(data="entry three"), user)

    assert first.getKeyVersion() == second.getKeyVersion() == third.getKeyVersion()

def test_Encrypt_on_an_already_EncryptedFile_decrypts_first():
    # Passing an already-EncryptedFile back into Encrypt() (e.g. re-saving an
    # edited entry) must decrypt it first rather than blindly re-encrypting
    # its (empty) plaintext `data`, which would silently destroy the content.
    journalAdapter = FakeJournalDBAdapter()
    keyRecordAdapter = FakeKeyRecordDBAdapter()
    encryptionManager = EncryptionManager(journalAdapter, keyRecordAdapter)
    user = make_user()

    encryptedFile = encryptionManager.Encrypt(make_file(data="original content"), user)

    reEncryptedFile = encryptionManager.Encrypt(encryptedFile, user)

    decrypted = encryptionManager.Decrypt(reEncryptedFile, user)
    assert decrypted.getData() == "original content"

def test_EncryptionManager_decrypt():
    journalAdapter = FakeJournalDBAdapter()
    keyRecordAdapter = FakeKeyRecordDBAdapter()
    encryptionManager = EncryptionManager(journalAdapter, keyRecordAdapter)
    user = make_user()
    file = make_file(data="round trip via EncryptionManager")

    encryptedFile = encryptionManager.Encrypt(file, user)
    decryptedFile = encryptionManager.Decrypt(encryptedFile, user)

    assert decryptedFile.getData() == file.getData()
    assert decryptedFile.getName() == file.getName()

def test_UpdateJournalFiles():
    journalAdapter = FakeJournalDBAdapter()
    keyRecordAdapter = FakeKeyRecordDBAdapter()
    encryptionManager = EncryptionManager(journalAdapter, keyRecordAdapter)
    user = make_user()
    file = make_file(data="entry encrypted before rotation")

    encryptedFile = encryptionManager.Encrypt(file, user)
    oldKeyVersion = encryptedFile.getKeyVersion()

    newKeyRecord = encryptionManager.updateJDB(user)

    assert newKeyRecord.getKeyVersion() == oldKeyVersion + 1
    assert encryptedFile.getKeyVersion() == newKeyRecord.getKeyVersion()  # re-encrypted in place
    persistedRecord = keyRecordAdapter.get(user.getUserID(), newKeyRecord.getKeyVersion())
    assert persistedRecord is not None
    assert persistedRecord.getKeyVersion() == newKeyRecord.getKeyVersion()

    # The old key stays in KeyRecordDB (not deleted) but its RETIRED status
    # must be persisted too, so it can't be mistaken for still-active.
    oldPersistedRecord = keyRecordAdapter.get(user.getUserID(), oldKeyVersion)
    assert oldPersistedRecord is not None
    assert oldPersistedRecord.getStatus() == KeyStatus.RETIRED

    # The entry should still decrypt correctly after rotation.
    decryptedFile = encryptionManager.Decrypt(encryptedFile, user)
    assert decryptedFile.getData() == "entry encrypted before rotation"

def test_changePassphrase():
    journalAdapter = FakeJournalDBAdapter()
    keyRecordAdapter = FakeKeyRecordDBAdapter()
    encryptionManager = EncryptionManager(journalAdapter, keyRecordAdapter)
    user = make_user(phrase="old passphrase")
    file = make_file(data="entry encrypted before passphrase change")
    encryptedFile = encryptionManager.Encrypt(file, user)
    oldKeyVersion = encryptedFile.getKeyVersion()
    oldPersistedSalt = keyRecordAdapter.get(user.getUserID(), oldKeyVersion).getSalt()

    encryptionManager.changePassphrase(user, "old passphrase", "new passphrase")

    assert user.getPrivateKeyPhrase() == "new passphrase"
    # Passphrase change re-wraps in place -- same key version, no re-encryption needed.
    assert encryptedFile.getKeyVersion() == oldKeyVersion

    # KeyRecordDB should reflect the re-wrapped key (new persisted salt), and
    # decryption with the new passphrase should still work.
    persistedRecord = keyRecordAdapter.get(user.getUserID(), oldKeyVersion)
    assert persistedRecord.getSalt() != oldPersistedSalt
    decryptedFile = encryptionManager.Decrypt(encryptedFile, user)
    assert decryptedFile.getData() == "entry encrypted before passphrase change"

def test_setupSecurityQuestions_gates_changePassphrase():
    # Simulates: Eve has Bob's device/session and knows the passphrase (e.g.
    # saved in the browser), but doesn't know Bob's security answers.
    journalAdapter = FakeJournalDBAdapter()
    keyRecordAdapter = FakeKeyRecordDBAdapter()
    encryptionManager = EncryptionManager(journalAdapter, keyRecordAdapter)
    user = make_user(phrase="old passphrase")
    encryptionManager.generateEncryptKey(user)
    encryptionManager.setupSecurityQuestions(user, {"What is your pet's name?": "Fluffy"})

    # Eve knows the real passphrase but not the security answer -- blocked.
    with pytest.raises(SecurityVerificationError):
        encryptionManager.changePassphrase(user, "old passphrase", "eve's new passphrase",
                                            {"What is your pet's name?": "wrong answer"})
    assert user.getPrivateKeyPhrase() == "old passphrase"  # unchanged

    # Bob knows both -- succeeds.
    encryptionManager.changePassphrase(user, "old passphrase", "bob's new passphrase",
                                        {"What is your pet's name?": "Fluffy"})
    assert user.getPrivateKeyPhrase() == "bob's new passphrase"

def test_GenerateEncryptKey():
    journalAdapter = FakeJournalDBAdapter()
    keyRecordAdapter = FakeKeyRecordDBAdapter()
    encryptionManager = EncryptionManager(journalAdapter, keyRecordAdapter)
    user = make_user()

    keyRecord = encryptionManager.generateEncryptKey(user)

    assert keyRecord.getKeyVersion() == 1
    assert keyRecord.getUserID() == user.getUserID()
    persistedRecord = keyRecordAdapter.get(user.getUserID(), keyRecord.getKeyVersion())
    assert persistedRecord is not None
    assert persistedRecord.getKeyVersion() == keyRecord.getKeyVersion()

def test_EncryptionManager_generateRecoveryCode_persists_to_KeyRecordDB():
    journalAdapter = FakeJournalDBAdapter()
    keyRecordAdapter = FakeKeyRecordDBAdapter()
    encryptionManager = EncryptionManager(journalAdapter, keyRecordAdapter)
    user = make_user()
    encryptionManager.generateEncryptKey(user)

    recoveryCode = encryptionManager.generateRecoveryCode(user)

    assert isinstance(recoveryCode, str) and len(recoveryCode) > 0
    persistedRecord = keyRecordAdapter.get(user.getUserID(), encryptionManager.kM.getKeyRecord().getKeyVersion())
    assert persistedRecord.getRecoverySalt() is not None
    assert persistedRecord.getRecoveryEncryptedKey() is not None

def test_EncryptionManager_recoverWithCode_full_helpdesk_flow():
    # Simulates: user forgets their passphrase, but still has their saved
    # one-time recovery code. Support confirms identity out-of-band and the
    # app calls recoverWithCode -- old entries remain decryptable afterward.
    journalAdapter = FakeJournalDBAdapter()
    keyRecordAdapter = FakeKeyRecordDBAdapter()
    encryptionManager = EncryptionManager(journalAdapter, keyRecordAdapter)
    user = make_user(phrase="forgotten passphrase")
    file = make_file(data="entry written before the passphrase was forgotten")
    encryptedFile = encryptionManager.Encrypt(file, user)
    recoveryCode = encryptionManager.generateRecoveryCode(user)

    encryptionManager.recoverWithCode(user, recoveryCode, "brand new passphrase")

    assert user.getPrivateKeyPhrase() == "brand new passphrase"
    decryptedFile = encryptionManager.Decrypt(encryptedFile, user)
    assert decryptedFile.getData() == "entry written before the passphrase was forgotten"

def test_EncryptionManager_wipeAndReprovision_last_resort_when_both_lost():
    # Simulates: both the passphrase AND the recovery code are lost. Old
    # entries are unrecoverable by definition and get wiped; the user ends up
    # with a fresh, working keypair (and a fresh recovery code) afterward.
    journalAdapter = FakeJournalDBAdapter()
    keyRecordAdapter = FakeKeyRecordDBAdapter()
    encryptionManager = EncryptionManager(journalAdapter, keyRecordAdapter)
    user = make_user(phrase="hopelessly forgotten passphrase")
    oldEntry = encryptionManager.Encrypt(make_file(data="old entry, now unrecoverable"), user)
    oldKeyVersion = oldEntry.getKeyVersion()
    oldPersistedSalt = keyRecordAdapter.get(user.getUserID(), oldKeyVersion).getSalt()

    newKeyRecord, newRecoveryCode = encryptionManager.wipeAndReprovision(user, "fresh new passphrase")

    assert user.getPrivateKeyPhrase() == "fresh new passphrase"
    assert journalAdapter.entries == []  # old (undecryptable) entries wiped
    assert isinstance(newRecoveryCode, str) and len(newRecoveryCode) > 0

    # Note: versioning restarts at 1 after a wipe (discardKey() clears the
    # in-memory key), so the new key's version number may coincide with the
    # deleted old one -- what matters is the key MATERIAL is genuinely new.
    newPersistedRecord = keyRecordAdapter.get(user.getUserID(), newKeyRecord.getKeyVersion())
    assert newPersistedRecord is not None
    assert newPersistedRecord.getSalt() != oldPersistedSalt

    # The user can immediately journal again under the fresh key.
    newEntry = encryptionManager.Encrypt(make_file(data="new entry after reprovisioning"), user)
    decrypted = encryptionManager.Decrypt(newEntry, user)
    assert decrypted.getData() == "new entry after reprovisioning"

## Edge Cases

def test_EncryptionManager_decrypt_after_key_rotation_without_cached_key_uses_persisted_record():
    # Simulates decrypting in a fresh session (new KeyManager/EncryptionManager)
    # where the entry's original key is no longer cached in memory and must be
    # looked up from the keyRecordDBAdapter instead.
    journalAdapter = FakeJournalDBAdapter()
    keyRecordAdapter = FakeKeyRecordDBAdapter()
    user = make_user()

    firstManager = EncryptionManager(journalAdapter, keyRecordAdapter)
    file = make_file(data="entry from an earlier session")
    encryptedFile = firstManager.Encrypt(file, user)

    secondManager = EncryptionManager(journalAdapter, keyRecordAdapter)
    decryptedFile = secondManager.Decrypt(encryptedFile, user)

    assert decryptedFile.getData() == "entry from an earlier session"

def test_EncryptionManager_decrypt_wrong_passphrase_raises_CorruptedEntryError():
    journalAdapter = FakeJournalDBAdapter()
    keyRecordAdapter = FakeKeyRecordDBAdapter()
    encryptionManager = EncryptionManager(journalAdapter, keyRecordAdapter)
    user = make_user()
    file = make_file(data="sensitive")

    encryptedFile = encryptionManager.Encrypt(file, user)

    wrongUser = make_user(phrase="wrong passphrase", user_id=user.getUserID())
    with pytest.raises(CorruptedEntryError):
        encryptionManager.Decrypt(encryptedFile, wrongUser)

def test_EncryptionManager_recoverWithCode_wrong_code_raises_CorruptedEntryError():
    journalAdapter = FakeJournalDBAdapter()
    keyRecordAdapter = FakeKeyRecordDBAdapter()
    encryptionManager = EncryptionManager(journalAdapter, keyRecordAdapter)
    user = make_user(phrase="forgotten passphrase")
    encryptionManager.generateEncryptKey(user)
    encryptionManager.generateRecoveryCode(user)

    with pytest.raises(CorruptedEntryError):
        encryptionManager.recoverWithCode(user, "not the real recovery code", "new passphrase")

# User tests

def test_User_getters_setters():
    user = User("alice", "alice@example.com")
    user.setUserID("user-1")
    user.setPrivateKeyPhrase("my passphrase")
    user.setPassword("hunter2")

    assert user.getUsername() == "alice"
    assert user.getEmail() == "alice@example.com"
    assert user.getUserID() == "user-1"
    assert user.getPrivateKeyPhrase() == "my passphrase"
    assert user.getPassword() == "hunter2"

## Edge Cases

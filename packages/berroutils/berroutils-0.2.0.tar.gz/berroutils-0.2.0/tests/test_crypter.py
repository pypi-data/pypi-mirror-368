from berroutils.crypter import Crypter

example_data = {"task": "encryption", "size": 42}


def test_generate_key_salt():
    """Check if key & salt are generated in the correct foramt"""
    mykey, mysalt = Crypter.generate_key_salt_from_password(password="my_password")

    assert isinstance(mykey, str)
    assert len(mykey) == 44
    assert isinstance(mysalt, str)
    assert len(mysalt) == 24


def test_en_decrypt_json(crypter):
    example_token = crypter.encrypt_json(json_data=example_data)
    result = crypter.decrypt_to_json(token=example_token)

    assert result == example_data


def test_en_decrypt(crypter):
    example_token = crypter.encrypt(data="A simple string for testing")
    result = crypter.decrypt(token=example_token)

    assert result == "A simple string for testing"


def test_decryption_from_pass_salt(crypter):
    example_token = crypter.encrypt_json(json_data=example_data)

    # password = "my_password"
    mysalt = 'jVRgK4mCjM3z3lP3dECzYg=='
    crypter_2 = Crypter.from_password_salt(password="my_password", salt=mysalt)
    result = crypter_2.decrypt_to_json(token=example_token)

    assert result == example_data

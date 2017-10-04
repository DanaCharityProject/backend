from app import validators

def test_is_valid_password():
    # Meets all requirements
    assert validators.is_valid_password("Xs2dfkj$")
    # Too short
    assert not validators.is_valid_password("Xs2fkj$")
    # Missing special character
    assert not validators.is_valid_password("Xs2dfkjd")
    # Missing number
    assert not validators.is_valid_password("Xsxdfkj$")
    # Missing letter
    assert not validators.is_valid_password("2345678$")


def test_is_valid_email():
    # Good email
    assert validators.is_valid_email("email@gmail.ca")
    # Missing @
    assert not validators.is_valid_email("someincorrecte.mail")
    # Too long
    assert not validators.is_valid_email("reallyreallyextremelylongemailtowritedownsomewhere@hotmail.com")
    # Too short
    assert not validators.is_valid_email("a@bd")


def test_is_valid_username():
    # Good username
    assert validators.is_valid_username("abc123")
    # Too short
    assert not validators.is_valid_username("9d")
    # Too long
    assert not validators.is_valid_username("7978ads7fda--dfadgwew324")
    # Special characters
    assert not validators.is_valid_username("&#JLDS*(7/")
    # Not string
    assert not validators.is_valid_username(1)


def test_is_valid_phone_number():
    # Good example
    assert validators.is_valid_phone_number("6475556666")
    # Good example
    assert validators.is_valid_phone_number("4165556666")
    # Good example
    assert validators.is_valid_phone_number("9055556666")
    # Too short
    assert not validators.is_valid_phone_number("416111")
    # Too long
    assert not validators.is_valid_phone_number("41611100000")
    # Invalid area code
    assert not validators.is_valid_phone_number("1234567890")
    # Not string
    assert not validators.is_valid_phone_number(1)



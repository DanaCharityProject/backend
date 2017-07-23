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



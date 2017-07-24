import re
from jsonschema import draft4_format_checker

PASSWORD_RE = re.compile("^(?=.*[A-Za-z])(?=.*\d)(?=.*[$@$!%*#?&])[A-Za-z\d$@$!%*#?&]{8,}$")
EMAIL_RE = re.compile("^([a-zA-Z0-9-])+@([a-zA-Z])+(.[a-zA-Z]+)*(.[a-zA-Z]+)$")
USERNAME_RE = re.compile("^([a-zA-Z0-9-]){4,12}$")
EMAIL_MIN = 5
EMAIL_MAX = 40

@draft4_format_checker.checks('secure_password')
def is_valid_password(val):
    if not isinstance(val, str):
        return False
    return PASSWORD_RE.match(val)


def is_valid_email(email):
    if not isinstance(email, str):
        return False
    if len(email) < EMAIL_MIN:
        return False
    if len(email) > EMAIL_MAX:
        return False
    return EMAIL_RE.match(email) is not None


def is_valid_username(username):
    if not isinstance(username, str):
        return False
    return USERNAME_RE.match(username) is not None


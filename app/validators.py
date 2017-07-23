import re
from jsonschema import draft4_format_checker

PASSWORD_RE = re.compile("^(?=.*[A-Za-z])(?=.*\d)(?=.*[$@$!%*#?&])[A-Za-z\d$@$!%*#?&]{8,}$")

@draft4_format_checker.checks('secure_password')
def is_valid_password(val):
    if not isinstance(val, str):
        return False
    return PASSWORD_RE.match(val)



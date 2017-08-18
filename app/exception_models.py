class NoExistingUser(Exception):
    def __init__(self, message):
        Exception.__init__(self, message)


class InvalidUserInfo(Exception):
    def __init__(self, message):
        Exception.__init__(self, message)

from .exception_models import NoExistingUser, InvalidUserInfo
from .user_model import User
from .validators import is_valid_username

class UserManager():

    @staticmethod
    def edit_user(user_id, new_username):
        user = User.query.get(user_id)
        try:
            if user is None:
                raise NoExistingUser("Something went wrong!")
            if not is_valid_username(new_username):
                raise InvalidUserInfo("User information is invalid.")
            user.username = new_username
        except NoExistingUser:
            raise
        except InvalidUserInfo:
            raise

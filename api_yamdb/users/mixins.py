from users.services import validate_username_value


class UsernameValidationMixin:
    def validate_username(self, username):
        return validate_username_value(username)

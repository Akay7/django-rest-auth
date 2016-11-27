from django.contrib.auth import get_user_model

from oauth2_provider.oauth2_validators import OAuth2Validator


class OAuth2SocialValidator(OAuth2Validator):
    def validate_user(self, username, password, client, request, *args, **kwargs):
        """
        Instead checking username and password correspond to a valid and active User
        we are just find user who is logged in
        """
        # Try find by pk which in password, anyway by pk will be just one element
        u = get_user_model().objects.filter(id=password, username=username).first()
        if u is not None and u.is_active:
            request.user = u
            return True
        return False

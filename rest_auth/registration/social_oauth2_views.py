from django.http import HttpResponse

from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny

from oauth2_provider.ext.rest_framework import OAuth2Authentication
from oauth2_provider.views.mixins import OAuthLibMixin
from oauth2_provider.settings import oauth2_settings

from .serializers import SocialLoginSerializer

from .social_oauth2_validators import OAuth2SocialValidator


class OAuth2SocialLoginView(OAuthLibMixin, GenericAPIView):
    permission_classes = (AllowAny,)
    serializer_class = SocialLoginSerializer
    authentication_classes = (OAuth2Authentication,)

    server_class = oauth2_settings.OAUTH2_SERVER_CLASS
    validator_class = OAuth2SocialValidator
    oauthlib_backend_class = oauth2_settings.OAUTH2_BACKEND_CLASS

    def login(self):
        self.user = self.serializer.validated_data['user']
        self.request.data['grant_type'] = 'password'
        self.request.data['password'] = self.user.id
        self.request.data['username'] = self.user.username
        self.oauth_response = self.create_token_response(self.request)

    def get_response(self):
        uri, headers, body, status = self.oauth_response
        response = HttpResponse(content=body, status=status)

        for k, v in headers.items():
            response[k] = v
        return response

    def post(self, request, *args, **kwargs):
        self.request = request
        self.serializer = self.get_serializer(data=self.request.data)
        self.serializer.is_valid(raise_exception=True)
        self.login()
        return self.get_response()

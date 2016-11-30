import json
import base64
import responses
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from .test_social import TestSocialAuth

from oauth2_provider.models import get_application_model, AbstractApplication


class TestSocialOAuth2(TestSocialAuth):
    def setUp(self):
        super(TestSocialOAuth2, self).setUp()

        user = get_user_model().objects.create(username="admin")
        self.app = get_application_model().objects.create(
            name="TestApp", client_type="public",
            authorization_grant_type=AbstractApplication.GRANT_PASSWORD,
            user=user
        )

        resp_body = {
            "id": "123123123123",
            "first_name": "John",
            "gender": "male",
            "last_name": "Smith",
            "link": "https://www.facebook.com/john.smith",
            "locale": "en_US",
            "name": "John Smith",
            "timezone": 2,
            "updated_time": "2014-08-13T10:14:38+0000",
            "username": "john.smith",
            "verified": True
        }

        responses.add(
            responses.GET,
            self.graph_api_url,
            body=json.dumps(resp_body),
            status=200,
            content_type='application/json'
        )
        self.client = APIClient()

    @responses.activate
    def test_can_exchange_access_token_from_social_network_to_oauth2_tokens(self):
        users_count = get_user_model().objects.all().count()
        payload = {
            'access_token': 'abc123'
        }

        token = base64.b64encode(bytes(
            "{}:{}".format(self.app.client_id, self.app.client_secret), 'utf8'
        ))
        auth = {'HTTP_AUTHORIZATION': 'Basic %s' % token.decode('utf8')}

        response = self.client.post(self.fb_login_oauth2_url, payload, **auth)
        self.assertEqual(response.status_code, 200)
        self.assertIn('refresh_token', response.json().keys())
        self.assertIn('access_token', response.json().keys())
        self.assertEqual(get_user_model().objects.all().count(),
                         users_count + 1)

        # make sure that second request will not create a new user
        response = self.client.post(self.fb_login_oauth2_url, payload, **auth)
        self.assertEqual(response.status_code, 200)
        self.assertIn('refresh_token', response.json().keys())
        self.assertIn('access_token', response.json().keys())
        self.assertEqual(get_user_model().objects.all().count(),
                         users_count + 1)

    @responses.activate
    def test_cant_get_token_when_make_request_without_auth_header(self):
        users_count = get_user_model().objects.all().count()
        payload = {'access_token': 'abc123'}

        response = self.client.post(self.fb_login_oauth2_url, payload)
        self.assertEqual(response.status_code, 401)

    @responses.activate
    def test_cant_get_token_when_make_request_with_wrong_auth_header(self):
        users_count = get_user_model().objects.all().count()
        payload = {'access_token': 'abc123'}

        token = base64.b64encode(bytes(
            "{}:{}".format(self.app.client_id, self.app.client_secret), 'utf8'
        ))
        auth = {'HTTP_AUTHORIZATION': 'Basic {}f'.format(token.decode('utf8'))}

        response = self.client.post(self.fb_login_oauth2_url, payload)
        self.assertEqual(response.status_code, 401)

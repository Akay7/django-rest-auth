import json
import responses
from django.contrib.auth import get_user_model
from .test_social import TestSocialAuth


class TestCocialOAuth2(TestSocialAuth):
    @responses.activate
    def test_can_exchange_access_token_from_social_network_to_oauth2_tokens(self):
        # 'name': 'Test',
        # 'client_type': 'confidential',
        # 'authorization_grant_type': 'password',
        # 'client_id': client_id,
        # 'client_secret': client_secret,

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

        users_count = get_user_model().objects.all().count()
        payload = {
            'access_token': 'abc123'
        }

        response = self.post(self.fb_login_oauth2_url, data=payload)
        # response = self.post(self.fb_login_oauth2_url, data=payload, status_code=200)
        self.assertIn('key', self.response.json.keys())
        self.assertEqual(get_user_model().objects.all().count(),
                         users_count + 1)

        # make sure that second request will not create a new user
        self.post(self.fb_login_oauth2_url, data=payload, status_code=200)
        self.assertIn('key', self.response.json.keys())
        self.assertEqual(get_user_model().objects.all().count(),
                         users_count + 1)

    # FixMe: test without token, unsupported grant type
from rest_framework.test import APIClient
from . import base_test

class UserLoginTestCase(base_test.NewUserTestCase):

    def setUp(self) -> None:
        super().setUp()

    def test_user_login_success(self):
        client = APIClient()
        result = client.post('/api/user/login/', {'username': self.username,
                                                  'password': self.password}, format='json')
        self.assertEquals(result.status_code, 200)
        self.assertTrue('access' in result.json())
        self.assertTrue('refresh' in result.json())

    def test_user_login_wrong_password(self):
        client = APIClient()
        result = client.post('/api/user/login/', {'username': self.username,
                                                  'password': '1'}, format='json')
        self.assertEquals(result.status_code, 401)

    def test_get_userlist_by_superuser(self):
        client = APIClient()
        self.user.is_superuser = True
        self.user.save()
        request = client.post('/api/user/login/', {'username': self.user.username,
                                                  'password': self.password}, format='json')
        access_token = request.json()['access']
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        result = client.get('/api/user/', format='json')

        self.assertEquals(result.status_code, 200)

    def test_get_userlist_by_common(self):
        client = APIClient()

        request = client.post('/api/user/login/', {'username': self.user_sec.username,
                                                   'password': self.password}, format='json')
        access_token = request.json()['access']
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        result = client.get('/api/user/', format='json')

        self.assertEquals(result.status_code, 403)
        self.assertEquals(result.json()['status'], 'fail')

    def tearDown(self) -> None:
        self.client.logout()
        super().tearDown()


class LoginTokenVerifyTest(base_test.NewUserTestCase):
    def setUp(self) -> None:
        super().setUp()

    def test_user_login_token_verify(self):
        client = APIClient()
        login_response = client.post('/api/user/login/', {'username': self.username,
                                                  'password': self.password}, format='json')
        token_verify_response = client.post('/api/verify/', {'token': login_response.json()['access']}, format='json')

        self.assertEquals(token_verify_response.status_code, 200)

    def tearDown(self) -> None:
        self.client.logout()
        super().tearDown()
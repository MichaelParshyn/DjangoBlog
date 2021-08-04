from rest_framework.test import APIClient
from . import base_test
from blog_app.models import Log, Account, PostCreator, Post, PostReaction
from blog_app import constants
import pdb

class AccountLogTestCase(base_test.NewUserTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.client = APIClient()
        self.login_response = self.client.post('/api/user/login/', {'username': self.username,
                                               'password': self.password}, format='json')
        self.access_token = self.login_response.json()['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')

    def test_create_account_success(self):
        """
        Checking account creating with correct credentials. Checking logs.
        Expected: account created. Log created. Status 'success'.
        """
        create_account = self.client.post('/api/user/account/', {'username': 'test_username',
                                                                 'user': self.user.id}, format='json')
        self.assertEquals(create_account.status_code, 201)
        self.assertEquals(create_account.json()['status'], 'success')
        self.assertEquals(Log.objects.filter(user=self.user, method='POST', action='/api/user/account/').count(), 1)

    def test_create_account_used_username(self):
        """
        Checking account creating with used username. Checking logs.
        Expected: account not created. Log not created. Status 'fail'.
        """
        self.client.post('/api/user/account/', {'username': 'test_username', 'user': self.user.id}, format='json')
        self.login_response = self.client.post('/api/user/login/', {'username': self.username_sec,
                                                                    'password': self.password}, format='json')
        self.access_token = self.login_response.json()['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        create_account = self.client.post('/api/user/account/', {'username': 'test_username',
                                                                 'user': self.user_sec.id}, format='json')
        self.assertEquals(create_account.status_code, 400)
        self.assertTrue(create_account.json()['username'][0]=='account with this username already exists.')
        self.assertEquals(Log.objects.filter(user=self.user, method='POST', action='/api/user/account/').count(), 1)

    def test_update_account_success(self):
        """
        Checking account updating with correct credentials. Checking logs.
        Expected: account updated. Log created. Status 'success'.
        """
        self.client.post('/api/user/account/', {'username': 'test_username_1', 'user': self.user.id}, format='json')
        acc = Account.objects.filter(user=self.user)[0]
        result = self.client.put(f'/api/user/account/{acc.id}', {'username': 'test_username_2', 'user': self.user.id}, format='json')

        self.assertEquals(result.status_code, 202)
        self.assertEquals(result.json()['status'], 'success')
        self.assertEquals(Account.objects.filter(id=acc.id, username='test_username_2').count(), 1)
        self.assertEquals(Log.objects.filter(user=self.user, method='PUT', action=f'/api/user/account/{acc.id}').count(), 1)

    def test_update_account_non_owner(self):
        """
        Checking account updating by non-owner. Checking logs.
        Expected: account not updated. Log not created. Status 'fail'.
        """
        self.client.post('/api/user/account/', {'username': 'test_username_1', 'user': self.user.id}, format='json')
        acc = Account.objects.filter(user=self.user)[0]
        result = self.client.put(f'/api/user/account/{acc.id}', {'username': 'test_username_2', 'user': self.user_sec.id}, format='json')

        self.login_response = self.client.post('/api/user/login/', {'username': self.username_sec,
                                                                    'password': self.password}, format='json')
        self.access_token = self.login_response.json()['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')

        self.assertEquals(result.status_code, 400)
        self.assertEquals(result.json()['status'], 'fail')
        self.assertEquals(Account.objects.filter(id=acc.id, username='test_username_2').count(), 0)
        self.assertEquals(Log.objects.filter(user=self.user, method='PUT', action=f'/api/user/account/{acc.id}').count(), 0)

    def test_update_account_used_username(self):
        """
        Checking account updating with used username. Checking logs.
        Expected: account not updated. Log not created. Status 'fail'.
        """
        self.client.post('/api/user/account/', {'username': 'test_username_1', 'user': self.user.id}, format='json')
        self.client.post('/api/user/account/', {'username': 'test_username_2', 'user': self.user.id}, format='json')

        acc = Account.objects.filter(user=self.user)[1]
        result = self.client.put(f'/api/user/account/{acc.id}', {'username': 'test_username_1', 'user': self.user.id},
                                 format='json')
        self.assertEquals(result.status_code, 400)
        self.assertEquals(result.json()['status'], 'fail')
        self.assertEquals(Account.objects.filter(id=acc.id, username='test_username_1').count(), 0)
        self.assertEquals(Log.objects.filter(user=self.user, method='PUT', action=f'/api/user/account/{acc.id}').count(), 0)

    def test_delete_account_owner_success(self):
        """
        Checking account deleting with correct credentials. Checking logs.
        Expected: account deleted. Log created. Status 'success'.
        """
        self.client.post('/api/user/account/', {'username': 'test_username_1', 'user': self.user.id}, format='json')
        acc = Account.objects.filter(user=self.user)[0]
        result = self.client.delete(f'/api/user/account/{acc.id}', format='json')

        self.assertEquals(result.status_code, 204)
        self.assertEquals(Account.objects.filter(id=acc.id, user=self.user).count(), 0)
        self.assertEquals(Log.objects.filter(user=self.user, method='DELETE', action=f'/api/user/account/{acc.id}').count(), 1)

    def test_delete_account_superuser_success(self):
        """
        Checking account deleting by superuser. Checking logs.
        Expected: account deleted. Log created. Status 'success'.
        """
        self.client.post('/api/user/account/', {'username': 'test_username_1', 'user': self.user.id}, format='json')
        acc = Account.objects.filter(user=self.user)[0]

        self.login_response = self.client.post('/api/user/login/', {'username': self.username_sec,
                                                                    'password': self.password}, format='json')
        self.access_token = self.login_response.json()['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        self.user_sec.is_superuser = True
        self.user_sec.save()

        result = self.client.delete(f'/api/user/account/{acc.id}', format='json')

        self.assertEquals(result.status_code, 204)
        self.assertEquals(Account.objects.filter(id=acc.id, user=self.user).count(), 0)
        self.assertEquals(Log.objects.filter(user=self.user_sec, method='DELETE', action=f'/api/user/account/{acc.id}').count(), 1)

    def test_delete_account_another(self):
        """
        Checking account deleting by common user. Checking logs.
        Expected: account not deleted. Log not created. Status 'fail'.
        """
        self.client.post('/api/user/account/', {'username': 'test_username_1', 'user': self.user.id}, format='json')
        acc = Account.objects.filter(user=self.user)[0]

        self.login_response = self.client.post('/api/user/login/', {'username': self.username_sec,
                                                                    'password': self.password}, format='json')
        self.access_token = self.login_response.json()['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')

        result = self.client.delete(f'/api/user/account/{acc.id}', format='json')

        self.assertEquals(result.status_code, 400)
        self.assertEquals(result.json()['status'], 'fail')
        self.assertEquals(Account.objects.filter(id=acc.id, user=self.user).count(), 1)
        self.assertEquals(Log.objects.filter(user=self.user, method='DELETE', action=f'/api/user/account/{acc.id}').count(), 0)

    def tearDown(self) -> None:
        self.client.logout()
        super().tearDown()


class PostLogTestCase(base_test.NewUserTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.client = APIClient()
        self.login_response = self.client.post('/api/user/login/', {'username': self.username,
                                                                    'password': self.password}, format='json')
        self.access_token = self.login_response.json()['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        self.client.post('/api/user/account/', {'username': 'test_username',
                                                'user': self.user.id}, format='json')
        self.acc = Account.objects.filter(user=self.user)[0]

    def test_create_post_success(self):
        """
        Checking post creating, PostCreator creating, role in PostCreator. Checking logs.
        Expected: post created successfully, PostCreator object created successfully, author has role "owner", log created.
        """
        result = self.client.post('/api/post/', {'title': 'Head', 'author': self.acc.id}, format='json')

        self.assertEquals(result.status_code, 201)
        self.assertEquals(result.json()['status'], 'success')
        self.assertEquals(PostCreator.objects.filter(account=self.acc, role=constants.ROLE_OWNER).count(), 1)
        self.assertEquals(Log.objects.filter(user=self.user, method='POST', action='/api/post/').count(), 1)

    def test_create_post_empty_title(self):
        """
        Checking post creating, 'PostCreator' creating, role in PostCreator. Checking logs.
        Expected: post not created, PostCreator object not created, log not created.
        """
        result = self.client.post('/api/post/', {'author': self.acc.id}, format='json')

        self.assertEquals(result.status_code, 400)
        self.assertEquals(result.json()['status'], 'fail')
        self.assertEquals(PostCreator.objects.filter(account=self.acc, role=constants.ROLE_OWNER).count(), 0)
        self.assertEquals(Log.objects.filter(user=self.user, method='POST', action='/api/post/').count(), 0)

    def test_update_post_success(self):
        """
        Checking post updating with the correct data. Checking logs.
        Expected: post updated, log not created.
        """
        self.client.post('/api/post/', {'title': 'Head', 'author': self.acc.id}, format='json')
        post = Post.objects.filter(title='Head', author=self.acc.id)[0]
        result = self.client.put(f'/api/post/{post.id}', {'title': 'Header', 'text': 'Some text', 'author': self.acc.id}, format='json')

        self.assertEquals(result.status_code, 202)
        self.assertEquals(result.json()['status'], 'success')
        self.assertEquals(Post.objects.filter(title='Header', text='Some text', author= self.acc.id).count(), 1)
        self.assertEquals(Log.objects.filter(user=self.user, method='PUT', action=f'/api/post/{post.id}').count(), 1)

    def test_update_post_empty_title(self):
        """
        Checking post updating with empty title. Checking logs.
        Expected: post not updated, log not created.
        """
        self.client.post('/api/post/', {'title': 'Head', 'author': self.acc.id}, format='json')
        post = Post.objects.filter(title='Head', author=self.acc.id)[0]
        result = self.client.put(f'/api/post/{post.id}',
                                 {'title': '', 'text': 'Some text', 'author': self.acc.id}, format='json')

        self.assertEquals(result.status_code, 400)
        self.assertEquals(result.json()['status'], 'fail')
        self.assertEquals(Post.objects.filter(title='', text='Some text', author= self.acc.id).count(), 0)
        self.assertEquals(Log.objects.filter(user=self.user, method='PUT', action=f'/api/post/{post.id}').count(), 0)

    def test_delete_post_by_staff(self):
        """
        Checking post deleting with correct data. Checking logs.
        Expected: post deleted, log created, 'PostCreator' deleted.
        """
        self.client.post('/api/post/', {'title': 'Head', 'author': self.acc.id}, format='json')
        post = Post.objects.filter(title='Head', author=self.acc.id)[0]
        result = self.client.delete(f'/api/post/{post.id}', format='json')

        self.assertEquals(result.status_code, 204)
        self.assertEquals(Post.objects.filter(title='Head', author=self.acc.id).count(), 0)
        self.assertEquals(PostCreator.objects.filter(post=post).count(), 0)
        self.assertEquals(Log.objects.filter(user=self.user, method='DELETE', action=f'/api/post/{post.id}').count(), 1)

    def test_delete_post_by_another(self):
        """
        Checking post deleting by non permitted user. Checking logs.
        Expected: post not deleted, log not created.
        """
        author_id = self.acc.id
        self.client.post('/api/post/', {'title': 'Head', 'author': author_id}, format='json')
        post = Post.objects.filter(title='Head', author=self.acc.id)[0]

        self.login_response = self.client.post('/api/user/login/', {'username': self.username_sec,
                                                                    'password': self.password}, format='json')
        self.access_token = self.login_response.json()['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        result = self.client.delete(f'/api/post/{post.id}', format='json')

        self.assertEquals(result.status_code, 403)
        self.assertEquals(Post.objects.filter(title='Head', author=author_id).count(), 1)
        self.assertEquals(PostCreator.objects.filter(post=post).count(), 1)
        self.assertEquals(Log.objects.filter(user=self.user, method='DELETE', action=f'/api/post/{post.id}').count(), 0)

    def tearDown(self) -> None:
        self.client.logout()
        super().tearDown()
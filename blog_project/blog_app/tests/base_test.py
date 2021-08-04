from django.test import TestCase
from django.contrib.auth.models import User
from faker import Faker

class NewUserTestCase(TestCase):
    def setUp(self) -> None:
        faker = Faker()
        self.username = faker.user_name()
        self.password = faker.password()
        self.email = faker.email()
        self.first_name = faker.first_name()
        self.last_name = faker.last_name()
        self.user = User.objects.create_user(username=self.username,
                                             password=self.password,
                                             email=self.email,
                                             first_name=self.first_name,
                                             last_name=self.last_name)

        self.username_sec = faker.user_name()
        self.user_sec = User.objects.create_user(username=self.username_sec,
                                             password=self.password,
                                             email=self.email,
                                             first_name=self.first_name,
                                             last_name=self.last_name)

    def tearDown(self) -> None:
        self.user.delete()
        self.user_sec.delete()

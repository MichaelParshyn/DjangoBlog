from django.db import models
from django.contrib.auth.models import User
from datetime import datetime
from blog_app import constants

class Account(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    username = models.CharField(max_length=20, unique=True, blank=False, null=False)

    def __str__(self):
        return f'@{self.username}'

class Post(models.Model):
    title = models.CharField(max_length=20, blank=False, null=False)
    text = models.TextField()
    author = models.ForeignKey(Account, on_delete=models.CASCADE)
    creation_date = models.DateTimeField(default=datetime.now())
    posting_date = models.DateTimeField()
    deleting_date = models.DateTimeField()

    def __str__(self):
        return f'{self.title} by {self.author}'

class PostReaction(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    reaction = models.CharField(max_length=200, choices=constants.REACTIONS, default=constants.REACTION_NONE)
    time = models.DateTimeField(default=datetime.now())
    pass

class PostCreator(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    role = models.CharField(max_length=200, choices=constants.ROLES, default=constants.ROLE_NONE)

class Log (models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    method = models.CharField(max_length=10, blank=False, null=False)
    action = models.CharField(max_length=100, blank=False, null=False)
    time = models.DateTimeField(default=datetime.now())


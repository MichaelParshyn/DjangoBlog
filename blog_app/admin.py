from django.contrib import admin
from models import Account, PostReaction, Post, PostCreator, Log

class AccountAdmin(admin.ModelAdmin):
    fields = ['username', 'user']
    search_fields = ['username']

class PostReactionAdmin(admin.ModelAdmin):
    fields = ['account', 'post', 'reaction', 'time']
    search_fields = ['account', 'reaction']

class PostCreatorAdmin(admin.ModelAdmin):
    fields = ['post', 'account', 'role']
    search_fields = ['post', 'role']

class PostAdmin(admin.ModelAdmin):
    fields = ['title', 'text', 'author', 'creation_date', 'posting_date', 'deleting_date']
    search_fields = ['title', 'author']

class LogAdmin(admin.ModelAdmin):
    fields = ['account', 'method', 'action', 'time']
    search_fields = ['account', 'method']

admin.site.register(Account, AccountAdmin)
admin.site.register(PostCreator, PostCreatorAdmin)
admin.site.register(PostReaction, PostReactionAdmin)
admin.site.register(Post, PostAdmin)
admin.site.register(Log, LogAdmin)

# Register your models here.

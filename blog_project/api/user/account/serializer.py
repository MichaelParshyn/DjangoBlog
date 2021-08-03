from rest_framework import serializers
from blog_app.models import Account

class AccountSerializer(serializers.ModelSerializer):
    class Meta():
        model = Account
        fields = '__all__'
from rest_framework import serializers
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta():
        model = User
        fields = '__all__'
        username = serializers.CharField()
        first_name = serializers.CharField()
        email = serializers.EmailField()
        password = serializers.CharField()
        is_active = serializers.BooleanField()

from rest_framework.generics import (ListCreateAPIView, RetrieveUpdateDestroyAPIView)
from django.contrib.auth.models import User
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from . import serializer
from blog_app.models import Log
from datetime import datetime

class UserAPI(ListCreateAPIView, RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = serializer.UserSerializer
    permission_classes = (AllowAny,)

    def list(self, request):
        if request.user.is_superuser:
            queryset = self.get_queryset()
            serializ = serializer.UserSerializer(queryset, many=True)
            return Response(serializ.data)
        else:
            return Response({'status':'fail',
                             'message':'You are not permitted to see this page!'}, status=status.HTTP_403_FORBIDDEN)

    def create(self, request, *args, **kwargs):
        user = User.objects.create_user(username=request.data['username'], password=request.data['password'],
                                        is_active = True, *args)
        return Response({'status': 'success',
                         'message': 'User registered!'}, status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if request.user.is_superuser or request.user == instance:
            self.perform_destroy(instance)
            Log.objects.create(user=request.user, method=request.method, action=request.path, time=datetime.now())
            return Response({'status': 'success',
                     'message': 'Deleted successfully!'}, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({'status': 'fail',
                             'message': 'You cannot delete this user!'}, status=status.HTTP_403_FORBIDDEN)
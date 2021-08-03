from rest_framework.generics import (ListCreateAPIView, RetrieveUpdateDestroyAPIView)
from blog_app.models import Account, Log
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from api.user.account import serializer
from datetime import datetime

class AccountAPI(ListCreateAPIView, RetrieveUpdateDestroyAPIView):
    queryset = Account.objects.all()
    serializer_class = serializer.AccountSerializer
    permission_classes = (IsAuthenticated,)

    def create(self, request, *args, **kwargs):
        if (request.user.username == request.data['username']):
            return Response({'status': 'fail',
                            'message': 'User with this username registered! User and account usernames have not be repeated'},
                            status=status.HTTP_400_BAD_REQUEST)
        else:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)

            Log.objects.create(account=Account.objects.get(id=serializer.data['author'], method=request.method,
                                                           action=request.path, time=datetime.now()))
            return Response({'status': 'success',
                         'message': 'Added successfully!',
                         'data': serializer.data}, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        if (request.user.id==request.data['user'] or request.user.is_superuser):
            partial = kwargs.pop('partial', False)
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data, partial=partial)
            print(request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)

            if getattr(instance, '_prefetched_objects_cache', None):
                # If 'prefetch_related' has been applied to a queryset, we need to
                # forcibly invalidate the prefetch cache on the instance.
                instance._prefetched_objects_cache = {}
            Log.objects.create(account=Account.objects.get(id=serializer.data['author'], method=request.method,
                                                           action=request.path, time=datetime.now()))
            return Response({'status': 'success',
                             'message': 'Updated successfully!',
                             'data': serializer.data}, status=status.HTTP_202_ACCEPTED)
        else:
            return Response({'status': 'fail',
                             'message': 'Only owner can update account info!'},
                            status=status.HTTP_400_BAD_REQUEST)


    def destroy(self, request, *args, **kwargs):
        if(request.user.id==request.data['user'] or request.user.is_superuser):
            instance = self.get_object()
            self.perform_destroy(instance)
            Log.objects.create(account=Account.objects.get(id=serializer.data['author'], method=request.method,
                                                           action=request.path, time=datetime.now()))
            return Response({'status': 'success',
                         'message': 'Deleted successfully!'}, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({'status': 'fail',
                             'message': 'Account could be deleted by owner or by superuser!'}, status=status.HTTP_400_BAD_REQUEST)
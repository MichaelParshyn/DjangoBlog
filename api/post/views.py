from rest_framework import status
from rest_framework.generics import (ListCreateAPIView, RetrieveUpdateDestroyAPIView)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import api_view
from blog_app.models import Post, PostCreator, Account, PostReaction, Log
from datetime import datetime, timedelta
from blog_app import constants
from . import serializer
import pdb

class PostAPI(ListCreateAPIView, RetrieveUpdateDestroyAPIView):
    queryset = Post.objects.all()
    serializer_class = serializer.PostSerializer
    permission_classes = (IsAuthenticated,)

    def create(self, request, *args, **kwargs):
        """
        Creating post. Can be created by authenticated user. Automatically gets onwnership.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)

        PostCreator.objects.create(post=Post.objects.get(id=serializer.data['id']),
                                   account=Account.objects.get(id=serializer.data['author']),
                                   role=constants.ROLE_OWNER)

        pdb.set_trace()
        Log.objects.create(account=Account.objects.get(id=serializer.data['author'], method=request.method,
                                                       action=request.path, time=datetime.now()))

        return Response({'status': 'success',
                         'message': 'Added successfully!',
                         'data': serializer.data}, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        """
        Updating post. Can be updated by authenticated user from staff account (owner, admin or editor role)
        """
        if (Account.objects.filter(user = request.user)[0].user!=request.user):
            return Response({'status': 'fail',
                             'message': 'You are triyng to use account which not belongs to you!'},
                            status=status.HTTP_403_FORBIDDEN)
        else:
            instance = self.get_object()
            if (PostCreator.objects.filter(post=instance)[0].account.user!=request.user):
                return Response({'status': 'fail',
                                 'message': 'You are not permitted to edit this post!'},
                                status=status.HTTP_403_FORBIDDEN)
            else:
                partial = kwargs.pop('partial', False)
                serializer = self.get_serializer(instance, data=request.data, partial=partial)
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

    def destroy(self, request, *args, **kwargs):
        """
        Deleting post. Can be deleted by owner or admin
        """
        if (Account.objects.filter(request.user.id==user.id)!=1):
            return Response({'status': 'fail',
                             'message': 'You are triyng to use account which not belongs to you!'},
                            status=status.HTTP_403_FORBIDDEN)
        else:
            if (PostCreator.objects.filter(post.id == request.data.id, account.id == request.data['account'],
                                           (role==constants.ROLE_OWNER or constants.ROLE_ADMIN)) != 1):
                return Response({'status': 'fail',
                                 'message': 'You are not permitted to delete this post!'},
                                status=status.HTTP_403_FORBIDDEN)
            else:
                instance = self.get_object()
                self.perform_destroy(instance)
                Log.objects.create(account=Account.objects.get(id=serializer.data['author'], method=request.method,
                                                               action=request.path, time=datetime.now()))
                return Response({'status': 'success',
                         'message': 'Deleted successfully!'}, status=status.HTTP_204_NO_CONTENT)

    @api_view(['GET'])
    def react(request, *args, **kwargs):
        user = request.user
        post_id = int(request.data['post_id'])
        username = request.data['username']
        reaction = request.data['reaction']

        post = Post.objects.filter(id = post_id)
        if post.count()==0:
            return Response({'status': 'fail',
                             'message': 'Post not found!'}, status=status.HTTP_404_NOT_FOUND)

        acc = Account.objects.filter(username = username)
        if acc.count() == 0:
            return Response({'status': 'fail',
                             'message': 'Account not found!'}, status=status.HTTP_404_NOT_FOUND)
        acc = Account.objects.filter(username = username)

        if (PostCreator.objects.filter(post = post[0], account = acc[0]).count() > 0):
            return Response({'status': 'fail',
                             'message': 'Creators cannot react on their post!'},
                            status=status.HTTP_403_FORBIDDEN)
        if reaction == 'like':
            if (PostReaction.objects.filter(post = post[0], account = acc[0], reaction = constants.REACTION_LIKE).count() > 0):
                return Response({'status': 'fail',
                                 'message': 'You have liked this post!'},
                                status = status.HTTP_403_FORBIDDEN)
            else:
                PostReaction.objects.filter(account = acc[0], post = post[0], reaction = constants.REACTION_DISLIKE).delete()
                PostReaction.objects.create(account = acc[0], post = post[0], reaction = constants.REACTION_LIKE)
                Log.objects.create(account=Account.objects.get(id=serializer.data['author'], method=request.method,
                                                               action=request.path, time=datetime.now()))
                return Response({'status': 'success',
                             'message': 'Post liked!'}, status=status.HTTP_200_OK)
        else:
            if (PostReaction.objects.filter(post = post[0], account = acc[0]).count() > 0):
                return Response({'status': 'fail',
                                 'message': 'You have liked this post!'},
                                status = status.HTTP_403_FORBIDDEN)
            else:
                PostReaction.objects.filter(account = acc[0], post = post[0], reaction = constants.REACTION_LIKE).delete()
                PostReaction.objects.create(account = acc[0], post = post[0], reaction = constants.REACTION_DISLIKE)
                Log.objects.create(account=Account.objects.get(id=serializer.data['author'], method=request.method,
                                                               action=request.path, time=datetime.now()))
                return Response({'status': 'success',
                             'message': 'Post liked!'}, status = status.HTTP_200_OK)

    @api_view(['GET'])
    def get_reaction_stat(request, *args, **kwargs):
        post_id = request.data['post_id']
        datetime_from = datetime.strptime(request.data['datetime_from'], '%Y-%m-%d').date()
        datetime_to = datetime.strptime(request.data['datetime_to'], '%Y-%m-%d').date()
        post = Post.objects.filter(id = post_id)
        current_data = datetime_from
        stat = {}

        if post.count() > 0:
            for i in range((datetime_to-datetime_from).days+1):
                reaction = PostReaction.objects.filter(post=post[0], reaction=constants.REACTION_LIKE,
                                                       time=current_data)
                stat[f'{current_data}'] = reaction.count()
                current_data += timedelta(days=1)

            return Response ({'status': 'true',
                          'message': stat})
        else:
            return Response({'status': 'false',
                             'message': 'Post not fount'}, status = status.HTTP_404_NOT_FOUND)
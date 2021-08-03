from rest_framework.generics import (ListCreateAPIView)
from rest_framework.permissions import AllowAny
from blog_app.models import Log

class LogAPI(ListCreateAPIView):
    queryset = Log.objects.all()
    permission_classes = (AllowAny,)


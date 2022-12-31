from rest_framework import generics
from app.models import User, Message
from app.api.serializers import UserSerializer, MessageSerializer

class UserView(generics.ListCreateAPIView):
  queryset = User.objects.all()
  serializer_class = UserSerializer

class MessageView(generics.ListCreateAPIView):
  queryset = Message.objects.all()
  serializer_class = MessageSerializer
  
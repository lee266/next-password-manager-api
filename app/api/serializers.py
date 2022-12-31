from rest_framework import serializers
from app.models import User, Message

class UserSerializer(serializers.ModelSerializer):
  
  class Meta:
    model = User
    fields = ('id', 'name', 'email', 'password')
    extra_kwargs = {'password': {'write_only': True, 'required': True}}
    
    # def create(self, valudated_date):
    #   user = User.objects.create_user(**valudated_date)
    #   return user

class MessageSerializer(serializers.ModelSerializer):
  class Meta:
    model = Message
    fields = '__all__'
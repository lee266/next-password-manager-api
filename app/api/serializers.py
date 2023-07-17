from rest_framework import serializers
from app.models import User, Message, PasswordManage, Task, Calendar, PasswordCustomField, PasswordGroup, PasswordTag


class UserSerializer(serializers.ModelSerializer):
  class Meta:
    model = User
    fields = ('id', 'username', 'email', 'password')
    extra_kwargs = {'password': {'write_only': True, 'required': True},
                    'email': {'write_only': True, 'required': True}
                    }
    
  def create(self, validated_data):
    user = User.objects.create_user(**validated_data)
    return user

class MessageSerializer(serializers.ModelSerializer):
  created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
  class Meta:
    model = Message
    fields = '__all__'

class PasswordCustomFieldSerializer(serializers.ModelSerializer):
  created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
  
  class Meta:
    model = PasswordCustomField
    fields = '__all__'


class PasswordGroupSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    
    class Meta:
        model = PasswordGroup
        fields = '__all__'


class PasswordTagSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    
    class Meta:
        model = PasswordTag
        fields = '__all__'

class PasswordManageSerializer(serializers.ModelSerializer):
  created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
  group = PasswordGroupSerializer(read_only=True)
  tag = PasswordTagSerializer(read_only=True)
  custom = PasswordCustomFieldSerializer(many=True, read_only=True)
  
  class Meta:
    model = PasswordManage
    fields = '__all__'

class TaskSerializer(serializers.ModelSerializer):
  created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
  
  class Meta:
    model = Task
    fields = '__all__'

class CalendarSerializer(serializers.ModelSerializer):
  class Meta:
    model = Calendar
    fields = '__all__'
    read_only_fields = ('id',)
    

    
  
    
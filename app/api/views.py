from rest_framework import generics, viewsets
from rest_framework.permissions import AllowAny
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from django.http.response import JsonResponse
from app.models import User, Message, PasswordManage, Task, Calendar
from app.api.serializers import UserSerializer, MessageSerializer, PasswordManageSerializer, TaskSerializer, CalendarSerializer

class UserView(generics.ListCreateAPIView):
  queryset = User.objects.all()
  serializer_class = UserSerializer
  permission_classes = (AllowAny,)

class MessageView(generics.ListCreateAPIView):
  queryset = Message.objects.all()
  serializer_class = MessageSerializer
  permission_classes = (AllowAny,)
  
class UserViewSet(viewsets.ModelViewSet):
  queryset = User.objects.all()
  serializer_class = UserSerializer
  permission_classes = (AllowAny,)

class PasswordManageView(generics.ListCreateAPIView):
  queryset = PasswordManage.objects.all()
  serializer_class = PasswordManageSerializer
  permission_classes = (AllowAny,)

class TaskViewSet(viewsets.ModelViewSet):
  queryset = Task.objects.all()
  serializer_class = TaskSerializer
  permission_classes = (AllowAny,)

class CalendarViewSet(viewsets.ModelViewSet):
  queryset = Calendar.objects.all()
  serializer_class = CalendarSerializer
  permission_classes = (AllowAny,)


@api_view(['GET', 'POST'])
def task_list(request):
  if request.method == 'GET':
        Tasks = Task.objects.all()
        serializer = TaskSerializer(Tasks, many=True)
        return JsonResponse(serializer.data)
  elif request.method == 'POST':
      serializer = TaskSerializer(data=request.data)
      if serializer.is_valid():
          serializer.save()
          return Response(serializer.data, status=status.HTTP_201_CREATED)
      return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class TestAppView(APIView):
  permission_classes = (AllowAny,)
  def get(self, request, **kwargs):
    return JsonResponse({ "data": "this is get" })
  def post(self, request, **kwargs):
    return JsonResponse({ "data": "post" })
  def put(self, request, **kwargs):
    return JsonResponse({ "data": "put" })
  def patch(self, request, **kwargs):
    return JsonResponse({ "data": "patch" })
  def delete(self, request, **kwargs):
    return JsonResponse({ "data": "delete" })

  
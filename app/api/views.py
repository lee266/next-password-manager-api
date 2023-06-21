from rest_framework import generics, viewsets, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import api_view, action
from rest_framework.response import Response
from rest_framework.views import APIView
from django.http.response import JsonResponse
from app.models import User, Message, PasswordManage, Task, Calendar, PasswordGroup, PasswordTag, PasswordCustomField
from app.api.serializers import UserSerializer, MessageSerializer, PasswordManageSerializer, TaskSerializer, CalendarSerializer, PasswordCustomFieldSerializer, PasswordGroupSerializer, PasswordTagSerializer


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

class PasswordManageViewSet(viewsets.ModelViewSet):
  serializer_class = PasswordManageSerializer
  queryset = PasswordManage.objects.all()
  model = PasswordManage
  # permission_classes = [IsAuthenticated]
  permission_classes = (AllowAny,)
  
  @action(detail=False, methods=['get'])
  def columns(self):
    serializer = self.get_serializer()
    columns = [field for field in serializer.fields.keys()]
    return Response(columns)
  
  @action(detail=False, methods=['post'])
  def search(self, request):
    print("request",request.data)
    userID = request.data["id"]
    queryset = self.get_queryset().filter(user_id=userID)
    serializer = self.get_serializer(queryset, many=True)
    print("userID:",request.data["id"])
    print("queryset:",queryset)
    print("serializer:",serializer)
    return Response(serializer.data)
  
  @action(detail=False, methods=['post'])
  def get_data(self, request):
    userID = request.data["user_id"]
    queryset = self.model.objects.filter(user_id=userID).select_related('group', 'tag').prefetch_related('custom').order_by('index')
    serializer = self.get_serializer(queryset, many=True)
    # Get a list of all unique group names from the Group model
    group_names = PasswordGroup.objects.filter(user_id=userID).values_list('group_name', flat=True).distinct()
    grouped_data = {group_name: [] for group_name in group_names}
    grouped_data['group'] = []

    for data in serializer.data:
        groupData = data['group']
        if groupData is None:
            group_key = 'group'
        else:
            group_key = groupData["group_name"]
        
        if group_key in grouped_data:
            grouped_data[group_key].append(data)
        else:
            grouped_data[group_key] = [data]

    return Response(grouped_data)

class PasswordGroupViewSet(viewsets.ModelViewSet):
  serializer_class = PasswordGroupSerializer
  queryset = PasswordGroup.objects.all()
  # permission_classes = [IsAuthenticated]
  permission_classes = (AllowAny,)
  model = PasswordGroup
  
  def create(self, request, *args, **kwargs):
      print("request", request.data)
      return super().create(request, *args, **kwargs)

class PasswordTagViewSet(viewsets.ModelViewSet):
  serializer_class = PasswordTagSerializer
  queryset = PasswordTag.objects.all()
  permission_classes = (AllowAny,)
  model = PasswordTag

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

  
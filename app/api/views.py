from rest_framework import generics, viewsets, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import api_view, action
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from django.http.response import JsonResponse
from app.models import User, Message, PasswordManage, Task, Calendar, PasswordGroup, PasswordTag, PasswordCustomField, Inquiry, InquiryCategory
from app.api.serializers import UserSerializer, MessageSerializer, PasswordManageSerializer, TaskSerializer, CalendarSerializer, PasswordCustomFieldSerializer, PasswordGroupSerializer, PasswordTagSerializer, InquiryCategorySerializer, InquirySerializer
from django.db.models import Q


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
  
  def create(self, request, *args, **kwargs):
    user_id = request.data.get('user')
    group_id = request.data.get('group')
    tag_id = request.data.get('tag')
    # custom_ids = request.data.get('custom')

    # Check user_id that is required
    if not user_id:
        return Response({'error': 'User ID is required.'}, status=status.HTTP_400_BAD_REQUEST)
    try:
        user = User.objects.get(id=user_id)
    except ObjectDoesNotExist:
        return Response({'error': f'User ID {user_id} does not exist.'}, status=status.HTTP_400_BAD_REQUEST)
    # Check group and tag. These are able to null
    group = None
    tag = None
    if group_id:
        try: group = PasswordGroup.objects.get(id=group_id)
        except ObjectDoesNotExist:
            return Response({'error': f'Group ID {group_id} does not exist.'}, status=status.HTTP_400_BAD_REQUEST)
    if tag_id:
        try: tag = PasswordTag.objects.get(id=tag_id)
        except ObjectDoesNotExist:
            return Response({'error': f'Tag ID {tag_id} does not exist.'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Compute the index based on the last 'PasswordManage' record for the given group
    if group:
        last_password_manage = PasswordManage.objects.filter(group=group).order_by('-index').first()
    else:
        last_password_manage = PasswordManage.objects.filter(group__isnull=True).order_by('-index').first()
    # Index set 0 if not record in database
    next_index = last_password_manage.index + 1 if last_password_manage else 0
    
    data = {k: v for k, v in request.data.items() if k not in ['user', 'group', 'tag']}
    # Save to database 
    password_manage = PasswordManage.objects.create(user=user, group=group, tag=tag, index=next_index, **data)
    # password_manage.save()
    serializer = self.get_serializer(password_manage)
    return Response(serializer.data, status=status.HTTP_201_CREATED)

  def update(self, request, *args, **kwargs):
    changeGroup = request.data.get('changeGroup')
    group_id = request.data.get('group')
    tag_id = request.data.get('tag')

    # Fetch the object to update
    password_manage = self.get_object()

    tag = PasswordTag.objects.get(id=tag_id) if tag_id else None

    if changeGroup:
      # If group change is requested, re-index the old groups
      
      # Update index of the passwords in the original group
      old_group_passwords = (
        PasswordManage.objects.filter(group=password_manage.group)
        .exclude(id=password_manage.id) 
        if password_manage.group else 
        PasswordManage.objects.filter(group__isnull=True).exclude(id=password_manage.id))
      for i, pm in enumerate(old_group_passwords.order_by('index')):
          pm.index = i
          pm.save()

      # Compute new index as the last index of the destination group + 1
      group = PasswordGroup.objects.get(id=group_id) if group_id else None
      last_password_manage = (
        PasswordManage.objects.filter(group=group).order_by('-index').first() 
        if group else 
        PasswordManage.objects.filter(group__isnull=True).order_by('-index').first()
      )
      new_index = last_password_manage.index + 1 if last_password_manage else 0
      
      # Update the group and index
      password_manage.group = group
      password_manage.index = new_index
    
    # Update the rest of the fields
    password_manage.tag = tag
    data = {k: v for k, v in request.data.items() if k not in ['user', 'group', 'tag', 'changeGroup']}
    for k, v in data.items():
        if hasattr(password_manage, k):
            setattr(password_manage, k, v)

    password_manage.save()

    serializer = self.get_serializer(password_manage)
    return Response(serializer.data)

  def destroy(self, request, *args, **kwargs):
    password_manage = self.get_object()
    # Delete password
    password_manage.delete()

    # Fetch all PasswordManage objects in the same group and sort them by index
    group_id = request.data.get('group', None)
    if group_id:
        passwords_in_same_group = PasswordManage.objects.filter(group=group_id).order_by('index')
    else:
        passwords_in_same_group = PasswordManage.objects.filter(group__isnull=True).order_by('index')

    # Re-assign indices
    for new_index, password in enumerate(passwords_in_same_group):
        password.index = new_index
        password.save()

    return Response(status=status.HTTP_204_NO_CONTENT)

  @action(detail=False, methods=['get'])
  def columns(self):
    serializer = self.get_serializer()
    columns = [field for field in serializer.fields.keys()]
    return Response(columns)

  @action(detail=False, methods=['post'])
  def search(self, request):
    print("requests")
    print(request.data)
    userID = request.data["user_id"]
    passwordFilters = request.data["passwordFilters"]

    queryset = self.get_queryset().filter(user_id=userID).order_by('index')

    # Apply additional filters based on `passwordFilters`
    if passwordFilters and passwordFilters is not None:
        print("move")
        if 'title' in passwordFilters:
            queryset = queryset.filter(title__icontains=passwordFilters['title'])
        if 'tags' in passwordFilters and passwordFilters['tags']:
            queryset = queryset.filter(tag__id__in=passwordFilters['tags'])
        if 'groups' in passwordFilters and passwordFilters['groups']:
            if (-1 in passwordFilters['groups']):
              group_filters = passwordFilters['groups'].copy()
              group_filters.remove(-1)
              queryset = queryset.filter(Q(group__isnull=True) | Q(group__in=group_filters))
            else:
              queryset = queryset.filter(group__in=passwordFilters['groups'])

    serializer = self.get_serializer(queryset, many=True)

    # Get a list of all unique group names from the Group model
    if passwordFilters:  
      if 'groups' in passwordFilters and passwordFilters['groups']:
          group_names = PasswordGroup.objects.filter(user_id=userID, id__in=passwordFilters['groups']).values_list('group_name', flat=True).distinct()
          grouped_data = {group_name: [] for group_name in group_names}
          if (-1 in passwordFilters['groups']):
            grouped_data['other'] = []
      else: 
        group_names = PasswordGroup.objects.filter(user_id=userID).values_list('group_name', flat=True).distinct()
        grouped_data = {group_name: [] for group_name in group_names}
        grouped_data['other'] = []
    else:
        group_names = PasswordGroup.objects.filter(user_id=userID).values_list('group_name', flat=True).distinct()
        grouped_data = {group_name: [] for group_name in group_names}
        grouped_data['other'] = []

    for data in serializer.data:
        groupData = data['group']
        if groupData is None:
            group_key = 'other'
        else:
            group_key = groupData["group_name"]

        if group_key in grouped_data:
            grouped_data[group_key].append(data)

    return Response(grouped_data)

  @action(detail=False, methods=['post'])
  def get_data(self, request):
    userID = request.data["user_id"]
    queryset = self.model.objects.filter(user_id=userID).select_related('group', 'tag').prefetch_related('custom').order_by('index')
    serializer = self.get_serializer(queryset, many=True)
    # Get a list of all unique group names from the Group model
    group_names = PasswordGroup.objects.filter(user_id=userID).values_list('group_name', flat=True).distinct()
    grouped_data = {group_name: [] for group_name in group_names}
    
    grouped_data['other'] = []

    for data in serializer.data:
        groupData = data['group']
        if groupData is None:
            group_key = 'other'
        else:
            group_key = groupData["group_name"]
        
        if group_key in grouped_data:
            grouped_data[group_key].append(data)
        else:
            grouped_data[group_key] = [data]

    return Response(grouped_data)

  @action(detail=False, methods=['patch'])
  def update_indexes(self, request):
    print("move update_indexes")
    passwordsData = request.data.get('new_passwords')
    oldPasswordsData = request.data.get('old_passwords', [])
    oldGroup = request.data.get('old_group')
    newGroup = request.data.get('new_group')
    user = request.data.get('user')
    userId = user["id"]
    print(f"passwordsData: {passwordsData}")
    print(f"oldPasswordsData: {oldPasswordsData}")
    print(f"oldGroup: {oldGroup}")
    print(f"newGroup: {newGroup}")
    print(f"user: {user}")
    print(f"userId: {userId}")
    # get relation data 
    old_group = get_object_or_404(PasswordGroup, group_name=oldGroup ,user=userId) if oldGroup != 'other' else None
    new_group = get_object_or_404(PasswordGroup, group_name=newGroup ,user=userId) if newGroup != 'other' else None
    print(f"old_group: {old_group}")
    print(f"new_group: {new_group}")
    
    if passwordsData:
    # Temporarily set indices to None to avoid uniqueness constraint violation
      for password_data in passwordsData + oldPasswordsData:
          password_id = password_data.get('id')
          if password_id is not None:
              password = PasswordManage.objects.get(pk=password_id)
              password.index = None
              password.save()

      # Set the new indices
      for password_data in passwordsData:
          password_id = password_data.get('id') 
          new_index = password_data.get('index')
          if password_id is not None and new_index is not None:
              password = PasswordManage.objects.get(pk=password_id)
              password.group = new_group
              password.index = new_index
              password.save()

      if oldPasswordsData:
        for password_data in oldPasswordsData:
          password_id = password_data.get('id')
          new_index = password_data.get('index')
          if password_id is not None and new_index is not None:
              password = PasswordManage.objects.get(pk=password_id)
              password.group = old_group
              password.index = new_index
              password.save()

      return Response({"detail": "Password indices updated."}, status=status.HTTP_200_OK)
    else:
      return Response({"detail": "Passwords not provided."}, status=status.HTTP_400_BAD_REQUEST)


class PasswordGroupViewSet(viewsets.ModelViewSet):
  serializer_class = PasswordGroupSerializer
  queryset = PasswordGroup.objects.all()
  # permission_classes = [IsAuthenticated]
  permission_classes = (AllowAny,)
  model = PasswordGroup
  
  @action(detail=False, methods=['post'])
  def get_data(self, request):
    userID = request.data["user_id"]
    queryset = self.get_queryset().filter(user_id=userID).values('id', 'group_name')
    return Response(list(queryset))

class PasswordTagViewSet(viewsets.ModelViewSet):
  serializer_class = PasswordTagSerializer
  queryset = PasswordTag.objects.all()
  permission_classes = (AllowAny,)
  model = PasswordTag
  
  @action(detail=False, methods=['post'])
  def get_data(self, request):
    userID = request.data["user_id"]
    queryset = self.get_queryset().filter(user_id=userID).values('id', 'tag_name')
    return Response(list(queryset))

class PasswordManageView(generics.ListCreateAPIView):
  queryset = PasswordManage.objects.all()
  serializer_class = PasswordManageSerializer
  permission_classes = (AllowAny,)


class InquiryViewSet(viewsets.ModelViewSet):
  serializer_class = InquirySerializer
  queryset = Inquiry.objects.all()
  model = Inquiry
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

  
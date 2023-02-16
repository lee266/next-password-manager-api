from django.urls import path
from django.conf.urls import include
from rest_framework import routers
from app.api import views

router = routers.DefaultRouter()
router.register(r'users', views.UserViewSet, basename="users")
# router.register(r'passwords', views.PasswordManageView, basename="passwords")
router.register(r'tasks', views.TaskViewSet, basename="tasks")
router.register(r'calendars', views.CalendarViewSet, basename="calendars")


urlpatterns = [
    path('', include(router.urls)),
    path('user/', views.UserView.as_view(), name='User'),
    path('message/', views.MessageView.as_view(), name='message'),
    path('password/', views.PasswordManageView.as_view(), name="password"),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.jwt')),
    path('snippets/', views.task_list),
    path(r'test', views.TestAppView.as_view()),
]

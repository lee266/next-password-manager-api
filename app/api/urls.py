from django.urls import path
from django.conf.urls import include
from rest_framework import routers
from app.api import views
# from djoser.views import PasswordResetView, PasswordResetConfirmView

router = routers.DefaultRouter()
router.register(r'users', views.UserViewSet, basename="users")
router.register(r'passwords', views.PasswordManageViewSet, basename="passwords")
router.register(r'groups', views.PasswordGroupViewSet, basename="groups")
router.register(r'tags', views.PasswordTagViewSet, basename="tags")
router.register(r'tasks', views.TaskViewSet, basename="tasks")
router.register(r'calendars', views.CalendarViewSet, basename="calendars")
router.register(r'inquiry', views.InquiryViewSet, basename="inquiries")

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

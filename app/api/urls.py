from django.urls import path
from app.api import views

urlpatterns = [
    path('user/', views.UserView.as_view(), name='User'),
    path('message/', views.MessageView.as_view(), name='message'),
]

from django.contrib import admin
from .models import User, Message, PasswordManage, Calendar

# Register your models here.
admin.site.register(User)
admin.site.register(Message)
admin.site.register(PasswordManage)
admin.site.register(Calendar)


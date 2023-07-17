from django.db import models
from django.core.mail import send_mail
from django.contrib.auth.models import PermissionsMixin, UserManager
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError


"""_summary_
  Naming convention:
      class: UpperCamelCase
      field: snakeCase

  Returns:
      _type_: _description_
"""
class UserManager(BaseUserManager):
  use_in_migrations = True
  
  def _create_user(self, username, email, password, **extra_fields):
    if not email:
      raise ValueError('The given email must be set')
    
    email = self.normalize_email(email)
    username = self.model.normalize_username(username)
    user = self.model(username=username, email=email, **extra_fields)
    user.set_password(password)
    user.save(using=self.db)
    return user
  
  def create_user(self, username, email, password, **extra_fields):
    extra_fields.setdefault('is_staff', False)
    extra_fields.setdefault('is_superuser', False)
    return self._create_user(username=username,email=email, password=password, **extra_fields)

  def create_superuser(self, username, email, password, **extra_fields):
    extra_fields.setdefault('is_staff', True)
    extra_fields.setdefault('is_superuser', True)
    if extra_fields.get('is_staff') is not True:
        raise ValueError('is_staff=Trueである必要があります。')
    if extra_fields.get('is_superuser') is not True:
        raise ValueError('is_superuser=Trueである必要があります。')
    return self._create_user(username, email, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
  # check invalid text
  username_validator = UnicodeUsernameValidator()
  
  username = models.CharField(
    _("username"), max_length=255, 
    validators=[username_validator],
  )
  email = models.EmailField(
    _("email"), unique=True,
    error_messages={
      "unique": "このメールアドレスは既に使用されています。",
    })
  password = models.CharField(max_length=255)
  is_staff = models.BooleanField(_('staff status'), default=False,)
  is_active = models.BooleanField(default=True)
  created_at = models.DateField(auto_now_add=True)
  
  objects = UserManager()
  
  EMAIL_FIELD = "email"
  USERNAME_FIELD = "email"
  REQUIRED_FIELDS = ["username"]
  
  class Meta:
    verbose_name = _("user")
    verbose_name_plural = _("users")
  
  def clean(self):
    super().clean()
    self.email = self.__class__.objects.normalize_email(self.email)
  
  def email_user(self, subject, message, from_email=None, **kwargs):
    send_mail(subject, message, from_email, [self.email], **kwargs)

class Message(models.Model):
  user = models.ForeignKey(User, on_delete=models.CASCADE)
  Message = models.TextField(max_length=10000)
  created_at = models.DateTimeField(auto_now_add=True)
  
  def __str__(self):
    return self.Message

class PasswordGroup(models.Model):
  user = models.ForeignKey(User, on_delete=models.CASCADE)
  group_name = models.CharField(max_length=255)
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)
  
  class Meta :
    constraints = [
      models.UniqueConstraint(
        fields=["user", "group_name"],
        name="group_unique"
      )
    ]
  
  # Do not input other 
  # def clean(self):
  #   if self.group_name.lower() == "other":
  #     raise ValidationError("group_name cannot be 'other'")
  
  def __str__(self):
    return self.group_name


class PasswordTag(models.Model):
  user = models.ForeignKey(User, on_delete=models.CASCADE)
  tag_name = models.CharField(max_length=255)
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)

  class Meta :
    constraints = [
      models.UniqueConstraint(
        fields=["user", "tag_name"],
        name="tag_unique"
      )
    ]

  def __str__(self):
    return self.tag_name

class PasswordCustomField(models.Model):
  custom_name = models.TextField(max_length=255)
  custom_value = models.TextField(max_length=255)
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)
  
  def __str__(self):
    return self.custom_name

class PasswordManage(models.Model):
  user = models.ForeignKey(User, on_delete=models.CASCADE)
  title = models.CharField(max_length=255, blank=True)
  password = models.TextField()
  email = models.EmailField(blank=True, null=True)
  website = models.URLField(blank=True)
  notes = models.TextField(blank=True)
  index = models.PositiveIntegerField(null=True)
  tag = models.ForeignKey(PasswordTag, null=True, on_delete=models.SET_NULL)
  group = models.ForeignKey(PasswordGroup, null=True, on_delete=models.CASCADE)
  custom = models.ManyToManyField(PasswordCustomField, blank=True)
  created_at = models.DateTimeField(auto_now_add=True)
  
  class Meta :
    constraints = [
      models.UniqueConstraint(
        fields=["user", "group_id", "index"],
        name="index_unique"
      )
    ]
  
  def __str__(self):
    return self.title


class Task(models.Model):
  user = models.ForeignKey(User, on_delete=models.CASCADE)
  task = models.TextField(max_length=255)
  created_at = models.DateTimeField(auto_now_add=True)
  
  def __str__(self):
    return self.task

class Calendar(models.Model):
  title = models.TextField(max_length=2000)
  user = models.ForeignKey(User, on_delete=models.CASCADE)
  start = models.DateTimeField()
  end = models.DateTimeField()
  all_day = models.BooleanField(default=False)
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)
  
  def __str__(self):
    return self.title